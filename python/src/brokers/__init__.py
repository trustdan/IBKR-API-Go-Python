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
