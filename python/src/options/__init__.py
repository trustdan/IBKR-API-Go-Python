"""
Options package for enhanced option spread trading.

This package contains modules for filtering and managing option spreads
with greater fidelity based on the parameters described in greater-fidelity.md.
"""

from src.options.spread_filter import OptionSpreadFilter
from src.options.spread_manager import SpreadManager

__all__ = ["OptionSpreadFilter", "SpreadManager"]
