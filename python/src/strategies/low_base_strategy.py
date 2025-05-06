import pandas as pd
from typing import List, Tuple, Dict, Any

from ..utils.logger import log_debug, log_info
from .base_strategy import BaseStrategy


class LowBaseStrategy(BaseStrategy):
    """
    Low Base Strategy: Looks for stocks trading at relatively low prices compared to their
    historical volatility (measured by ATR), combined with weak momentum (RSI).
    
    This strategy searches for potential short entries in weak stocks that have been
    forming a low base and are likely to continue their downtrend.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Low Base Strategy.
        
        Args:
            config: Dictionary containing strategy parameters
        """
        super().__init__(config)
        # Extract strategy-specific parameters
        self.min_atr_ratio = config.get("LOW_BASE_MIN_ATR_RATIO", 0.5)
        self.max_rsi = config.get("LOW_BASE_MAX_RSI", 40)
        
    def generate_signals(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Generate trading signals based on low base criteria.
        
        Args:
            df: DataFrame with price data and indicators
            
        Returns:
            List of (signal_type, symbol) tuples
        """
        signals = []
        
        # Need at least one row of data
        if df.empty:
            return signals
            
        # Get the most recent data point
        latest = df.iloc[-1]
        symbol = latest.get('symbol', 'UNKNOWN')
        
        log_debug(f"Evaluating Low Base Strategy for {symbol}")
        
        # Check for required indicators
        if 'ATR14' not in df.columns or 'RSI14' not in df.columns:
            log_info(f"Missing required indicators for {symbol}")
            return signals
            
        # Strategy logic:
        # 1. Price is low relative to ATR (price < ATR * min_atr_ratio)
        # 2. Weak momentum indicated by low RSI (RSI < max_rsi)
        # 3. Optionally, price is below key moving averages
        
        # Check if price is low relative to ATR
        # This indicates the stock is trading at a relatively low level compared to its volatility
        price_to_atr_ratio = latest['close'] / latest['ATR14'] if latest['ATR14'] > 0 else float('inf')
        
        # Check RSI for momentum confirmation
        rsi_below_threshold = latest['RSI14'] < self.max_rsi
        
        # Additional confirmation: price below moving averages
        below_sma50 = latest['close'] < latest['SMA50'] if 'SMA50' in df.columns else True
        below_sma200 = latest['close'] < latest['SMA200'] if 'SMA200' in df.columns else True
        
        # Generate signal if conditions are met
        if (price_to_atr_ratio < self.min_atr_ratio and 
            rsi_below_threshold and 
            below_sma50 and 
            below_sma200):
            
            log_info(f"Low Base signal generated for {symbol}. "
                     f"Price/ATR: {price_to_atr_ratio:.2f}, RSI: {latest['RSI14']:.2f}")
            signals.append(("SHORT", symbol))
        
        return signals 