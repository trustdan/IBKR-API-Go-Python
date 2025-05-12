"""
Scheduler module for trading schedule control.

This module implements time-based trading automation, allowing the application
to automatically start and stop trading based on configured schedules.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Callable, Optional

import pytz
import schedule

logger = logging.getLogger(__name__)


class TradingScheduler:
    """Manages trading schedule and controls trading_enabled state."""

    def __init__(self, config: dict, trading_enabled_setter: Callable[[bool], None]):
        """
        Initialize the trading scheduler.

        Args:
            config: Configuration dictionary with scheduling settings
            trading_enabled_setter: Callback function to set trading_enabled state
        """
        self.config = config
        self.set_trading_enabled = trading_enabled_setter
        self.scheduler_thread: Optional[threading.Thread] = None
        self.running = False

        # Initialize scheduler
        self._configure_schedule()

    def _configure_schedule(self) -> None:
        """Configure the scheduler based on current config."""
        # Clear any existing schedules
        schedule.clear()

        scheduling_config = self.config.get("scheduling", {})
        trading_days = scheduling_config.get(
            "trading_days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        )
        start_time = scheduling_config.get("trading_start_time", "09:30:00")
        end_time = scheduling_config.get("trading_end_time", "16:00:00")
        timezone_str = scheduling_config.get("timezone", "America/New_York")

        try:
            timezone = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.error(
                f"Unknown timezone: {timezone_str}, defaulting to America/New_York"
            )
            timezone = pytz.timezone("America/New_York")

        # Register start trading job for each trading day
        for day in trading_days:
            day_lower = day.lower()
            # Get the proper schedule.every().<day> method
            day_scheduler = getattr(schedule.every(), day_lower, None)
            if day_scheduler:
                day_scheduler.at(start_time).do(self._start_trading, day, start_time)
                logger.info(f"Scheduled trading start on {day} at {start_time}")
            else:
                logger.warning(f"Invalid day '{day}' in trading_days config")

        # Register end trading job for each trading day
        for day in trading_days:
            day_lower = day.lower()
            day_scheduler = getattr(schedule.every(), day_lower, None)
            if day_scheduler:
                day_scheduler.at(end_time).do(self._stop_trading, day, end_time)
                logger.info(f"Scheduled trading stop on {day} at {end_time}")

    def _start_trading(self, day: str, time_str: str) -> None:
        """
        Start trading at the scheduled time.

        Args:
            day: Day of the week
            time_str: Time string in HH:MM:SS format
        """
        logger.info(f"Starting automated trading (scheduled for {day} at {time_str})")
        self.set_trading_enabled(True)

    def _stop_trading(self, day: str, time_str: str) -> None:
        """
        Stop trading at the scheduled time.

        Args:
            day: Day of the week
            time_str: Time string in HH:MM:SS format
        """
        logger.info(f"Stopping automated trading (scheduled for {day} at {time_str})")
        self.set_trading_enabled(False)

    def start(self) -> None:
        """Start the scheduler in a background thread."""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.warning("Scheduler already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        logger.info("Trading scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2.0)
        logger.info("Trading scheduler stopped")

    def _run_scheduler(self) -> None:
        """Run the scheduler loop in background thread."""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def reload_config(self, config: dict) -> None:
        """
        Reload configuration and update schedules.

        Args:
            config: New configuration dictionary
        """
        self.config = config
        self._configure_schedule()
        logger.info("Trading scheduler configuration reloaded")

    def is_trading_time(self) -> bool:
        """
        Check if current time is within trading hours.

        Returns:
            bool: True if current time is within configured trading hours
        """
        scheduling_config = self.config.get("scheduling", {})
        trading_days = scheduling_config.get(
            "trading_days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        )
        start_time = scheduling_config.get("trading_start_time", "09:30:00")
        end_time = scheduling_config.get("trading_end_time", "16:00:00")
        timezone_str = scheduling_config.get("timezone", "America/New_York")

        try:
            timezone = pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            timezone = pytz.timezone("America/New_York")

        now = datetime.now(timezone)
        day_of_week = now.strftime("%A")

        if day_of_week not in trading_days:
            return False

        current_time = now.strftime("%H:%M:%S")
        return start_time <= current_time <= end_time
