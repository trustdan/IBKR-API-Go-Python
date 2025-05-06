import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from ..utils.logger import log_info, log_debug, log_error
from ..strategies.base_strategy import BaseStrategy
from ..strategies.strategy_factory import StrategyFactory


class BacktestEngine:
    """
    Basic backtesting engine for evaluating trading strategies on historical data.
    """
    
    def __init__(self, config: Dict[str, Any], data_manager=None):
        """
        Initialize the backtest engine.
        
        Args:
            config: Configuration dictionary
            data_manager: Optional DataManager instance for fetching market data
        """
        self.config = config
        self.data_manager = data_manager
        self.strategy_factory = StrategyFactory(config)
        self.results = {}
        
    def run_backtest(self, 
                     symbols: List[str], 
                     start_date: str, 
                     end_date: str, 
                     strategy_ids: List[str] = None,
                     initial_equity: float = None) -> Dict[str, Any]:
        """
        Run a backtest for the specified symbols, date range, and strategies.
        
        Args:
            symbols: List of symbols to test
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            strategy_ids: List of strategy IDs to test (None for all)
            initial_equity: Initial equity for the backtest
            
        Returns:
            Dictionary of backtest results
        """
        if self.data_manager is None:
            log_error("Cannot run backtest without a DataManager")
            return {}
            
        # Set default values if not provided
        if initial_equity is None:
            initial_equity = self.config.get("INITIAL_EQUITY", 100000)
            
        if strategy_ids is None:
            strategy_ids = self.strategy_factory.get_strategy_ids()
            
        log_info(f"Running backtest for {len(symbols)} symbols from {start_date} to {end_date}")
        log_debug(f"Testing strategies: {strategy_ids}")
        
        # Get strategy instances
        strategies = []
        for strategy_id in strategy_ids:
            strategy = self.strategy_factory.get_strategy(strategy_id)
            if strategy:
                strategies.append((strategy_id, strategy))
                
        # Initialize results structure
        results = {
            'overall': {
                'initial_equity': initial_equity,
                'final_equity': initial_equity,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'total_profit': 0.0,
                'max_drawdown': 0.0
            },
            'strategies': {},
            'symbols': {},
            'trades': []
        }
        
        # Initialize per-strategy results
        for strategy_id, _ in strategies:
            results['strategies'][strategy_id] = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'total_profit': 0.0
            }
            
        # Run backtest for each symbol
        for symbol in symbols:
            try:
                # Get historical data for the symbol
                data = self.data_manager.get_data(symbol, "daily", start_date, end_date)
                
                if data is None or data.empty:
                    log_debug(f"No data available for {symbol}")
                    continue
                    
                # Add symbol column if not present
                if 'symbol' not in data.columns:
                    data['symbol'] = symbol
                    
                # Initialize symbol results
                results['symbols'][symbol] = {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0.0,
                    'avg_win': 0.0,
                    'avg_loss': 0.0,
                    'total_profit': 0.0
                }
                
                # Backtest each strategy for this symbol
                for strategy_id, strategy in strategies:
                    symbol_trades = self._backtest_symbol_strategy(
                        symbol, strategy_id, strategy, data, initial_equity
                    )
                    
                    # Add trades to results
                    results['trades'].extend(symbol_trades)
                    
                    # Update symbol stats
                    results['symbols'][symbol]['total_trades'] += len(symbol_trades)
                    winning_trades = [t for t in symbol_trades if t['pnl'] > 0]
                    losing_trades = [t for t in symbol_trades if t['pnl'] <= 0]
                    
                    results['symbols'][symbol]['winning_trades'] += len(winning_trades)
                    results['symbols'][symbol]['losing_trades'] += len(losing_trades)
                    
                    if symbol_trades:
                        results['symbols'][symbol]['win_rate'] = len(winning_trades) / len(symbol_trades)
                        
                    if winning_trades:
                        results['symbols'][symbol]['avg_win'] = sum(t['pnl'] for t in winning_trades) / len(winning_trades)
                        
                    if losing_trades:
                        results['symbols'][symbol]['avg_loss'] = sum(t['pnl'] for t in losing_trades) / len(losing_trades)
                        
                    results['symbols'][symbol]['total_profit'] += sum(t['pnl'] for t in symbol_trades)
                    
                    # Update strategy stats
                    results['strategies'][strategy_id]['total_trades'] += len(symbol_trades)
                    results['strategies'][strategy_id]['winning_trades'] += len(winning_trades)
                    results['strategies'][strategy_id]['losing_trades'] += len(losing_trades)
                    
                    if results['strategies'][strategy_id]['total_trades'] > 0:
                        results['strategies'][strategy_id]['win_rate'] = (
                            results['strategies'][strategy_id]['winning_trades'] / 
                            results['strategies'][strategy_id]['total_trades']
                        )
                    
                    strategy_profits = sum(t['pnl'] for t in symbol_trades)
                    results['strategies'][strategy_id]['total_profit'] += strategy_profits
                    
            except Exception as e:
                log_error(f"Error backtesting {symbol}: {str(e)}")
                
        # Calculate overall results
        trades = results['trades']
        total_trades = len(trades)
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        
        results['overall']['total_trades'] = total_trades
        results['overall']['winning_trades'] = len(winning_trades)
        results['overall']['losing_trades'] = len(losing_trades)
        
        if total_trades > 0:
            results['overall']['win_rate'] = len(winning_trades) / total_trades
            
        if winning_trades:
            results['overall']['avg_win'] = sum(t['pnl'] for t in winning_trades) / len(winning_trades)
            
        if losing_trades:
            results['overall']['avg_loss'] = sum(t['pnl'] for t in losing_trades) / len(losing_trades)
            
        # Calculate profit factor
        total_gain = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
        total_loss = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 0
        
        if total_loss > 0:
            results['overall']['profit_factor'] = total_gain / total_loss
        else:
            results['overall']['profit_factor'] = float('inf') if total_gain > 0 else 0
            
        results['overall']['total_profit'] = sum(t['pnl'] for t in trades)
        results['overall']['final_equity'] = initial_equity + results['overall']['total_profit']
        
        # Calculate max drawdown (simplified)
        equity_curve = self._calculate_equity_curve(trades, initial_equity)
        results['overall']['max_drawdown'] = self._calculate_max_drawdown(equity_curve)
        results['equity_curve'] = equity_curve
        
        log_info(f"Backtest completed with {total_trades} trades")
        log_info(f"Final equity: ${results['overall']['final_equity']:.2f}")
        log_info(f"Win rate: {results['overall']['win_rate']*100:.2f}%")
        
        self.results = results
        return results
        
    def _backtest_symbol_strategy(self, 
                                 symbol: str, 
                                 strategy_id: str,
                                 strategy: BaseStrategy, 
                                 data: pd.DataFrame,
                                 initial_equity: float) -> List[Dict]:
        """
        Backtest a single strategy on a single symbol.
        
        Args:
            symbol: Symbol to test
            strategy_id: Strategy identifier
            strategy: Strategy instance
            data: Historical price data
            initial_equity: Initial equity
            
        Returns:
            List of trade dictionaries
        """
        trades = []
        
        # Add indicators to the data
        data_with_indicators = strategy.compute_indicators(data)
        
        # Set a fake current position to None (not in a trade)
        current_position = None
        
        # Process each day in the data
        for i in range(1, len(data_with_indicators)):
            day = data_with_indicators.iloc[i]
            prev_day = data_with_indicators.iloc[i-1]
            current_date = day.name if isinstance(day.name, datetime) else pd.to_datetime(day.name)
            
            # Set a fake time to check execution window (3 PM ET)
            fake_time = current_date.replace(hour=15, minute=0)
            
            # If no position, check for entry signal
            if current_position is None:
                # Check if this day has a signal
                if strategy.should_execute(fake_time):
                    # Create a DataFrame slice with just the current day for signal generation
                    current_slice = data_with_indicators.iloc[i:i+1]
                    signals = strategy.generate_signals(current_slice)
                    
                    # If we have a signal, enter a position
                    if signals:
                        signal_type, _ = signals[0]
                        
                        # Simple position sizing: use 2% risk per trade
                        risk_pct = self.config.get("RISK_PER_TRADE", 0.02)
                        position_size = initial_equity * risk_pct / day['ATR14'] if day['ATR14'] > 0 else 0
                        
                        # Create the position
                        current_position = {
                            'symbol': symbol,
                            'strategy': strategy_id,
                            'entry_date': current_date,
                            'entry_price': day['close'],
                            'direction': signal_type,
                            'size': position_size
                        }
            
            # If in a position, check for exit conditions
            elif current_position is not None:
                # For this simple backtest, use fixed holding period of 10 days
                # or exit on reversal signal or stop loss
                holding_days = (current_date - current_position['entry_date']).days
                max_holding_period = self.config.get("MAX_HOLDING_PERIOD", 10)
                
                # Check for stop loss (2 ATR from entry)
                stop_loss_atr_mult = self.config.get("STOP_LOSS_ATR_MULT", 2.0)
                atr_at_entry = prev_day['ATR14']
                
                stop_price = None
                if current_position['direction'] == "LONG":
                    stop_price = current_position['entry_price'] - (atr_at_entry * stop_loss_atr_mult)
                    stop_hit = day['low'] <= stop_price
                else:  # SHORT
                    stop_price = current_position['entry_price'] + (atr_at_entry * stop_loss_atr_mult)
                    stop_hit = day['high'] >= stop_price
                
                # Check for exit conditions
                exit_signal = False
                if strategy.should_execute(fake_time):
                    # Check for reversal signal
                    current_slice = data_with_indicators.iloc[i:i+1]
                    signals = strategy.generate_signals(current_slice)
                    
                    # Exit if signal in opposite direction
                    if signals and signals[0][0] != current_position['direction']:
                        exit_signal = True
                        
                # Exit if max holding period reached, stop loss hit, or reversal signal
                if holding_days >= max_holding_period or stop_hit or exit_signal:
                    # Calculate P&L
                    exit_price = day['close']
                    if stop_hit:
                        # Use stop price if stop was hit
                        exit_price = stop_price
                    
                    if current_position['direction'] == "LONG":
                        pnl = (exit_price - current_position['entry_price']) * current_position['size']
                    else:  # SHORT
                        pnl = (current_position['entry_price'] - exit_price) * current_position['size']
                        
                    # Record the trade
                    trade = {
                        'symbol': symbol,
                        'strategy': strategy_id,
                        'entry_date': current_position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': current_position['entry_price'],
                        'exit_price': exit_price,
                        'direction': current_position['direction'],
                        'size': current_position['size'],
                        'pnl': pnl,
                        'holding_days': holding_days,
                        'exit_reason': 'stop_loss' if stop_hit else ('max_holding' if holding_days >= max_holding_period else 'reversal')
                    }
                    trades.append(trade)
                    
                    # Reset position
                    current_position = None
        
        return trades
        
    def _calculate_equity_curve(self, trades: List[Dict], initial_equity: float) -> pd.Series:
        """
        Calculate the equity curve from a list of trades.
        
        Args:
            trades: List of trade dictionaries
            initial_equity: Initial equity
            
        Returns:
            Pandas Series with equity values indexed by date
        """
        if not trades:
            return pd.Series([initial_equity], index=[datetime.now()])
            
        # Sort trades by exit date
        sorted_trades = sorted(trades, key=lambda x: x['exit_date'])
        
        # Create a dictionary to store equity by date
        equity_by_date = defaultdict(float)
        equity_by_date[sorted_trades[0]['entry_date'] - timedelta(days=1)] = initial_equity
        
        # Add each trade's P&L to the equity curve
        current_equity = initial_equity
        for trade in sorted_trades:
            current_equity += trade['pnl']
            equity_by_date[trade['exit_date']] = current_equity
            
        # Convert to Series
        dates = sorted(equity_by_date.keys())
        values = [equity_by_date[date] for date in dates]
        
        return pd.Series(values, index=dates)
        
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown from an equity curve.
        
        Args:
            equity_curve: Pandas Series with equity values
            
        Returns:
            Maximum drawdown as a percentage
        """
        # Calculate drawdown series
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        
        return abs(drawdown.min()) if not drawdown.empty else 0.0
        
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a text report from the backtest results.
        
        Args:
            output_file: Optional file path to write the report
            
        Returns:
            Report string
        """
        if not self.results:
            return "No backtest results available."
            
        report = []
        report.append("=== BACKTEST REPORT ===")
        report.append("")
        
        # Overall results
        overall = self.results['overall']
        report.append("Overall Performance:")
        report.append(f"Initial Equity: ${overall['initial_equity']:.2f}")
        report.append(f"Final Equity: ${overall['final_equity']:.2f}")
        report.append(f"Total Profit: ${overall['total_profit']:.2f} "
                     f"({overall['total_profit']/overall['initial_equity']*100:.2f}%)")
        report.append(f"Max Drawdown: {overall['max_drawdown']*100:.2f}%")
        report.append(f"Profit Factor: {overall['profit_factor']:.2f}")
        report.append(f"Win Rate: {overall['win_rate']*100:.2f}% "
                     f"({overall['winning_trades']}/{overall['total_trades']})")
        
        if overall['winning_trades'] > 0:
            report.append(f"Average Win: ${overall['avg_win']:.2f}")
        if overall['losing_trades'] > 0:
            report.append(f"Average Loss: ${overall['avg_loss']:.2f}")
            
        report.append("")
        
        # Strategy performance
        report.append("Strategy Performance:")
        for strategy_id, stats in self.results['strategies'].items():
            if stats['total_trades'] > 0:
                report.append(f"  {strategy_id}:")
                report.append(f"    Win Rate: {stats['win_rate']*100:.2f}% "
                             f"({stats['winning_trades']}/{stats['total_trades']})")
                report.append(f"    Total Profit: ${stats['total_profit']:.2f}")
                
        report.append("")
        
        # Top 5 symbols
        report.append("Top 5 Symbols:")
        symbols_by_profit = sorted(
            self.results['symbols'].items(),
            key=lambda x: x[1]['total_profit'],
            reverse=True
        )[:5]
        
        for symbol, stats in symbols_by_profit:
            if stats['total_trades'] > 0:
                report.append(f"  {symbol}: ${stats['total_profit']:.2f} "
                             f"(Win Rate: {stats['win_rate']*100:.2f}%)")
                
        report.append("")
        
        # Sample trades
        report.append("Sample Trades:")
        sample_trades = sorted(
            self.results['trades'],
            key=lambda x: x['pnl'],
            reverse=True
        )[:5]
        
        for trade in sample_trades:
            report.append(f"  {trade['symbol']} {trade['direction']} - "
                         f"Entry: {trade['entry_date'].strftime('%Y-%m-%d')} "
                         f"@ ${trade['entry_price']:.2f}, "
                         f"Exit: {trade['exit_date'].strftime('%Y-%m-%d')} "
                         f"@ ${trade['exit_price']:.2f}, "
                         f"P&L: ${trade['pnl']:.2f}")
                
        report_text = "\n".join(report)
        
        # Write to file if requested
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(report_text)
            except Exception as e:
                log_error(f"Error writing backtest report: {str(e)}")
                
        return report_text 