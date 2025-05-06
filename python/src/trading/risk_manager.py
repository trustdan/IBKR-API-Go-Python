from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
import math

from ..utils.logger import log_debug, log_info, log_warning, log_error
from ..models.option import OptionSpread
from ..app.config import Config


class RiskManager:
    """Manages risk parameters and position sizing for trades."""
    
    def __init__(self, config: Config, broker_api=None):
        """Initialize the risk manager.
        
        Args:
            config: Configuration parameters
            broker_api: IBKR API client (optional)
        """
        self.config = config
        self.broker_api = broker_api
        self.daily_trades = {}  # Track trades by date
        self.active_positions = {}  # Track current positions
        
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
        
        log_debug(f"Position sizing: Account value ${account_value:.2f}, "
                f"Risk amount ${max_risk_amount:.2f}, "
                f"Spread cost ${spread_cost:.2f}, "
                f"Contracts: {contracts}")
                
        return contracts
        
    def can_enter_trade(self, symbol: str, direction: str) -> Tuple[bool, str]:
        """Check if a new trade can be entered based on risk limits.
        
        Args:
            symbol: Symbol to trade
            direction: Trade direction ("LONG" or "SHORT")
            
        Returns:
            Tuple of (can_enter, reason)
        """
        # Check if we have reached the maximum daily trades limit
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")
        
        if today_str not in self.daily_trades:
            self.daily_trades[today_str] = []
            
        if len(self.daily_trades[today_str]) >= self.config.MAX_DAILY_TRADES:
            return False, f"Maximum daily trades limit ({self.config.MAX_DAILY_TRADES}) reached"
            
        # Check if we have reached the maximum positions limit
        if len(self.active_positions) >= self.config.MAX_POSITIONS:
            return False, f"Maximum positions limit ({self.config.MAX_POSITIONS}) reached"
            
        # Check if we already have a position in this symbol
        if symbol in self.active_positions:
            existing_direction = self.active_positions[symbol]['direction']
            if existing_direction == direction:
                return False, f"Already have a {direction} position in {symbol}"
            # Could allow opposite direction trades as a form of scaling out/hedging
            # else:
            #    return True, "Opposite direction trade allowed"
            
        # Get account value from broker if available
        account_value = None
        if self.broker_api:
            account_summary = self.broker_api.get_account_summary()
            account_value = account_summary.get('net_liquidation', 0)
            
            # Check if we have enough buying power
            if account_summary.get('available_funds', 0) < 5000:  # Arbitrary minimum
                return False, "Insufficient buying power"
                
        return True, "Trade allowed"
        
    def record_trade(self, symbol: str, direction: str, contracts: int, spread: OptionSpread) -> None:
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
            
        self.daily_trades[today_str].append({
            'symbol': symbol,
            'direction': direction,
            'contracts': contracts,
            'spread_type': spread.spread_type,
            'expiration': spread.expiration,
            'cost': spread.cost,
            'timestamp': datetime.now()
        })
        
        # Record active position
        self.active_positions[symbol] = {
            'direction': direction,
            'contracts': contracts,
            'spread': spread,
            'entry_date': today,
            'entry_price': spread.cost  # Per contract
        }
        
        log_info(f"Recorded new trade: {symbol} {direction} x{contracts} contracts, "
               f"Daily trades: {len(self.daily_trades[today_str])}/{self.config.MAX_DAILY_TRADES}, "
               f"Active positions: {len(self.active_positions)}/{self.config.MAX_POSITIONS}")
        
    def close_position(self, symbol: str) -> None:
        """Record the closing of a position.
        
        Args:
            symbol: Symbol of the closed position
        """
        if symbol in self.active_positions:
            position = self.active_positions.pop(symbol)
            log_info(f"Closed position: {symbol} {position['direction']} x{position['contracts']} contracts, "
                   f"Active positions: {len(self.active_positions)}/{self.config.MAX_POSITIONS}")
                   
    def update_positions_from_broker(self) -> None:
        """Update active positions from broker data.
        
        This should be called periodically to ensure position data is accurate.
        """
        if not self.broker_api:
            return
            
        try:
            # Get current positions from broker
            broker_positions = self.broker_api.get_positions()
            
            # Update our active positions based on broker data
            for symbol, position in broker_positions.items():
                if position['quantity'] == 0:
                    # Position is closed
                    if symbol in self.active_positions:
                        self.active_positions.pop(symbol)
                else:
                    # Position exists but we don't have it tracked
                    if symbol not in self.active_positions:
                        log_warning(f"Found untracked position in {symbol}")
                        
            # Check for positions we think are active but broker doesn't have
            for symbol in list(self.active_positions.keys()):
                if symbol not in broker_positions:
                    log_warning(f"Position in {symbol} not found in broker data, removing from active positions")
                    self.active_positions.pop(symbol)
                    
        except Exception as e:
            log_error(f"Error updating positions from broker: {str(e)}")
            
    def get_account_value(self) -> float:
        """Get the current account value.
        
        Returns:
            Account value or default value if broker not available
        """
        if self.broker_api:
            try:
                account_summary = self.broker_api.get_account_summary()
                return account_summary.get('net_liquidation', 100000.0)
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
        stop_factor = 0.5  # 50% loss as default
        
        # Calculate stop price
        stop_price = option_spread.cost * (1 - stop_factor)
        
        # Ensure minimum value (spreads can't go below $0)
        stop_price = max(stop_price, 0.05)
        
        return stop_price
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get risk management metrics.
        
        Returns:
            Dictionary of risk metrics
        """
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")
        
        return {
            "daily_trades": len(self.daily_trades.get(today_str, [])),
            "max_daily_trades": self.config.MAX_DAILY_TRADES,
            "active_positions": len(self.active_positions),
            "max_positions": self.config.MAX_POSITIONS,
            "remaining_trades_today": max(0, self.config.MAX_DAILY_TRADES - len(self.daily_trades.get(today_str, []))),
            "remaining_positions": max(0, self.config.MAX_POSITIONS - len(self.active_positions))
        } 