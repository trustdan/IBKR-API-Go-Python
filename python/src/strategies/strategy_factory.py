from typing import Dict, Optional, Type

from ..utils.logger import log_debug, log_error
from .base_strategy import BaseStrategy


class StrategyFactory:
    """
    Factory class for creating and retrieving trading strategies.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the strategy factory.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.strategies = {}
        self._register_strategies()
        
    def _register_strategies(self) -> None:
        """Register all available strategies."""
        # Import strategies here to avoid circular imports
        from .high_base_strategy import HighBaseStrategy
        from .low_base_strategy import LowBaseStrategy
        from .bull_pullback_strategy import BullPullbackStrategy
        from .bear_rally_strategy import BearRallyStrategy
        
        # Map of strategy identifiers to strategy classes
        strategy_classes = {
            "HIGH_BASE": HighBaseStrategy,
            "LOW_BASE": LowBaseStrategy,
            "BULL_PULLBACK": BullPullbackStrategy,
            "BEAR_RALLY": BearRallyStrategy
        }
        
        # Initialize all strategies with config
        for strategy_id, strategy_class in strategy_classes.items():
            try:
                self.strategies[strategy_id] = strategy_class(self.config)
                log_debug(f"Registered strategy: {strategy_id}")
            except Exception as e:
                log_error(f"Failed to register strategy {strategy_id}", str(e))
                
    def get_strategy(self, strategy_id: str) -> Optional[BaseStrategy]:
        """
        Get a strategy by its identifier.
        
        Args:
            strategy_id: Identifier of the strategy
            
        Returns:
            Strategy instance or None if not found
        """
        if strategy_id not in self.strategies:
            log_error(f"Strategy not found: {strategy_id}")
            return None
            
        return self.strategies[strategy_id]
        
    def get_all_strategies(self) -> Dict[str, BaseStrategy]:
        """
        Get all registered strategies.
        
        Returns:
            Dictionary of strategy identifiers to strategy instances
        """
        return self.strategies.copy()
        
    def get_strategy_ids(self) -> list:
        """
        Get list of all registered strategy identifiers.
        
        Returns:
            List of strategy identifiers
        """
        return list(self.strategies.keys()) 