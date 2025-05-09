"""
Enhanced option spread filtering module.

This module implements the greater-fidelity filtering for option spreads based on the
enhanced parameters defined in the configuration.
"""

import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class OptionSpreadFilter:
    """
    Enhanced filter for option spreads with greater fidelity controls.

    This class implements all the filtering criteria described in greater-fidelity.md,
    including liquidity filters, IV regime checks, Greek-based risk controls,
    probability metrics, event avoidance, and strike selection flexibility.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the option spread filter with configuration parameters.

        Args:
            config: Dictionary containing the options configuration settings
        """
        self.config = config

        # Extract basic settings
        self.min_dte = config.get("min_dte", 30)
        self.max_dte = config.get("max_dte", 45)
        self.min_delta = config.get("min_delta", 0.30)
        self.max_delta = config.get("max_delta", 0.45)
        self.max_spread_cost = config.get("max_spread_cost", 500)
        self.min_reward_risk = config.get("min_reward_risk", 1.5)

        # Liquidity & Execution-Quality Filters
        self.min_open_interest = config.get("min_open_interest", 1000)
        self.max_bid_ask_spread_pct = config.get("max_bid_ask_spread_pct", 0.5)

        # Implied-Volatility Regime
        self.min_iv_rank = config.get("min_iv_rank", 0.0)
        self.max_iv_rank = config.get("max_iv_rank", 100.0)
        self.min_call_put_skew_pct = config.get("min_call_put_skew_pct", 0.0)

        # Greek-Based Risk Controls
        self.max_theta_per_day = config.get("max_theta_per_day", 10.0)
        self.max_vega_exposure = config.get("max_vega_exposure", 0.4)
        self.max_gamma_exposure = config.get("max_gamma_exposure", 0.4)

        # Probability & Expected-Move Metrics
        self.min_prob_of_profit = config.get("min_prob_of_profit", 65.0)
        self.max_width_vs_move_pct = config.get("max_width_vs_move_pct", 150.0)

        # Event & Calendar Controls
        self.days_before_earnings = config.get("days_before_earnings", 5)
        self.days_before_ex_div = config.get("days_before_ex_div", 3)
        self.dte_from_atr = config.get("dte_from_atr", False)
        self.atr_coefficient = config.get("atr_coefficient", 2.0)

        # Strike-Selection Flexibility
        self.strike_offset = config.get("strike_offset", 1)
        self.spread_width = config.get("spread_width", 1)

    def filter_spreads(self, spreads: List[Dict], underlying_data: Dict) -> List[Dict]:
        """
        Filter option spreads based on all enhanced criteria.

        Args:
            spreads: List of option spread dictionaries
            underlying_data: Dictionary with underlying stock data including
                             price, IV, earnings date, ex-dividend date, etc.

        Returns:
            Filtered list of option spreads
        """
        filtered_spreads = []

        for spread in spreads:
            if self._passes_all_filters(spread, underlying_data):
                filtered_spreads.append(spread)

        return filtered_spreads

    def _passes_all_filters(self, spread: Dict, underlying_data: Dict) -> bool:
        """
        Check if a spread passes all the filtering criteria.

        Args:
            spread: Option spread dictionary
            underlying_data: Dictionary with underlying stock data

        Returns:
            True if the spread passes all filters, False otherwise
        """
        # Check basic criteria
        if not self._check_basic_criteria(spread):
            return False

        # Check liquidity and execution quality
        if not self._check_liquidity(spread):
            return False

        # Check IV regime
        if not self._check_iv_regime(spread, underlying_data):
            return False

        # Check Greek risk controls
        if not self._check_greek_risks(spread):
            return False

        # Check probability metrics
        if not self._check_probability_metrics(spread, underlying_data):
            return False

        # Check calendar events
        if not self._check_calendar_events(underlying_data):
            return False

        # If we passed all filters, return True
        return True

    def _check_basic_criteria(self, spread: Dict) -> bool:
        """Check basic spread criteria like DTE, delta, spread cost, and reward/risk."""
        # Check Days to Expiration
        dte = spread.get("dte", 0)
        if self.dte_from_atr:
            # If using dynamic DTE, calculate based on ATR
            atr = spread.get("atr", 0)
            adjusted_min_dte = max(self.min_dte, int(atr * self.atr_coefficient))
            adjusted_max_dte = max(self.max_dte, int(atr * self.atr_coefficient * 1.5))

            if dte < adjusted_min_dte or dte > adjusted_max_dte:
                return False
        else:
            # Use fixed DTE range
            if dte < self.min_dte or dte > self.max_dte:
                return False

        # Check delta
        delta = abs(spread.get("delta", 0))
        if delta < self.min_delta or delta > self.max_delta:
            return False

        # Check spread cost
        spread_cost = spread.get("cost", 0) * 100  # Convert to dollars
        if spread_cost > self.max_spread_cost:
            return False

        # Check reward/risk ratio
        reward_risk = spread.get("reward_risk", 0)
        if reward_risk < self.min_reward_risk:
            return False

        return True

    def _check_liquidity(self, spread: Dict) -> bool:
        """Check liquidity and execution quality criteria."""
        # Check open interest
        leg1_open_interest = spread.get("leg1_open_interest", 0)
        leg2_open_interest = spread.get("leg2_open_interest", 0)
        min_open_interest = min(leg1_open_interest, leg2_open_interest)

        if min_open_interest < self.min_open_interest:
            return False

        # Check bid-ask spread percentage
        leg1_bid = spread.get("leg1_bid", 0)
        leg1_ask = spread.get("leg1_ask", 0)
        leg2_bid = spread.get("leg2_bid", 0)
        leg2_ask = spread.get("leg2_ask", 0)

        # Calculate bid-ask spread percentage for each leg
        if leg1_ask == 0 or leg2_ask == 0:
            return False  # Avoid division by zero

        leg1_spread_pct = (leg1_ask - leg1_bid) / leg1_ask * 100
        leg2_spread_pct = (leg2_ask - leg2_bid) / leg2_ask * 100
        max_spread_pct = max(leg1_spread_pct, leg2_spread_pct)

        if max_spread_pct > self.max_bid_ask_spread_pct:
            return False

        return True

    def _check_iv_regime(self, spread: Dict, underlying_data: Dict) -> bool:
        """Check IV rank and skew criteria."""
        # Check IV rank
        iv_rank = underlying_data.get("iv_rank", 0) * 100  # Convert to percentage
        if iv_rank < self.min_iv_rank or iv_rank > self.max_iv_rank:
            return False

        # Check call/put skew
        call_put_skew = (
            underlying_data.get("call_put_skew", 0) * 100
        )  # Convert to percentage
        if call_put_skew < self.min_call_put_skew_pct:
            return False

        return True

    def _check_greek_risks(self, spread: Dict) -> bool:
        """Check Greek-based risk controls."""
        # Check theta
        theta_per_day = abs(spread.get("theta", 0)) * 100  # Convert to dollars
        if theta_per_day > self.max_theta_per_day:
            return False

        # Check vega
        vega_exposure = abs(spread.get("vega", 0))
        if vega_exposure > self.max_vega_exposure:
            return False

        # Check gamma
        gamma_exposure = abs(spread.get("gamma", 0))
        if gamma_exposure > self.max_gamma_exposure:
            return False

        return True

    def _check_probability_metrics(self, spread: Dict, underlying_data: Dict) -> bool:
        """Check probability of profit and expected move criteria."""
        # Check probability of profit
        prob_of_profit = (
            spread.get("probability_of_profit", 0) * 100
        )  # Convert to percentage
        if prob_of_profit < self.min_prob_of_profit:
            return False

        # Check spread width vs expected move
        expected_move = underlying_data.get("expected_move", 0)
        if expected_move == 0:
            return True  # Skip if expected move is not available

        spread_width = abs(spread.get("leg1_strike", 0) - spread.get("leg2_strike", 0))
        width_vs_move_pct = (spread_width / expected_move) * 100

        if width_vs_move_pct > self.max_width_vs_move_pct:
            return False

        return True

    def _check_calendar_events(self, underlying_data: Dict) -> bool:
        """Check calendar events like earnings and dividends."""
        today = datetime.datetime.now().date()

        # Check earnings date
        earnings_date_str = underlying_data.get("earnings_date", "")
        if earnings_date_str:
            try:
                earnings_date = datetime.datetime.strptime(
                    earnings_date_str, "%Y-%m-%d"
                ).date()
                days_to_earnings = (earnings_date - today).days

                if 0 <= days_to_earnings <= self.days_before_earnings:
                    return False
            except (ValueError, TypeError):
                pass  # Skip if date format is invalid

        # Check ex-dividend date
        ex_div_date_str = underlying_data.get("ex_dividend_date", "")
        if ex_div_date_str:
            try:
                ex_div_date = datetime.datetime.strptime(
                    ex_div_date_str, "%Y-%m-%d"
                ).date()
                days_to_ex_div = (ex_div_date - today).days

                if 0 <= days_to_ex_div <= self.days_before_ex_div:
                    return False
            except (ValueError, TypeError):
                pass  # Skip if date format is invalid

        return True

    def select_strikes(
        self, chain: Dict, underlying_price: float, spread_type: str
    ) -> List[Dict]:
        """
        Select strikes for option spreads based on offset and width parameters.

        Args:
            chain: Option chain dictionary with calls and puts
            underlying_price: Current price of the underlying
            spread_type: Type of spread (e.g., "BULL_PUT_SPREAD", "BEAR_CALL_SPREAD")

        Returns:
            List of selected spreads with appropriate strikes
        """
        selected_spreads = []

        # Determine which options to use (calls or puts)
        if "CALL" in spread_type:
            options = chain.get("calls", [])
        else:
            options = chain.get("puts", [])

        # Sort options by strike
        options.sort(key=lambda x: x.get("strike", 0))

        # Find the ATM option (closest to current price)
        atm_index = 0
        min_diff = float("inf")

        for i, option in enumerate(options):
            strike = option.get("strike", 0)
            diff = abs(strike - underlying_price)

            if diff < min_diff:
                min_diff = diff
                atm_index = i

        # Apply strike offset from ATM
        if "BULL" in spread_type:
            # For bull spreads, go below ATM
            start_index = max(0, atm_index - self.strike_offset)
        else:
            # For bear spreads, go above ATM
            start_index = min(len(options) - 1, atm_index + self.strike_offset)

        # Apply spread width
        if "BULL" in spread_type and "PUT" in spread_type:
            # Bull put spread: sell higher strike, buy lower strike
            for i in range(
                start_index, min(len(options) - self.spread_width, start_index + 5)
            ):
                short_leg = options[i + self.spread_width]
                long_leg = options[i]

                spread = {
                    "type": "BULL_PUT_SPREAD",
                    "short_leg": short_leg,
                    "long_leg": long_leg,
                    "leg1_strike": short_leg.get("strike", 0),
                    "leg2_strike": long_leg.get("strike", 0),
                    "dte": short_leg.get("dte", 0),
                    "delta": short_leg.get("delta", 0),
                    "gamma": short_leg.get("gamma", 0),
                    "theta": short_leg.get("theta", 0),
                    "vega": short_leg.get("vega", 0),
                    "cost": short_leg.get("bid", 0) - long_leg.get("ask", 0),
                    "max_profit": short_leg.get("bid", 0) - long_leg.get("ask", 0),
                    "max_loss": (short_leg.get("strike", 0) - long_leg.get("strike", 0))
                    - (short_leg.get("bid", 0) - long_leg.get("ask", 0)),
                    "leg1_bid": short_leg.get("bid", 0),
                    "leg1_ask": short_leg.get("ask", 0),
                    "leg2_bid": long_leg.get("bid", 0),
                    "leg2_ask": long_leg.get("ask", 0),
                    "leg1_open_interest": short_leg.get("open_interest", 0),
                    "leg2_open_interest": long_leg.get("open_interest", 0),
                }

                # Calculate reward/risk ratio and probability of profit
                if spread["max_loss"] > 0:
                    spread["reward_risk"] = spread["max_profit"] / spread["max_loss"]
                    # Simplified probability calculation (can be replaced with more accurate model)
                    probability_otm = 1 - abs(short_leg.get("delta", 0))
                    spread["probability_of_profit"] = probability_otm

                    selected_spreads.append(spread)

        elif "BEAR" in spread_type and "CALL" in spread_type:
            # Bear call spread: sell lower strike, buy higher strike
            for i in range(
                max(0, start_index - 5),
                min(len(options) - self.spread_width, start_index),
            ):
                short_leg = options[i]
                long_leg = options[i + self.spread_width]

                spread = {
                    "type": "BEAR_CALL_SPREAD",
                    "short_leg": short_leg,
                    "long_leg": long_leg,
                    "leg1_strike": short_leg.get("strike", 0),
                    "leg2_strike": long_leg.get("strike", 0),
                    "dte": short_leg.get("dte", 0),
                    "delta": short_leg.get("delta", 0),
                    "gamma": short_leg.get("gamma", 0),
                    "theta": short_leg.get("theta", 0),
                    "vega": short_leg.get("vega", 0),
                    "cost": short_leg.get("bid", 0) - long_leg.get("ask", 0),
                    "max_profit": short_leg.get("bid", 0) - long_leg.get("ask", 0),
                    "max_loss": (long_leg.get("strike", 0) - short_leg.get("strike", 0))
                    - (short_leg.get("bid", 0) - long_leg.get("ask", 0)),
                    "leg1_bid": short_leg.get("bid", 0),
                    "leg1_ask": short_leg.get("ask", 0),
                    "leg2_bid": long_leg.get("bid", 0),
                    "leg2_ask": long_leg.get("ask", 0),
                    "leg1_open_interest": short_leg.get("open_interest", 0),
                    "leg2_open_interest": long_leg.get("open_interest", 0),
                }

                # Calculate reward/risk ratio and probability of profit
                if spread["max_loss"] > 0:
                    spread["reward_risk"] = spread["max_profit"] / spread["max_loss"]
                    # Simplified probability calculation (can be replaced with more accurate model)
                    probability_otm = 1 - abs(short_leg.get("delta", 0))
                    spread["probability_of_profit"] = probability_otm

                    selected_spreads.append(spread)

        return selected_spreads
