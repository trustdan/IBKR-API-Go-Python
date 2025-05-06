"""
Application configuration module.
This module provides application-specific configuration settings.
The base Config class is imported from the config module.
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import yaml
from src.config.config import Config as BaseConfig


@dataclass
class Config(BaseConfig):
    """Application-specific configuration extends the base Config."""

    # Scanner service configuration
    SCANNER_HOST: str = "localhost"
    SCANNER_PORT: int = 50051

    # Strategy Parameters
    HIGH_BASE_MAX_ATR_RATIO: float = 2.0
    HIGH_BASE_MIN_RSI: float = 60
    LOW_BASE_MIN_ATR_RATIO: float = 0.5
    LOW_BASE_MAX_RSI: float = 40
    BULL_PULLBACK_RSI_THRESHOLD: float = 45
    BEAR_RALLY_RSI_THRESHOLD: float = 55

    # Trade Execution Mode
    TRADING_MODE: str = "PAPER"  # Options: "PAPER" or "LIVE"
    PRICE_IMPROVEMENT_FACTOR: float = 0.4  # For live trading: 0.5 = midpoint, <0.5 = closer to bid, >0.5 = closer to ask

    # Risk Management Parameters
    MAX_POSITIONS: int = 5
    MAX_DAILY_TRADES: int = 3
    STOP_LOSS_ATR_MULT: float = 2.0
    RISK_PER_TRADE: float = 0.02  # 2% account risk per trade
    MAX_CONTRACTS_PER_TRADE: int = 10
    # New Risk Management Parameters for Stage 4
    MAX_PORTFOLIO_HEAT: float = 10.0  # Maximum portfolio heat (percentage at risk)
    MAX_SECTOR_EXPOSURE: float = (
        0.30  # Maximum exposure to a single sector (30% of portfolio)
    )
    MAX_INDUSTRY_EXPOSURE: float = (
        0.20  # Maximum exposure to a single industry (20% of portfolio)
    )
    MAX_DIRECTIONAL_BIAS: float = 0.70  # Maximum directional bias (70% long/short)
    MIN_BUYING_POWER: float = 5000.0  # Minimum buying power to maintain

    # Option Selection Parameters
    MIN_DTE: int = 30
    MAX_DTE: int = 45
    MIN_DELTA: float = 0.30
    MAX_DELTA: float = 0.50
    MAX_SPREAD_COST: float = 500  # Max cost per spread in dollars
    MIN_REWARD_RISK: float = 1.5  # Minimum reward-to-risk ratio

    # Exit Strategy Parameters
    USE_FIBO_TARGETS: bool = True
    FIBO_TARGET_LEVEL: float = 1.618
    USE_R_MULTIPLE: bool = True
    R_MULTIPLE_TARGET: float = 2.0
    USE_ATR_TARGET: bool = True
    ATR_TARGET_MULTIPLE: float = 3.0
    MIN_DAYS_TO_EXIT: int = 14
    # New Exit Strategy Parameters for Stage 4
    USE_R_MULTIPLE_EXIT: bool = True
    STOP_LOSS_PERCENTAGE: float = 0.5  # 50% loss from entry triggers stop loss
    TARGET_REWARD_RISK: float = 1.5  # Target profit is 1.5x risk
    MIN_DAYS_TO_EXPIRY: int = 5  # Exit position when 5 days or less to expiry
    USE_TRAILING_STOP: bool = True  # Enable trailing stops
    TRAILING_STOP_PERCENTAGE: float = 0.2  # 20% trail from high/low
    USE_FIBONACCI_EXIT: bool = True
    FIBONACCI_TARGET_LEVEL: float = 1.618  # Fibonacci target level for exits
    USE_ADAPTIVE_ATR_EXIT: bool = False  # Enable ATR-based adaptive exits

    # Trade Execution Timing
    ALLOW_LATE_DAY_ENTRY: bool = True

    # Universe Filtering
    MIN_MARKET_CAP: int = 10_000_000_000  # $10B
    MIN_PRICE: float = 20
    MIN_VOLUME: int = 1_000_000

    # Performance Benchmarks
    MAX_SCAN_TIME: float = 5.0  # seconds
    MIN_SYMBOLS_PER_SECOND: int = 50
    MAX_ORDER_LATENCY: float = 0.5  # seconds
    CRITICAL_ORDER_LATENCY: float = 2.0  # seconds
    # New Performance Monitoring Thresholds for Stage 4
    API_REQUEST_WARNING_THRESHOLD: float = (
        1.0  # API request warning threshold in seconds
    )
    API_REQUEST_CRITICAL_THRESHOLD: float = (
        5.0  # API request critical threshold in seconds
    )
    OPTION_SELECTION_WARNING_THRESHOLD: float = (
        2.0  # Option selection warning threshold in seconds
    )
    OPTION_SELECTION_CRITICAL_THRESHOLD: float = (
        10.0  # Option selection critical threshold in seconds
    )
    ORDER_EXECUTION_WARNING_THRESHOLD: float = (
        2.0  # Order execution warning threshold in seconds
    )
    ORDER_EXECUTION_CRITICAL_THRESHOLD: float = (
        5.0  # Order execution critical threshold in seconds
    )
    DATA_PROCESSING_WARNING_THRESHOLD: float = (
        1.0  # Data processing warning threshold in seconds
    )
    DATA_PROCESSING_CRITICAL_THRESHOLD: float = (
        5.0  # Data processing critical threshold in seconds
    )
    SCANNING_WARNING_THRESHOLD: float = 5.0  # Scanning warning threshold in seconds
    SCANNING_CRITICAL_THRESHOLD: float = 20.0  # Scanning critical threshold in seconds
    CPU_WARNING_THRESHOLD: float = 80.0  # CPU usage warning threshold in percentage
    CPU_CRITICAL_THRESHOLD: float = 95.0  # CPU usage critical threshold in percentage
    MEMORY_WARNING_THRESHOLD: float = (
        80.0  # Memory usage warning threshold in percentage
    )
    MEMORY_CRITICAL_THRESHOLD: float = (
        95.0  # Memory usage critical threshold in percentage
    )
    ENABLE_RESOURCE_MONITORING: bool = True  # Enable resource monitoring
    RESOURCE_MONITORING_INTERVAL: int = 30  # Resource monitoring interval in seconds

    # Error Handling Parameters
    ERROR_THRESHOLD: int = 3  # Number of errors before elevated alerting
    MAX_RECOVERY_ATTEMPTS: int = 2  # Maximum recovery attempts per error
    CIRCUIT_BREAKER_THRESHOLD: int = (
        5  # Number of errors before tripping circuit breaker
    )
    CIRCUIT_BREAKER_MINUTES: int = 30  # Minutes to keep circuit breaker tripped
    INCLUDE_STACK_TRACE_IN_ALERTS: bool = True  # Include stack traces in alert messages

    # Alerting Configuration
    ALERT_LEVELS: Optional[List[str]] = None  # Will be set in __post_init__
    SEVERITY_CHANNELS: Optional[
        Dict[str, List[str]]
    ] = None  # Will be set in __post_init__
    USE_EMAIL_ALERTS: bool = True
    USE_SMS_ALERTS: bool = False
    USE_SLACK_ALERTS: bool = True

    # Email Alert Settings
    EMAIL_SETTINGS: Optional[Dict[str, Any]] = None  # Will be set in __post_init__

    # SMS Alert Settings
    SMS_SETTINGS: Optional[Dict[str, Any]] = None  # Will be set in __post_init__

    # Slack Alert Settings
    SLACK_SETTINGS: Optional[Dict[str, Any]] = None  # Will be set in __post_init__

    # IBKR API Settings
    IBKR_HOST: str = "127.0.0.1"
    IBKR_PORT: int = 7497  # 7496 for Gateway, 7497 for TWS
    IBKR_CLIENT_ID: int = 1
    IBKR_ACCOUNT_ID: str = ""  # Set in config.yaml or via environment

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "auto_trader.log"

    def __post_init__(self) -> None:
        """Initialize complex default values that can't be set as default class attributes."""
        # Set up default alert levels if not provided
        if self.ALERT_LEVELS is None:
            self.ALERT_LEVELS = ["INFO", "WARNING", "HIGH", "CRITICAL"]

        # Set up default severity channels if not provided
        if self.SEVERITY_CHANNELS is None:
            self.SEVERITY_CHANNELS = {
                "INFO": ["email"],
                "WARNING": ["email", "slack"],
                "HIGH": ["email", "slack", "sms"],
                "CRITICAL": ["email", "slack", "sms"],
            }

        # Set up default email settings if not provided
        if self.EMAIL_SETTINGS is None:
            self.EMAIL_SETTINGS = {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "",
                "to_addresses": [],
            }

        # Set up default SMS settings if not provided
        if self.SMS_SETTINGS is None:
            self.SMS_SETTINGS = {
                "service": "email",  # email or api
                "api_key": "",
                "api_url": "",
                "phone_numbers": [],
                "email_settings": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_address": "",
                    "to_addresses": [],
                },
            }

        # Set up default Slack settings if not provided
        if self.SLACK_SETTINGS is None:
            self.SLACK_SETTINGS = {
                "webhook_url": "",
                "channel": "#alerts",
                "username": "Trading Bot",
            }

    @classmethod
    def from_yaml(cls, yaml_file: str) -> "Config":
        """Load configuration from a YAML file.

        Args:
            yaml_file: Path to the YAML configuration file

        Returns:
            Config object with values from YAML file
        """
        # Start with default values
        config = cls()

        try:
            if os.path.exists(yaml_file):
                with open(yaml_file, "r") as f:
                    yaml_config = yaml.safe_load(f)

                # Update attributes from YAML
                if yaml_config:
                    for key, value in yaml_config.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
        except Exception as e:
            print(f"Error loading config from {yaml_file}: {str(e)}")

        # Override with environment variables if they exist
        for field_name in dir(config):
            # Skip private and special fields
            if field_name.startswith("_") or not field_name.isupper():
                continue

            # Check if environment variable exists
            env_var = os.environ.get(field_name)
            if env_var is not None:
                # Convert to the right type
                field_type = type(getattr(config, field_name))
                try:
                    if field_type == bool:
                        value = env_var.lower() in ("true", "yes", "1")
                    else:
                        value = field_type(env_var)
                    setattr(config, field_name, value)
                except ValueError:
                    print(
                        f"Error converting environment variable {field_name}={env_var} to {field_type}"
                    )

        return config


# Create a global app config instance
config = Config()
