from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from src.app.config import Config
from src.models.option import Option, OptionSpread
from src.utils.logger import log_debug, log_error, log_info, log_warning


class OptionSelector:
    """Selects optimal vertical spreads based on configured criteria."""

    def __init__(self, config: Config):
        """Initialize the option selector.

        Args:
            config: Configuration parameters
        """
        self.config = config

    def select_vertical_spread(
        self, symbol: str, direction: str, current_price: float
    ) -> Optional[OptionSpread]:
        """Select the optimal vertical spread for a trade signal.

        Args:
            symbol: The underlying symbol
            direction: Trade direction ("LONG" or "SHORT")
            current_price: Current price of the underlying

        Returns:
            The selected option spread or None if no suitable spread found
        """
        try:
            # Fetch available options
            options_chain = self.fetch_options_chain(symbol)
            if not options_chain:
                log_warning(f"No options available for {symbol}")
                return None

            # Filter by expiration (prefer 30-45 DTE)
            valid_expirations = self.filter_by_dte(options_chain)
            if not valid_expirations:
                log_warning(f"No options with valid expiration for {symbol}")
                return None

            # Create spreads based on direction
            if direction == "LONG":
                # For bullish trades, find call verticals
                spreads = self.create_call_vertical_spreads(
                    valid_expirations, current_price
                )
            else:
                # For bearish trades, find put verticals
                spreads = self.create_put_vertical_spreads(
                    valid_expirations, current_price
                )

            if not spreads:
                log_warning(f"No valid spreads created for {symbol} {direction}")
                return None

            # Filter by criteria
            filtered_spreads = self.filter_spreads(spreads)
            if not filtered_spreads:
                log_warning(f"No spreads matching criteria for {symbol} {direction}")
                return None

            # Rank by reward-to-risk ratio
            ranked_spreads = self.rank_by_reward_risk(filtered_spreads)

            selected_spread = ranked_spreads[0] if ranked_spreads else None
            if selected_spread:
                log_info(f"Selected spread for {symbol} {direction}: {selected_spread}")

            return selected_spread
        except Exception as e:
            log_error(f"Error selecting spread for {symbol}: {str(e)}")
            return None

    def fetch_options_chain(self, symbol: str) -> List[Option]:
        """Fetch options chain for a symbol.

        In a real implementation, this would call a data provider API.
        For now, we'll implement a placeholder with stub data.

        Args:
            symbol: Symbol to fetch options for

        Returns:
            List of available options
        """
        # TODO: Implement real options chain retrieval from broker API
        # This is a stub implementation for development
        log_debug(f"Fetching options chain for {symbol}")

        # In a real implementation, we would fetch from IBKR API
        # For now, create some synthetic options as a placeholder
        today = datetime.now().date()
        expiration_dates = [
            today + timedelta(days=30),
            today + timedelta(days=45),
            today + timedelta(days=60),
        ]

        # Create synthetic ATM options for development purposes
        atm_strikes = [95.0, 100.0, 105.0, 110.0]  # Assuming stock around $100

        options = []
        for exp in expiration_dates:
            for strike in atm_strikes:
                # Create call option
                call = Option(
                    symbol=f"{symbol}{exp.strftime('%y%m%d')}C{int(strike*100):08d}",
                    underlying=symbol,
                    option_type="call",
                    strike=strike,
                    expiration=exp,
                    bid=max(0.1, (100 - strike) + 3),
                    ask=max(0.15, (100 - strike) + 3.5),
                    last=max(0.125, (100 - strike) + 3.25),
                    volume=100,
                    open_interest=1000,
                    implied_volatility=0.3,
                    delta=max(
                        0.01, min(0.99, 0.5 + (100 - strike) * 0.04)
                    ),  # Synthetic delta
                    gamma=0.02,
                    theta=-0.01,
                    vega=0.1,
                    rho=0.01,
                )
                options.append(call)

                # Create put option
                put = Option(
                    symbol=f"{symbol}{exp.strftime('%y%m%d')}P{int(strike*100):08d}",
                    underlying=symbol,
                    option_type="put",
                    strike=strike,
                    expiration=exp,
                    bid=max(0.1, (strike - 100) + 3),
                    ask=max(0.15, (strike - 100) + 3.5),
                    last=max(0.125, (strike - 100) + 3.25),
                    volume=100,
                    open_interest=1000,
                    implied_volatility=0.3,
                    delta=min(
                        -0.01, max(-0.99, -0.5 - (strike - 100) * 0.04)
                    ),  # Synthetic delta
                    gamma=0.02,
                    theta=-0.01,
                    vega=0.1,
                    rho=0.01,
                )
                options.append(put)

        return options

    def filter_by_dte(self, options_chain: List[Option]) -> Dict[date, List[Option]]:
        """Filter options by preferred days to expiration.

        Args:
            options_chain: Full list of options

        Returns:
            Dictionary mapping expiration dates to option lists
        """
        filtered = {}
        today = datetime.now().date()

        for option in options_chain:
            dte = (option.expiration - today).days
            if self.config.MIN_DTE <= dte <= self.config.MAX_DTE:
                if option.expiration not in filtered:
                    filtered[option.expiration] = []
                filtered[option.expiration].append(option)

        return filtered

    def filter_spreads(self, spreads: List[OptionSpread]) -> List[OptionSpread]:
        """Filter spreads by configured criteria.

        Args:
            spreads: List of potential spreads

        Returns:
            Filtered list of spreads meeting criteria
        """
        return [
            spread
            for spread in spreads
            if self.config.MIN_DELTA <= abs(spread.delta) <= self.config.MAX_DELTA
            and spread.cost <= self.config.MAX_SPREAD_COST
            and spread.reward_risk_ratio >= self.config.MIN_REWARD_RISK
            and spread.cost > 0  # Avoid zero or negative cost spreads (data errors)
        ]

    def create_call_vertical_spreads(
        self, option_chains: Dict[date, List[Option]], current_price: float
    ) -> List[OptionSpread]:
        """Create bull call spreads.

        Args:
            option_chains: Dictionary of options by expiration
            current_price: Current price of the underlying

        Returns:
            List of possible bull call spreads
        """
        spreads = []

        for expiry, chain in option_chains.items():
            # Extract calls and sort by strike
            calls = sorted(
                [opt for opt in chain if opt.option_type == "call"],
                key=lambda x: x.strike,
            )

            # Need at least 2 calls to create a spread
            if len(calls) < 2:
                continue

            # Create spreads for adjacent strikes
            for i in range(len(calls) - 1):
                long_call = calls[i]
                short_call = calls[i + 1]

                # Create the spread
                try:
                    # Calculate cost (net debit)
                    cost = long_call.ask - short_call.bid

                    # Calculate max profit and loss
                    max_profit = short_call.strike - long_call.strike - cost
                    max_loss = cost

                    # Skip if max_profit is negative or zero
                    if max_profit <= 0:
                        continue

                    # Calculate net delta
                    net_delta = long_call.delta - short_call.delta

                    spread = OptionSpread(
                        symbol=long_call.underlying,
                        expiration=expiry,
                        spread_type="BULL_CALL",
                        long_leg=long_call,
                        short_leg=short_call,
                        cost=cost * 100,  # Convert to dollars (1 contract = 100 shares)
                        max_profit=max_profit * 100,
                        max_loss=max_loss * 100,
                        delta=net_delta,
                        reward_risk_ratio=max_profit / cost if cost > 0 else 0,
                    )

                    spreads.append(spread)
                except Exception as e:
                    log_error(f"Error creating call spread: {str(e)}")

        return spreads

    def create_put_vertical_spreads(
        self, option_chains: Dict[date, List[Option]], current_price: float
    ) -> List[OptionSpread]:
        """Create bear put spreads.

        Args:
            option_chains: Dictionary of options by expiration
            current_price: Current price of the underlying

        Returns:
            List of possible bear put spreads
        """
        spreads = []

        for expiry, chain in option_chains.items():
            # Extract puts and sort by strike
            puts = sorted(
                [opt for opt in chain if opt.option_type == "put"],
                key=lambda x: x.strike,
            )

            # Need at least 2 puts to create a spread
            if len(puts) < 2:
                continue

            # Create spreads for adjacent strikes
            for i in range(len(puts) - 1):
                short_put = puts[i]
                long_put = puts[i + 1]

                # Create the spread
                try:
                    # Calculate cost (net debit)
                    cost = long_put.ask - short_put.bid

                    # Calculate max profit and loss
                    max_profit = long_put.strike - short_put.strike - cost
                    max_loss = cost

                    # Skip if max_profit is negative or zero
                    if max_profit <= 0:
                        continue

                    # Calculate net delta
                    net_delta = long_put.delta - short_put.delta

                    spread = OptionSpread(
                        symbol=long_put.underlying,
                        expiration=expiry,
                        spread_type="BEAR_PUT",
                        long_leg=long_put,
                        short_leg=short_put,
                        cost=cost * 100,  # Convert to dollars (1 contract = 100 shares)
                        max_profit=max_profit * 100,
                        max_loss=max_loss * 100,
                        delta=net_delta,
                        reward_risk_ratio=max_profit / cost if cost > 0 else 0,
                    )

                    spreads.append(spread)
                except Exception as e:
                    log_error(f"Error creating put spread: {str(e)}")

        return spreads

    def rank_by_reward_risk(self, spreads: List[OptionSpread]) -> List[OptionSpread]:
        """Rank spreads by reward-to-risk ratio.

        Args:
            spreads: List of spreads to rank

        Returns:
            Sorted list of spreads (highest reward/risk first)
        """
        return sorted(spreads, key=lambda x: x.reward_risk_ratio, reverse=True)

    def get_chain_by_expiration(
        self, chain: Dict[str, Dict[str, Any]], days_min: int, days_max: int
    ) -> Dict[str, Dict[str, Any]]:
        """Filter the option chain by expiration days.

        Args:
            chain: Option chain data
            days_min: Minimum days to expiration
            days_max: Maximum days to expiration

        Returns:
            Filtered option chain
        """
        filtered: Dict[str, Dict[str, Any]] = {}

        # Implement the filtering logic here
        for exp_date, options in chain.items():
            days = (
                datetime.strptime(exp_date, "%Y-%m-%d").date() - datetime.now().date()
            ).days
            if days_min <= days <= days_max:
                filtered[exp_date] = options

        return filtered

