from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from src.strategies.base_strategy import BaseStrategy

class BacktestEngine:
    config: Dict[str, Any]
    data_manager: Any
    strategy_factory: Any
    results: Dict[str, Any]

    def __init__(self, config: Dict[str, Any], data_manager: Any = None) -> None: ...
    def run_backtest(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        strategy_ids: Optional[List[str]] = None,
        initial_equity: Optional[float] = None,
    ) -> Dict[str, Any]: ...
    def _backtest_symbol_strategy(
        self,
        symbol: str,
        strategy_id: str,
        strategy: BaseStrategy,
        data: pd.DataFrame,
        initial_equity: float,
    ) -> List[Dict[str, Any]]: ...
    def _calculate_equity_curve(
        self, trades: List[Dict[str, Any]], initial_equity: float
    ) -> pd.Series: ...
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float: ...
    def generate_report(self, output_file: Optional[str] = None) -> str: ...
