"""
Option spread management module.

This module provides the necessary logic to create, filter, and manage option spreads
based on the enhanced configuration settings.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from src.config.config import config
from src.options.spread_filter import OptionSpreadFilter

logger = logging.getLogger(__name__)


class SpreadManager:
    """
    Manager class for option spread creation and filtering.

    Integrates the enhanced spread filter with the application flow and provides
    a clean interface for generating and filtering option spreads.
    """

    def __init__(self):
        """Initialize the SpreadManager."""
        self._options_config = config.get("options", {})
        self._filter = OptionSpreadFilter(self._options_config)

    def reload_config(self):
        """Reload configuration settings."""
        self._options_config = config.get("options", {})
        self._filter = OptionSpreadFilter(self._options_config)
        logger.info("Spread manager configuration reloaded")

    def get_spread_candidates(
        self, symbol: str, option_chains: Dict, underlying_data: Dict
    ) -> Dict[str, List[Dict]]:
        """
        Generate and filter option spread candidates for a given symbol.

        Args:
            symbol: Stock symbol
            option_chains: Dictionary containing option chain data
            underlying_data: Dictionary containing underlying stock data

        Returns:
            Dictionary mapping strategy types to lists of filtered spread candidates
        """
        results = {}

        # Get current price of the underlying
        current_price = underlying_data.get("price", 0)
        if current_price <= 0:
            logger.warning(f"Invalid price for {symbol}: {current_price}")
            return results

        # Process each spread type
        for spread_type in ["BULL_PUT_SPREAD", "BEAR_CALL_SPREAD"]:
            # First select appropriate strikes based on our configuration
            spreads = self._filter.select_strikes(
                option_chains, current_price, spread_type
            )
            logger.info(
                f"Generated {len(spreads)} {spread_type} candidates for {symbol}"
            )

            # Then apply all filters
            filtered_spreads = self._filter.filter_spreads(spreads, underlying_data)
            logger.info(
                f"Filtered to {len(filtered_spreads)} {spread_type} spreads for {symbol}"
            )

            results[spread_type] = filtered_spreads

        return results

    def rank_spreads(self, spreads: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Rank spreads across all strategy types by reward/risk ratio.

        Args:
            spreads: Dictionary mapping strategy types to lists of spread candidates

        Returns:
            Combined list of spreads ranked by reward/risk ratio
        """
        # Combine all spreads into a single list
        all_spreads = []
        for strategy_type, strategy_spreads in spreads.items():
            for spread in strategy_spreads:
                spread["strategy"] = strategy_type
                all_spreads.append(spread)

        # Sort by reward/risk ratio (descending)
        ranked_spreads = sorted(
            all_spreads, key=lambda x: x.get("reward_risk", 0), reverse=True
        )

        return ranked_spreads

    def get_best_spread(
        self, symbol: str, option_chains: Dict, underlying_data: Dict
    ) -> Optional[Dict]:
        """
        Get the best option spread for a given symbol.

        Args:
            symbol: Stock symbol
            option_chains: Dictionary containing option chain data
            underlying_data: Dictionary containing underlying stock data

        Returns:
            Best option spread or None if no valid spreads found
        """
        # Get all spread candidates
        spread_candidates = self.get_spread_candidates(
            symbol, option_chains, underlying_data
        )

        # Rank the spreads
        ranked_spreads = self.rank_spreads(spread_candidates)

        # Return the best spread (if any)
        return ranked_spreads[0] if ranked_spreads else None
