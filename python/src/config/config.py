"""
Configuration module for IBKR Auto Vertical Spread Trader.
Loads settings from YAML files and environment variables.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize configuration from YAML file and environment variables.

        Args:
            config_path: Path to configuration YAML file. If None, uses default.
        """
        self.config_data: Dict[str, Any] = {}

        # Default config path
        if config_path is None:
            config_path = os.getenv("CONFIG_PATH", "config/config.yaml")

        self.config_path = Path(config_path)
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            print(f"Warning: Config file {self.config_path} not found. Using defaults.")
            return

        try:
            with open(self.config_path, "r") as file:
                self.config_data = yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key, supports dot notation for nested values
            default: Default value if key is not found

        Returns:
            Configuration value or default
        """
        # Check environment variable first (with upper case and underscores)
        env_key = key.upper().replace(".", "_")
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # If not in environment, check config file
        keys = key.split(".")
        value = self.config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def __getattr__(self, name: str) -> Any:
        """Allow accessing config values as attributes."""
        return self.get(name)


# Create a global config instance
config = Config()
