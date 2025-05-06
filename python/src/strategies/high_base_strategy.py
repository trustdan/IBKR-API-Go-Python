import pandas as pd
from typing import List, Tuple, Dict, Any

from ..utils.logger import log_debug, log_info
from .base_strategy import BaseStrategy


class HighBaseStrategy(BaseStrategy):
    """
    High Base Strategy: Looks for stocks trading at relatively high prices compared to their
    historical volatility (measured by ATR), combined with strong momentum (RSI).
    
    This strategy searches for potential long entries in strong stocks that have been
    building a high base and are likely to continue their uptrend.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the High Base Strategy.
        
        Args:
            config: Dictionary containing strategy parameters
        """
        super().__init__(config)
        # Extract strategy-specific parameters
        self.max_atr_ratio = config.get("HIGH_BASE_MAX_ATR_RATIO", 2.0)
        self.min_rsi = config.get("HIGH_BASE_MIN_RSI", 60)
        
    def generate_signals(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Generate trading signals based on high base criteria.
        
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
        
        log_debug(f"Evaluating High Base Strategy for {symbol}")
        
        # Check for required indicators
        if 'ATR14' not in df.columns or 'RSI14' not in df.columns:
            log_info(f"Missing required indicators for {symbol}")
            return signals
            
        # Strategy logic:
        # 1. Price is high relative to ATR (price > ATR * max_atr_ratio)
        # 2. Strong momentum indicated by high RSI (RSI > min_rsi)
        # 3. Optionally, price is above key moving averages
        
        # Check if price is high relative to ATR
        # This indicates the stock is trading at a relatively high level compared to its volatility
        price_to_atr_ratio = latest['close'] / latest['ATR14'] if latest['ATR14'] > 0 else 0
        
        # Check RSI for momentum confirmation
        rsi_above_threshold = latest['RSI14'] > self.min_rsi
        
        # Additional confirmation: price above moving averages
        above_sma50 = latest['close'] > latest['SMA50'] if 'SMA50' in df.columns else True
        above_sma200 = latest['close'] > latest['SMA200'] if 'SMA200' in df.columns else True
        
        # Generate signal if conditions are met
        if (price_to_atr_ratio > self.max_atr_ratio and 
            rsi_above_threshold and 
            above_sma50 and 
            above_sma200):
            
            log_info(f"High Base signal generated for {symbol}. "
                     f"Price/ATR: {price_to_atr_ratio:.2f}, RSI: {latest['RSI14']:.2f}")
            signals.append(("LONG", symbol))
        
        return signals 