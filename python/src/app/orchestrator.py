"""
Main orchestrator module for the trading system.

Coordinates trading activities, handles configuration, and manages
the trading schedule based on configured times.
"""

import logging
import os
import signal
import sys
import threading
import time
from typing import Any, Dict, Optional

import toml
import yaml
from app.scheduler import TradingScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class Orchestrator:
    """Main orchestrator class for the trading system."""

    def __init__(self, config_path: str = None):
        """
        Initialize the orchestrator.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or os.environ.get(
            "CONFIG_PATH", "/config/config.toml"
        )
        self.config: Dict[str, Any] = {}
        self.trading_enabled = threading.Event()
        self.running = False
        self.scheduler: Optional[TradingScheduler] = None

        # Set up signal handlers
        signal.signal(signal.SIGUSR1, self._handle_reload_signal)
        signal.signal(signal.SIGTERM, self._handle_terminate_signal)
        signal.signal(signal.SIGINT, self._handle_terminate_signal)

        # Load initial configuration
        self._load_config()

        # Initialize scheduler
        self.scheduler = TradingScheduler(self.config, self._set_trading_enabled)

    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            # Determine file format based on extension
            if self.config_path.endswith(".toml"):
                with open(self.config_path, "r") as f:
                    self.config = toml.load(f)
            elif self.config_path.endswith(".yaml") or self.config_path.endswith(
                ".yml"
            ):
                with open(self.config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                logger.error(f"Unsupported config file format: {self.config_path}")
                sys.exit(1)

            logger.info(f"Configuration loaded from {self.config_path}")

            # Set initial trading_enabled state based on scheduler if available
            if self.scheduler:
                self.scheduler.reload_config(self.config)
                trading_time = self.scheduler.is_trading_time()
                self._set_trading_enabled(trading_time)

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Keep running with existing config if we had one
            if not self.config:
                sys.exit(1)

    def _set_trading_enabled(self, enabled: bool) -> None:
        """
        Set the trading_enabled flag.

        Args:
            enabled: Whether trading should be enabled
        """
        if enabled:
            self.trading_enabled.set()
            logger.info("Trading enabled")
        else:
            self.trading_enabled.clear()
            logger.info("Trading disabled")

    def _handle_reload_signal(self, signum: int, frame: Any) -> None:
        """
        Handle the reload signal (SIGUSR1).

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info("Received reload signal")
        self._load_config()

    def _handle_terminate_signal(self, signum: int, frame: Any) -> None:
        """
        Handle termination signals (SIGTERM, SIGINT).

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received termination signal {signum}")
        self.stop()

    def start(self) -> None:
        """Start the orchestrator and scheduler."""
        if self.running:
            logger.warning("Orchestrator already running")
            return

        self.running = True

        # Start the scheduler
        if self.scheduler:
            self.scheduler.start()

        # Check if we should be trading now
        if self.scheduler and self.scheduler.is_trading_time():
            self._set_trading_enabled(True)

        logger.info("Orchestrator started")

        # Main loop
        try:
            while self.running:
                # Check if trading is enabled
                if self.trading_enabled.is_set():
                    # This is where trading logic would go
                    # For now, just log the state
                    logger.debug("Trading is currently enabled")
                else:
                    logger.debug("Trading is currently disabled")

                # Sleep to avoid busy loop
                time.sleep(5)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        """Stop the orchestrator and scheduler."""
        self.running = False
        if self.scheduler:
            self.scheduler.stop()
        self._set_trading_enabled(False)
        logger.info("Orchestrator stopped")


if __name__ == "__main__":
    # Entry point when run directly
    orchestrator = Orchestrator()
    orchestrator.start()
