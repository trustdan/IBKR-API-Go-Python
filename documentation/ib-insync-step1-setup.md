# IB Insync Implementation: Step 1 - Setup and Initial Structure

## Introduction

This guide covers the initial setup and structure for implementing the ib_insync library as a replacement for our current placeholder Interactive Brokers API implementation.

## Prerequisites

- Python 3.9+
- Access to IBKR Trader Workstation (TWS) or IB Gateway
- Paper trading account for testing

## Installation

Install the required dependencies:

```bash
# Core dependencies
pip install ib_insync>=0.9.86 pytz>=2023.3

# Testing dependencies
pip install pytest>=7.4.0 pytest-mock>=3.11.1 pytest-cov>=4.1.0 pytest-bdd>=7.0.0
```

## Update Project Configuration

Add the dependencies to your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = "^3.9"
ib_insync = "^0.9.86"
pytz = "^2023.3"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
pytest-mock = "^3.11.1"
pytest-cov = "^4.1.0"
pytest-bdd = "^7.0.0"
```

## Create the ib_insync Wrapper Class

Create a new file at `src/brokers/ibkr_ib_insync.py` with the basic structure:

```python
from typing import Any, Dict, List, Optional, Tuple
import threading
import time
from datetime import datetime, date

from ib_insync import IB, util
from ib_insync import Contract, Stock, Option as IBOption, ComboLeg, TagValue
from ib_insync import Order, LimitOrder, MarketOrder
from ib_insync import Ticker, Trade, Position as IBPosition
import pytz

from src.app.config import Config
from src.models.option import Option, OptionSpread
from src.utils.logger import log_debug, log_error, log_info, log_warning


class IBKRIBInsyncApi:
    """Implementation of IBKR API using ib_insync library."""
    
    def __init__(self, config: Config):
        """Initialize the IBKR API client.

        Args:
            config: Application configuration
        """
        self.config = config
        self.connected = False
        
        # Connection details
        self.host = config.IBKR_HOST if hasattr(config, "IBKR_HOST") else "127.0.0.1"
        self.port = config.IBKR_PORT if hasattr(config, "IBKR_PORT") else 7497
        self.client_id = config.IBKR_CLIENT_ID if hasattr(config, "IBKR_CLIENT_ID") else 1
        self.account_id = config.IBKR_ACCOUNT_ID if hasattr(config, "IBKR_ACCOUNT_ID") else ""
        self.read_only = config.IBKR_READ_ONLY if hasattr(config, "IBKR_READ_ONLY") else False
        
        # Create IB instance
        self.ib = IB()
        
        # Order tracking
        self.next_order_id = 1
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.positions: Dict[str, Dict[str, Any]] = {}

        # Lock for thread safety
        self.lock = threading.Lock()
```

## Update the Factory Method in `__init__.py`

Modify `src/brokers/__init__.py` to include our new implementation:

```python
"""
Brokers module for interacting with various trading platforms.
"""

from src.brokers.ibkr_api import IBKRApi
from src.brokers.ibkr_ib_insync import IBKRIBInsyncApi

def get_broker_api(config, use_ib_insync=True):
    """Factory method to get the appropriate broker API implementation.
    
    Args:
        config: Application configuration
        use_ib_insync: Whether to use the ib_insync implementation
        
    Returns:
        An instance of the appropriate broker API
    """
    if use_ib_insync:
        return IBKRIBInsyncApi(config)
    else:
        return IBKRApi(config)

__all__ = ["IBKRApi", "IBKRIBInsyncApi", "get_broker_api"]
```

## Update Configuration in `config.yaml`

Add the following to your configuration file:

```yaml
# IBKR API Connection
ibkr:
  host: "127.0.0.1"
  port: 7497  # TWS: 7497, IB Gateway: 4001
  client_id: 1
  read_only: false
  account: ""  # Set your account ID or leave blank to use active account
  use_ib_insync: true  # Use new implementation instead of placeholder
  timeout: 20  # Connection timeout in seconds
  auto_reconnect: true  # Automatically try to reconnect on disconnection
  max_rate: 45  # Maximum API requests per second (IB's limit is 50)
```

## Next Steps

After completing this setup, proceed to [Step 2](ib-insync-step2-connection.md) to implement the connection management functionality. 