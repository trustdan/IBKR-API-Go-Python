import math
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, DefaultDict, Dict, List, Optional, Tuple, Set

from src.app.config import Config
from src.models.option import OptionSpread
from src.utils.alert_system import AlertSystem
from src.utils.logger import log_debug, log_error, log_info, log_warning


class RiskManager:
    """Manages risk parameters and position sizing for trades."""

    def __init__(
        self,
        config: Config,
        broker_api=None,
        alert_system: Optional[AlertSystem] = None,
    ):
        """Initialize the risk manager.

        Args:
            config: Configuration parameters
            broker_api: IBKR API client (optional)
            alert_system: Alert system for notifications (optional)
        """
        self.config = config
        self.broker_api = broker_api
        self.alert_system = alert_system
        self.daily_trades: Dict[str, List[Dict[str, Any]]] = {}  # Track trades by date
        self.active_positions: Dict[str, Dict[str, Any]] = {}  # Track current positions
        self.sector_exposure: DefaultDict[str, float] = defaultdict(
            float
        )  # Track exposure by sector
        self.industry_exposure: DefaultDict[str, float] = defaultdict(
            float
        )  # Track exposure by industry

        # Initialize risk tracking
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.banned_symbols: Set[str] = set()
        self.daily_pnl = 0.0
        self.trade_count = 0
        self.max_positions = getattr(config, "MAX_POSITIONS", 5)
        self.max_position_size = getattr(config, "MAX_POSITION_SIZE", 10000.0)
        self.max_daily_loss = getattr(config, "MAX_DAILY_LOSS", -2000.0)
        
        # Last time positions were updated
        self.last_position_update = datetime.now() - timedelta(hours=1)

    def calculate_position_size(self, account_value: float, spread_cost: float) -> int:
        """Calculate position size based on risk parameters.

        Args:
            account_value: Current account value
            spread_cost: Cost of the option spread per contract

        Returns:
            Number of contracts to trade
        """
        # Calculate risk amount based on risk percentage
        max_risk_amount = account_value * self.config.RISK_PER_TRADE

        # Calculate number of contracts
        if spread_cost > 0:  # Prevent division by zero
            # Each contract is 100 shares, so multiply spread cost by 100
            contracts = math.floor(max_risk_amount / (spread_cost))
        else:
            contracts = 0

        # Apply maximum contracts limit
        contracts = min(contracts, self.config.MAX_CONTRACTS_PER_TRADE)

        # Ensure at least 1 contract (if any)
        contracts = max(contracts, 1) if contracts > 0 else 0

        log_debug(
            f"Position sizing: Account value ${account_value:.2f}, "
            f"Risk amount ${max_risk_amount:.2f}, "
            f"Spread cost ${spread_cost:.2f}, "
            f"Contracts: {contracts}"
        )

        return contracts

    def can_enter_trade(
        self, symbol: str, direction: str, cost_per_contract: float = 0.0
    ) -> Tuple[bool, str]:
        """Check if a new trade can be entered based on risk limits.

        Args:
            symbol: Symbol to trade
            direction: Trade direction ("LONG" or "SHORT")
            cost_per_contract: Cost per contract (optional)

        Returns:
            Tuple of (can_enter, reason)
        """
        # Check if we have reached the maximum daily trades limit
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")

        if today_str not in self.daily_trades:
            self.daily_trades[today_str] = []

        if len(self.daily_trades[today_str]) >= self.config.MAX_DAILY_TRADES:
            return (
                False,
                f"Maximum daily trades limit ({self.config.MAX_DAILY_TRADES}) reached",
            )

        # Check if we have reached the maximum positions limit
        if len(self.active_positions) >= self.config.MAX_POSITIONS:
            return (
                False,
                f"Maximum positions limit ({self.config.MAX_POSITIONS}) reached",
            )

        # Check if we already have a position in this symbol
        if symbol in self.active_positions:
            existing_direction = self.active_positions[symbol]["direction"]
            if existing_direction == direction:
                return False, f"Already have a {direction} position in {symbol}"

        # Get account value and check portfolio level risk
        account_value = self.get_account_value()

        # Check portfolio heat (percentage of account at risk)
        portfolio_heat = self.calculate_portfolio_heat()
        if portfolio_heat >= self.config.MAX_PORTFOLIO_HEAT:
            msg = f"Maximum portfolio heat reached: {portfolio_heat:.1f}% >= {self.config.MAX_PORTFOLIO_HEAT}%"
            if self.alert_system:
                self.alert_system.send_risk_alert("Portfolio Heat Limit", msg)
            return False, msg

        # Get sector and industry for this symbol
        sector, industry = self.get_sector_industry(symbol)

        # Check sector exposure limits
        if sector:
            sector_exposure = self.sector_exposure.get(sector, 0)
            if (
                sector_exposure + cost_per_contract
                > account_value * self.config.MAX_SECTOR_EXPOSURE
            ):
                msg = f"Sector exposure limit reached for {sector}"
                if self.alert_system:
                    self.alert_system.send_risk_alert("Sector Exposure Limit", msg)
                return False, msg

        # Check industry exposure limits
        if industry:
            industry_exposure = self.industry_exposure.get(industry, 0)
            if (
                industry_exposure + cost_per_contract
                > account_value * self.config.MAX_INDUSTRY_EXPOSURE
            ):
                msg = f"Industry exposure limit reached for {industry}"
                if self.alert_system:
                    self.alert_system.send_risk_alert("Industry Exposure Limit", msg)
                return False, msg

        # Check directional bias limits
        long_exposure, short_exposure = self.calculate_directional_exposure()
        if direction == "LONG" and long_exposure > self.config.MAX_DIRECTIONAL_BIAS * (
            long_exposure + short_exposure
        ):
            msg = f"Maximum long exposure bias reached: {long_exposure:.1f}%"
            if self.alert_system:
                self.alert_system.send_risk_alert("Directional Bias Limit", msg)
            return False, msg
        elif (
            direction == "SHORT"
            and short_exposure
            > self.config.MAX_DIRECTIONAL_BIAS * (long_exposure + short_exposure)
        ):
            msg = f"Maximum short exposure bias reached: {short_exposure:.1f}%"
            if self.alert_system:
                self.alert_system.send_risk_alert("Directional Bias Limit", msg)
            return False, msg

        # Get account value from broker if available
        if self.broker_api:
            account_summary = self.broker_api.get_account_summary()

            # Check if we have enough buying power
            if account_summary.get("available_funds", 0) < self.config.MIN_BUYING_POWER:
                msg = f"Insufficient buying power: ${account_summary.get('available_funds', 0):.2f} < ${self.config.MIN_BUYING_POWER:.2f}"
                if self.alert_system:
                    self.alert_system.send_risk_alert("Insufficient Buying Power", msg)
                return False, msg

        return True, "Trade allowed"

    def record_trade(
        self, symbol: str, direction: str, contracts: int, spread: OptionSpread
    ) -> None:
        """Record a newly executed trade.

        Args:
            symbol: Traded symbol
            direction: Trade direction
            contracts: Number of contracts
            spread: Option spread used
        """
        # Record daily trade
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")

        if today_str not in self.daily_trades:
            self.daily_trades[today_str] = []

        self.daily_trades[today_str].append(
            {
                "symbol": symbol,
                "direction": direction,
                "contracts": contracts,
                "spread_type": spread.spread_type,
                "expiration": spread.expiration,
                "cost": spread.cost,
                "timestamp": datetime.now(),
            }
        )

        # Record active position
        self.active_positions[symbol] = {
            "direction": direction,
            "contracts": contracts,
            "spread": spread,
            "entry_date": today,
            "entry_price": spread.cost,  # Per contract
            "stop_price": self.calculate_stop_price(spread),
            "target_price": self.calculate_target_price(spread, direction),
        }

        # Update sector and industry exposure
        sector, industry = self.get_sector_industry(symbol)
        total_cost = spread.cost * contracts * 100  # Total position cost

        if sector:
            self.sector_exposure[sector] += total_cost

        if industry:
            self.industry_exposure[industry] += total_cost

        log_info(
            f"Recorded new trade: {symbol} {direction} x{contracts} contracts, "
            f"Daily trades: {len(self.daily_trades[today_str])}/{self.config.MAX_DAILY_TRADES}, "
            f"Active positions: {len(self.active_positions)}/{self.config.MAX_POSITIONS}"
        )

    def close_position(self, symbol: str) -> None:
        """Record the closing of a position.

        Args:
            symbol: Symbol of the closed position
        """
        if symbol in self.active_positions:
            position = self.active_positions.pop(symbol)

            # Update sector and industry exposure
            sector, industry = self.get_sector_industry(symbol)
            total_cost = position["spread"].cost * position["contracts"] * 100

            if sector:
                self.sector_exposure[sector] -= total_cost
                if self.sector_exposure[sector] <= 0:
                    del self.sector_exposure[sector]

            if industry:
                self.industry_exposure[industry] -= total_cost
                if self.industry_exposure[industry] <= 0:
                    del self.industry_exposure[industry]

            log_info(
                f"Closed position: {symbol} {position['direction']} x{position['contracts']} contracts, "
                f"Active positions: {len(self.active_positions)}/{self.config.MAX_POSITIONS}"
            )

    def update_positions_from_broker(self) -> None:
        """Update positions from broker API."""
        # Only update positions every 30 seconds
        now = datetime.now()
        if (now - self.last_position_update).total_seconds() < 30:
            return
            
        # Get positions from broker if API supports it
        if hasattr(self.broker_api, 'get_positions'):
            try:
                positions = self.broker_api.get_positions()
                if positions:
                    self.positions = positions
                    self.last_position_update = now
                    
                    # Update daily P&L
                    realized_pnl = 0.0
                    for position in self.positions.values():
                        if "realized_pnl" in position:
                            realized_pnl += position.get("realized_pnl", 0.0)
                    
                    self.daily_pnl = realized_pnl
                    
                    # Log updated positions
                    position_summary = ", ".join([
                        f"{symbol}: {pos['quantity']} @ ${pos['avg_price']:.2f}"
                        for symbol, pos in self.positions.items()
                    ])
                    log_debug(f"Updated positions: {position_summary}")
            except Exception as e:
                log_error(f"Error updating positions from broker: {str(e)}")
    
    def can_trade_symbol(self, symbol: str) -> bool:
        """Check if we can trade a symbol based on risk rules.
        
        Args:
            symbol: Symbol to check
            
        Returns:
            True if symbol can be traded
        """
        # Check if symbol is banned
        if symbol in self.banned_symbols:
            log_warning(f"Symbol {symbol} is banned from trading")
            return False
            
        # Check if we have too many positions
        if len(self.positions) >= self.max_positions and symbol not in self.positions:
            log_warning(f"Maximum positions reached ({self.max_positions}), can't open new position for {symbol}")
            return False
            
        # Check if daily loss limit has been reached
        if self.daily_pnl < self.max_daily_loss:
            log_warning(f"Daily loss limit reached (${self.daily_pnl:.2f}), stopping trading")
            return False
            
        # All checks passed
        return True
        
    def calculate_position_size(self, symbol: str, price: float) -> int:
        """Calculate the appropriate position size for a trade.
        
        Args:
            symbol: Symbol to trade
            price: Current price
            
        Returns:
            Number of shares/contracts to trade
        """
        # Get account value or use default
        account_value = 100000.0  # Default
        
        # If broker API supports getting account summary, use that
        if hasattr(self.broker_api, 'get_account_summary'):
            try:
                account_summary = self.broker_api.get_account_summary()
                if account_summary and "net_liquidation" in account_summary:
                    account_value = account_summary["net_liquidation"]
            except Exception as e:
                log_warning(f"Could not get account value: {str(e)}")
        
        # Calculate max position size as percentage of account
        risk_per_trade = getattr(self.config, "RISK_PER_TRADE", 0.02)  # Default 2%
        max_risk = account_value * risk_per_trade
        
        # Calculate position size based on price
        position_size = int(max_risk / price)
        
        # Limit to max position size
        if position_size * price > self.max_position_size:
            position_size = int(self.max_position_size / price)
            
        return max(1, position_size)  # Ensure minimum of 1

    def get_account_value(self) -> float:
        """Get the current account value.

        Returns:
            Account value or default value if broker not available
        """
        if self.broker_api:
            try:
                account_summary = self.broker_api.get_account_summary()
                return account_summary.get("net_liquidation", 100000.0)
            except Exception as e:
                log_error(f"Error getting account value: {str(e)}")

        # Default value if broker not available
        return 100000.0

    def calculate_stop_price(self, option_spread: OptionSpread) -> float:
        """Calculate stop loss price for an option spread.

        Args:
            option_spread: The option spread

        Returns:
            Stop loss price
        """
        # For a vertical spread, the stop is typically based on a percentage of the spread's cost
        # or a maximum dollar loss amount
        stop_percentage = getattr(
            self.config, "STOP_LOSS_PERCENTAGE", 0.5
        )  # Default to 50% loss

        # Calculate stop price
        stop_price = option_spread.cost * (1 - stop_percentage)

        # Ensure minimum value (spreads can't go below $0)
        stop_price = max(stop_price, 0.05)

        return stop_price

    def calculate_target_price(
        self, option_spread: OptionSpread, direction: str
    ) -> float:
        """Calculate profit target price for an option spread.

        Args:
            option_spread: The option spread
            direction: Trade direction

        Returns:
            Target price
        """
        # Get reward-to-risk ratio from config
        target_reward_risk = getattr(self.config, "TARGET_REWARD_RISK", 1.5)

        # Calculate the max possible value of the spread
        if direction == "LONG":
            # For bull call spread: width of strikes - cost
            if option_spread.spread_type == "BULL_CALL":
                max_profit = (
                    option_spread.short_leg.strike - option_spread.long_leg.strike
                ) - option_spread.cost
            # For bear put spread: width of strikes - cost
            else:  # Bear put
                max_profit = (
                    option_spread.long_leg.strike - option_spread.short_leg.strike
                ) - option_spread.cost
        else:  # SHORT
            # For bear call spread: premium received (cost)
            if option_spread.spread_type == "BEAR_CALL":
                max_profit = option_spread.cost
            # For bull put spread: premium received (cost)
            else:  # Bull put
                max_profit = option_spread.cost

        # Calculate risk (max loss)
        risk = option_spread.cost  # For long positions, risk is the cost

        # Target price based on reward-to-risk ratio
        # For a 1.5:1 reward:risk ratio, we'd aim for 1.5 * risk as profit
        target_profit = min(max_profit, risk * target_reward_risk)

        # Calculate target price
        if direction == "LONG":
            target_price = option_spread.cost + target_profit
        else:  # SHORT
            target_price = option_spread.cost - target_profit
            target_price = max(target_price, 0.05)  # Ensure minimum value

        return target_price

    def should_exit_position(
        self, symbol: str, current_price: float
    ) -> Tuple[bool, str]:
        """Determine if a position should be exited based on current price.

        Args:
            symbol: Symbol of the position
            current_price: Current price of the position

        Returns:
            Tuple of (should_exit, reason)
        """
        if symbol not in self.active_positions:
            return False, "Position not found"

        position = self.active_positions[symbol]
        direction = position["direction"]

        # Check stop loss
        if direction == "LONG" and current_price <= position["stop_price"]:
            return True, "Stop loss triggered"
        elif direction == "SHORT" and current_price >= position["stop_price"]:
            return True, "Stop loss triggered"

        # Check profit target
        if direction == "LONG" and current_price >= position["target_price"]:
            return True, "Profit target reached"
        elif direction == "SHORT" and current_price <= position["target_price"]:
            return True, "Profit target reached"

        # Check time-based exit (option expiration approach)
        days_to_expiry = (position["spread"].expiration - datetime.now().date()).days
        if days_to_expiry <= self.config.MIN_DAYS_TO_EXPIRY:
            return True, f"Position close to expiry ({days_to_expiry} days)"

        # Check R-multiple exit (if price moved in favorable direction)
        if self.config.USE_R_MULTIPLE_EXIT:
            entry_price = position["entry_price"]
            stop_price = position["stop_price"]
            r_value = abs(entry_price - stop_price)  # 1R

            if direction == "LONG" and current_price >= entry_price + (
                r_value * self.config.R_MULTIPLE_TARGET
            ):
                return (
                    True,
                    f"R-multiple target reached ({self.config.R_MULTIPLE_TARGET}R)",
                )
            elif direction == "SHORT" and current_price <= entry_price - (
                r_value * self.config.R_MULTIPLE_TARGET
            ):
                return (
                    True,
                    f"R-multiple target reached ({self.config.R_MULTIPLE_TARGET}R)",
                )

        return False, "No exit criteria met"

    def calculate_portfolio_heat(self) -> float:
        """Calculate current portfolio heat (percentage of account at risk).

        Returns:
            Portfolio heat percentage
        """
        account_value = self.get_account_value()
        total_risk = 0.0

        for symbol, position in self.active_positions.items():
            position_cost = position["entry_price"] * position["contracts"] * 100
            position_risk = position_cost * self.config.RISK_PER_TRADE
            total_risk += position_risk

        portfolio_heat = (total_risk / account_value) * 100 if account_value > 0 else 0
        return portfolio_heat

    def calculate_directional_exposure(self) -> Tuple[float, float]:
        """Calculate long and short exposure percentages.

        Returns:
            Tuple of (long_exposure_percent, short_exposure_percent)
        """
        long_exposure = 0.0
        short_exposure = 0.0

        for symbol, position in self.active_positions.items():
            position_cost = position["entry_price"] * position["contracts"] * 100

            if position["direction"] == "LONG":
                long_exposure += position_cost
            else:  # SHORT
                short_exposure += position_cost

        total_exposure = long_exposure + short_exposure

        if total_exposure > 0:
            long_percent = (long_exposure / total_exposure) * 100
            short_percent = (short_exposure / total_exposure) * 100
        else:
            long_percent = 0
            short_percent = 0

        return long_percent, short_percent

    def get_sector_industry(self, symbol: str) -> Tuple[Optional[str], Optional[str]]:
        """Get sector and industry for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Tuple of (sector, industry)
        """
        # This would typically use an external data source or API
        # For now, return placeholder values
        if self.broker_api:
            try:
                sector_data = self.broker_api.get_symbol_fundamentals(symbol)
                return sector_data.get("sector"), sector_data.get("industry")
            except Exception as e:
                log_error(f"Error getting sector/industry data: {str(e)}")

        return None, None

    def get_metrics(self) -> Dict[str, Any]:
        """Get risk management metrics.

        Returns:
            Dictionary of risk metrics
        """
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")

        # Calculate portfolio metrics
        portfolio_heat = self.calculate_portfolio_heat()
        long_exposure, short_exposure = self.calculate_directional_exposure()

        return {
            "daily_trades": len(self.daily_trades.get(today_str, [])),
            "max_daily_trades": self.config.MAX_DAILY_TRADES,
            "active_positions": len(self.active_positions),
            "max_positions": self.config.MAX_POSITIONS,
            "remaining_trades_today": max(
                0,
                self.config.MAX_DAILY_TRADES
                - len(self.daily_trades.get(today_str, [])),
            ),
            "remaining_positions": max(
                0, self.config.MAX_POSITIONS - len(self.active_positions)
            ),
            "portfolio_heat": portfolio_heat,
            "long_exposure": long_exposure,
            "short_exposure": short_exposure,
            "sector_exposure": dict(self.sector_exposure),
            "industry_exposure": dict(self.industry_exposure),
        }
