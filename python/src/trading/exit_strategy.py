"""
Exit strategies implementation for options trading.
"""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.app.config import Config
from src.models.option import OptionSpread
from src.utils.logger import log_debug, log_error, log_info, log_warning


class ExitStrategyManager:
    """
    Manages different exit strategies for option trades.

    Implements various exit methodologies:
    - Stop-loss monitoring
    - Profit target exits
    - Fibonacci-based exits
    - ATR-based exits
    - R-multiple exits
    - Time-based exits
    """

    def __init__(self, config: Config):
        """
        Initialize the exit strategy manager.

        Args:
            config: Configuration parameters
        """
        self.config = config

    def calculate_exits(
        self,
        entry_price: float,
        direction: str,
        option_spread: OptionSpread,
        underlying_data: Optional[Dict] = None,
    ) -> Dict[str, float]:
        """
        Calculate exit levels for a position.

        Args:
            entry_price: Entry price of the spread
            direction: Trade direction ('LONG' or 'SHORT')
            option_spread: Option spread details
            underlying_data: Historical data for the underlying (for ATR calculations)

        Returns:
            Dictionary of exit prices by strategy type
        """
        exits = {}

        # Basic stop loss (percentage-based)
        exits["stop_loss"] = self._calculate_stop_loss(entry_price, direction)

        # Profit target
        exits["profit_target"] = self._calculate_profit_target(
            entry_price, direction, option_spread
        )

        # R-multiple exit
        if getattr(self.config, "USE_R_MULTIPLE_EXIT", False):
            exits["r_multiple"] = self._calculate_r_multiple_exit(
                entry_price, direction, exits["stop_loss"]
            )

        # ATR-based exit
        if getattr(self.config, "USE_ATR_EXIT", False) and underlying_data:
            exits["atr_exit"] = self._calculate_atr_exit(
                entry_price, direction, underlying_data
            )

        # Fibonacci-based exit
        if getattr(self.config, "USE_FIBONACCI_EXIT", False):
            exits["fibonacci_exit"] = self._calculate_fibonacci_exit(
                entry_price, direction, option_spread
            )

        return exits

    def _calculate_stop_loss(self, entry_price: float, direction: str) -> float:
        """
        Calculate basic stop loss based on percentage from entry.

        Args:
            entry_price: Entry price
            direction: 'LONG' or 'SHORT'

        Returns:
            Stop loss price
        """
        stop_percentage = getattr(
            self.config, "STOP_LOSS_PERCENTAGE", 0.5
        )  # Default 50%

        if direction == "LONG":
            # For long positions, stop loss is below entry price
            stop_price = entry_price * (1 - stop_percentage)
        else:  # SHORT
            # For short positions, stop loss is above entry price
            stop_price = entry_price * (1 + stop_percentage)

        # Ensure stop loss isn't below minimum value
        return max(stop_price, 0.05)

    def _calculate_profit_target(
        self, entry_price: float, direction: str, option_spread: OptionSpread
    ) -> float:
        """
        Calculate profit target based on reward-to-risk ratio.

        Args:
            entry_price: Entry price
            direction: 'LONG' or 'SHORT'
            option_spread: Option spread details

        Returns:
            Profit target price
        """
        target_ratio = getattr(self.config, "TARGET_REWARD_RISK", 1.5)

        # Calculate max possible profit
        if direction == "LONG":
            if option_spread.spread_type == "BULL_CALL":
                # Bull call spread: difference between strikes minus cost
                max_profit = (
                    option_spread.short_leg.strike - option_spread.long_leg.strike
                ) - entry_price
            else:  # BEAR_PUT
                # Bear put spread: difference between strikes minus cost
                max_profit = (
                    option_spread.long_leg.strike - option_spread.short_leg.strike
                ) - entry_price
        else:  # SHORT
            if option_spread.spread_type == "BEAR_CALL":
                # Bear call spread: premium received (cost)
                max_profit = entry_price
            else:  # BULL_PUT
                # Bull put spread: premium received (cost)
                max_profit = entry_price

        # Risk is typically the entry cost
        risk = entry_price

        # Target based on risk-reward ratio
        target_profit = min(max_profit, risk * target_ratio)

        # Calculate target price
        if direction == "LONG":
            target_price = entry_price + target_profit
        else:  # SHORT
            target_price = max(entry_price - target_profit, 0.05)

        return target_price

    def _calculate_r_multiple_exit(
        self, entry_price: float, direction: str, stop_loss: float
    ) -> float:
        """
        Calculate R-multiple exit level.

        Args:
            entry_price: Entry price
            direction: 'LONG' or 'SHORT'
            stop_loss: Stop loss price

        Returns:
            R-multiple target price
        """
        # R value is the risk per share/contract
        r_value = abs(entry_price - stop_loss)
        r_multiple = getattr(self.config, "R_MULTIPLE_TARGET", 2.0)

        if direction == "LONG":
            # For long positions, target is above entry
            target_price = entry_price + (r_value * r_multiple)
        else:  # SHORT
            # For short positions, target is below entry
            target_price = max(entry_price - (r_value * r_multiple), 0.05)

        return target_price

    def _calculate_atr_exit(
        self, entry_price: float, direction: str, underlying_data: Dict
    ) -> float:
        """
        Calculate ATR-based exit level.

        Args:
            entry_price: Entry price
            direction: 'LONG' or 'SHORT'
            underlying_data: Historical data with ATR

        Returns:
            ATR-based target price
        """
        # Get the ATR value
        atr = underlying_data.get("atr", 0)
        if not atr:
            # If ATR is not available, fall back to fixed percentage
            return self._calculate_profit_target(entry_price, direction, None)

        atr_multiple = getattr(self.config, "ATR_TARGET_MULTIPLE", 3.0)

        if direction == "LONG":
            # For long positions, target is entry + ATR multiple
            target_price = entry_price + (atr * atr_multiple)
        else:  # SHORT
            # For short positions, target is entry - ATR multiple
            target_price = max(entry_price - (atr * atr_multiple), 0.05)

        return target_price

    def _calculate_fibonacci_exit(
        self, entry_price: float, direction: str, option_spread: OptionSpread
    ) -> float:
        """
        Calculate Fibonacci-based exit level.

        Args:
            entry_price: Entry price
            direction: 'LONG' or 'SHORT'
            option_spread: Option spread details

        Returns:
            Fibonacci-based target price
        """
        # Calculate the range (max possible move)
        if direction == "LONG":
            if option_spread.spread_type == "BULL_CALL":
                price_range = (
                    option_spread.short_leg.strike - option_spread.long_leg.strike
                ) - entry_price
            else:  # BEAR_PUT
                price_range = (
                    option_spread.long_leg.strike - option_spread.short_leg.strike
                ) - entry_price
        else:  # SHORT
            price_range = entry_price

        # Default Fibonacci level (1.618 is common)
        fib_level = getattr(self.config, "FIBONACCI_TARGET_LEVEL", 1.618)

        # Apply Fibonacci level to the range
        fib_target = price_range * fib_level

        # Calculate target price
        if direction == "LONG":
            target_price = entry_price + fib_target
        else:  # SHORT
            target_price = max(entry_price - fib_target, 0.05)

        return target_price

    def should_exit_position(
        self,
        position: Dict,
        current_price: float,
        days_to_expiry: int,
        underlying_data: Optional[Dict] = None,
    ) -> Tuple[bool, str]:
        """
        Determine if a position should be exited based on current conditions.

        Args:
            position: Position details
            current_price: Current price of the position
            days_to_expiry: Days to option expiration
            underlying_data: Historical data for the underlying

        Returns:
            Tuple of (should_exit, reason)
        """
        direction = position["direction"]
        entry_price = position["entry_price"]

        # Check stop loss
        stop_loss = position.get("stop_price")
        if stop_loss:
            if direction == "LONG" and current_price <= stop_loss:
                return True, "Stop loss triggered"
            elif direction == "SHORT" and current_price >= stop_loss:
                return True, "Stop loss triggered"

        # Check profit target
        target_price = position.get("target_price")
        if target_price:
            if direction == "LONG" and current_price >= target_price:
                return True, "Profit target reached"
            elif direction == "SHORT" and current_price <= target_price:
                return True, "Profit target reached"

        # Check time-based exit (option expiration approach)
        min_days = getattr(self.config, "MIN_DAYS_TO_EXPIRY", 5)
        if days_to_expiry <= min_days:
            return True, f"Position close to expiry ({days_to_expiry} days)"

        # Check R-multiple exit
        if getattr(self.config, "USE_R_MULTIPLE_EXIT", False):
            stop_loss = position.get(
                "stop_price", self._calculate_stop_loss(entry_price, direction)
            )
            r_value = abs(entry_price - stop_loss)
            r_multiple = getattr(self.config, "R_MULTIPLE_TARGET", 2.0)

            if direction == "LONG":
                r_target = entry_price + (r_value * r_multiple)
                if current_price >= r_target:
                    return True, f"R-multiple target reached ({r_multiple}R)"
            else:  # SHORT
                r_target = entry_price - (r_value * r_multiple)
                if current_price <= r_target:
                    return True, f"R-multiple target reached ({r_multiple}R)"

        # Check trailing stop if enabled
        if getattr(self.config, "USE_TRAILING_STOP", False):
            trailing_result = self._check_trailing_stop(position, current_price)
            if trailing_result[0]:
                return trailing_result

        # Additional exit criteria can be implemented here

        return False, "No exit criteria met"

    def _check_trailing_stop(
        self, position: Dict, current_price: float
    ) -> Tuple[bool, str]:
        """
        Check if trailing stop has been triggered.

        Args:
            position: Position details
            current_price: Current price

        Returns:
            Tuple of (should_exit, reason)
        """
        direction = position["direction"]
        entry_price = position["entry_price"]
        highest_price = position.get("highest_price", entry_price)
        lowest_price = position.get("lowest_price", entry_price)

        # Trailing percentage
        trail_percentage = getattr(
            self.config, "TRAILING_STOP_PERCENTAGE", 0.2
        )  # 20% by default

        if direction == "LONG":
            # Update highest observed price
            if current_price > highest_price:
                position["highest_price"] = current_price
                highest_price = current_price

            # Check if price has dropped from highest by trail percentage
            trailing_stop = highest_price * (1 - trail_percentage)
            if current_price <= trailing_stop:
                return (
                    True,
                    f"Trailing stop triggered ({trail_percentage:.1%} from high of {highest_price:.2f})",
                )
        else:  # SHORT
            # Update lowest observed price
            if current_price < lowest_price:
                position["lowest_price"] = current_price
                lowest_price = current_price

            # Check if price has risen from lowest by trail percentage
            trailing_stop = lowest_price * (1 + trail_percentage)
            if current_price >= trailing_stop:
                return (
                    True,
                    f"Trailing stop triggered ({trail_percentage:.1%} from low of {lowest_price:.2f})",
                )

        return False, "Trailing stop not triggered"

    def get_stop_distance(self, position: Dict) -> float:
        """
        Calculate the distance from current price to stop loss.

        Args:
            position: Position details including current price and stop price

        Returns:
            Distance from current price to stop loss as percentage
        """
        current_price = position.get("current_price", position["entry_price"])
        stop_price = position.get("stop_price", 0)

        if current_price == 0 or stop_price == 0:
            return 0

        if position["direction"] == "LONG":
            return (current_price - stop_price) / current_price
        else:  # SHORT
            return (stop_price - current_price) / current_price

    def update_exits_for_position(
        self,
        position: Dict,
        current_price: float,
        underlying_data: Optional[Dict] = None,
    ) -> Dict:
        """
        Update exit levels for a position based on current price.

        Args:
            position: Position details
            current_price: Current price of the position
            underlying_data: Historical data for the underlying

        Returns:
            Updated position dictionary
        """
        direction = position["direction"]
        entry_price = position["entry_price"]
        option_spread = position["spread"]

        # Only update trailing stops and adaptive exits
        if getattr(self.config, "USE_TRAILING_STOP", False):
            if direction == "LONG":
                # Update highest observed price
                highest_price = position.get("highest_price", entry_price)
                if current_price > highest_price:
                    position["highest_price"] = current_price

                    # Update trailing stop if enabled
                    trail_percentage = getattr(
                        self.config, "TRAILING_STOP_PERCENTAGE", 0.2
                    )
                    position["trailing_stop"] = current_price * (1 - trail_percentage)
            else:  # SHORT
                # Update lowest observed price
                lowest_price = position.get("lowest_price", entry_price)
                if current_price < lowest_price:
                    position["lowest_price"] = current_price

                    # Update trailing stop if enabled
                    trail_percentage = getattr(
                        self.config, "TRAILING_STOP_PERCENTAGE", 0.2
                    )
                    position["trailing_stop"] = current_price * (1 + trail_percentage)

        # Update ATR-based exits if enabled and underlying data available
        if getattr(self.config, "USE_ADAPTIVE_ATR_EXIT", False) and underlying_data:
            position["atr_exit"] = self._calculate_atr_exit(
                entry_price, direction, underlying_data
            )

        return position
