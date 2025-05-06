import datetime
import logging
import multiprocessing
import os
import time
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union, Any

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.optimize import minimize

from python.src.app.config import Config
from python.src.models.option_models import OptionSpread
from python.src.models.trade_models import TradeResult
from python.src.strategies.strategy_factory import StrategyFactory
from python.src.utils.alert_system import AlertSystem

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """Container for backtest results"""
    trades: List[TradeResult]
    equity_curve: pd.Series
    drawdowns: pd.Series
    metrics: Dict[str, Union[float, int]]
    parameters: Dict[str, Any]
    strategy_name: str
    symbols: List[str]
    start_date: str
    end_date: str
    run_id: str = None
    
    def __post_init__(self):
        if self.run_id is None:
            self.run_id = str(uuid.uuid4())[:8]

@dataclass
class OptimizationResult:
    """Container for optimization results"""
    best_parameters: Dict[str, Any]
    all_results: List[BacktestResult]
    optimization_metric: str
    best_value: float
    parameter_ranges: Dict[str, Tuple[float, float]]
    time_taken: float
    strategy_name: str
    symbols: List[str]
    start_date: str
    end_date: str
    run_id: str = None
    
    def __post_init__(self):
        if self.run_id is None:
            self.run_id = str(uuid.uuid4())[:8]
    
    def get_parameter_impact(self) -> Dict[str, List[Tuple[float, float]]]:
        """Calculate the impact of each parameter on the optimization metric"""
        parameter_impact = {}
        
        for param_name in self.parameter_ranges.keys():
            # Extract parameter values and corresponding metric values
            values = []
            for result in self.all_results:
                values.append((
                    result.parameters[param_name],
                    result.metrics.get(self.optimization_metric, 0)
                ))
            
            # Sort by parameter value
            values.sort(key=lambda x: x[0])
            parameter_impact[param_name] = values
        
        return parameter_impact


class BacktestEngine:
    """Engine for running backtests and optimizations"""
    
    def __init__(self, config: Config, alert_system: Optional[AlertSystem] = None):
        self.config = config
        self.alert_system = alert_system
        self.strategy_factory = StrategyFactory()
        self.results_cache = {}  # Cache results to avoid duplicate runs
        
    def run_backtest(
        self, 
        symbols: List[str], 
        start_date: str, 
        end_date: str, 
        strategy_name: str, 
        parameters: Optional[Dict[str, Any]] = None,
        initial_capital: float = None,
        commission_model: str = None,
        data_frequency: str = "daily",
        cache_data: bool = True
    ) -> BacktestResult:
        """
        Run a backtest for a given strategy and parameters
        
        Args:
            symbols: List of symbols to backtest
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            strategy_name: Name of the strategy to test
            parameters: Optional parameters to override default strategy parameters
            initial_capital: Starting capital (defaults to config value)
            commission_model: Commission model to use
            data_frequency: Data frequency to use (daily, minute)
            cache_data: Whether to cache data between runs
            
        Returns:
            BacktestResult containing trades, equity curve, and performance metrics
        """
        start_time = time.time()
        logger.info(f"Starting backtest for {strategy_name} on {symbols} from {start_date} to {end_date}")
        
        # Create cache key for possibly reusing results
        cache_key = f"{','.join(symbols)}_{start_date}_{end_date}_{strategy_name}_{str(parameters)}"
        if cache_key in self.results_cache:
            logger.info(f"Using cached backtest result for {cache_key}")
            return self.results_cache[cache_key]
        
        # Set defaults
        if initial_capital is None:
            initial_capital = self.config.INITIAL_EQUITY
        
        # Get strategy instance
        strategy = self.strategy_factory.get_strategy(strategy_name)
        if not strategy:
            raise ValueError(f"Strategy {strategy_name} not found")
        
        # Override parameters if provided
        if parameters:
            strategy.set_parameters(parameters)
        
        # Get data for all symbols
        all_data = {}
        for symbol in symbols:
            # In a real implementation, this would fetch from a data source
            # For now, generate mock data for demonstration
            all_data[symbol] = self._get_mock_data(symbol, start_date, end_date, data_frequency)
        
        # Run the backtest
        trades = []
        equity_curve = pd.Series(initial_capital, index=[pd.Timestamp(start_date)])
        positions = {}  # Current positions by symbol
        
        # Combine all data and sort by date
        all_dates = sorted(set(date for symbol_data in all_data.values() for date in symbol_data.index))
        
        # Initialize drawdown tracking
        high_watermark = initial_capital
        drawdowns = pd.Series(0.0, index=[pd.Timestamp(start_date)])
        
        # Simulate each day
        current_capital = initial_capital
        for current_date in all_dates:
            if current_date.strftime('%Y-%m-%d') <= start_date:
                continue
                
            # Check for new signals
            for symbol, data in all_data.items():
                if current_date not in data.index:
                    continue
                
                # Skip if we already have a position in this symbol
                if symbol in positions:
                    continue
                
                # Get recent data for the symbol
                recent_data = data[:current_date]
                if len(recent_data) < self.config.MIN_BARS_FOR_ANALYSIS:
                    continue
                
                # Check for signal
                signal = strategy.generate_signal(recent_data)
                if signal and signal.direction:
                    # We have a new signal, simulate trade entry
                    price = data.loc[current_date, 'close']
                    position_size = self._calculate_position_size(current_capital, price)
                    
                    # Create synthetic option spread for the simulation
                    spread = self._create_synthetic_spread(
                        symbol, current_date, signal.direction, 
                        price, strategy.get_parameters()
                    )
                    
                    # Record the trade
                    trade = TradeResult(
                        symbol=symbol,
                        entry_date=current_date,
                        direction=signal.direction,
                        entry_price=spread.cost,
                        quantity=position_size,
                        spread=spread,
                        strategy=strategy_name,
                        stop_price=self._calculate_stop_price(
                            recent_data, signal.direction, 
                            self.config.STOP_LOSS_ATR_MULT
                        )
                    )
                    
                    # Add to positions
                    positions[symbol] = trade
                    
                    # Deduct the cost from capital
                    current_capital -= trade.entry_price * trade.quantity
            
            # Check for exits on existing positions
            for symbol in list(positions.keys()):
                if symbol not in all_data:
                    continue
                    
                data = all_data[symbol]
                if current_date not in data.index:
                    continue
                
                trade = positions[symbol]
                current_price = data.loc[current_date, 'close']
                
                # Check exit conditions
                exit_reason = self._check_exit_conditions(
                    trade, current_price, current_date, data
                )
                
                if exit_reason:
                    # Exit the position
                    exit_price = self._simulate_exit_price(trade, current_price, exit_reason)
                    trade.exit_date = current_date
                    trade.exit_price = exit_price
                    trade.exit_reason = exit_reason
                    
                    # Calculate PnL
                    if trade.direction == "LONG":
                        trade.pnl = (exit_price - trade.entry_price) * trade.quantity
                    else:
                        trade.pnl = (trade.entry_price - exit_price) * trade.quantity
                    
                    # Add trade to results
                    trades.append(trade)
                    
                    # Update capital
                    current_capital += (trade.entry_price + trade.pnl) * trade.quantity
                    
                    # Remove from positions
                    del positions[symbol]
            
            # Update equity curve
            equity_curve[current_date] = current_capital
            
            # Update drawdown
            if current_capital > high_watermark:
                high_watermark = current_capital
            current_drawdown = (high_watermark - current_capital) / high_watermark
            drawdowns[current_date] = current_drawdown
        
        # Close any remaining positions at the last date
        for symbol, trade in positions.items():
            if symbol not in all_data:
                continue
                
            data = all_data[symbol]
            if not data.empty:
                last_date = data.index[-1]
                last_price = data.loc[last_date, 'close']
                
                trade.exit_date = last_date
                trade.exit_price = last_price
                trade.exit_reason = "END_OF_PERIOD"
                
                # Calculate PnL
                if trade.direction == "LONG":
                    trade.pnl = (last_price - trade.entry_price) * trade.quantity
                else:
                    trade.pnl = (trade.entry_price - last_price) * trade.quantity
                
                trades.append(trade)
        
        # Calculate metrics
        metrics = self._calculate_performance_metrics(trades, equity_curve, drawdowns)
        
        # Create result
        result = BacktestResult(
            trades=trades,
            equity_curve=equity_curve,
            drawdowns=drawdowns,
            metrics=metrics,
            parameters=strategy.get_parameters(),
            strategy_name=strategy_name,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )
        
        # Cache result for reuse
        self.results_cache[cache_key] = result
        
        logger.info(f"Completed backtest in {time.time() - start_time:.2f}s with {len(trades)} trades")
        return result
        
    def run_optimization(
        self,
        symbols: List[str], 
        start_date: str, 
        end_date: str, 
        strategy_name: str,
        parameter_ranges: Dict[str, Tuple[float, float]],
        optimization_metric: str = "sharpe_ratio",
        method: str = "grid_search",
        n_iterations: int = 100,
        n_jobs: int = -1,
        **kwargs
    ) -> OptimizationResult:
        """
        Optimize strategy parameters through backtesting
        
        Args:
            symbols: List of symbols to backtest
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            strategy_name: Name of the strategy to test
            parameter_ranges: Dict of parameter names and their (min, max) ranges
            optimization_metric: Metric to optimize (e.g., "sharpe_ratio", "profit_factor")
            method: Optimization method ("grid_search", "random_search", "bayesian", "differential_evolution")
            n_iterations: Number of iterations or grid points per dimension
            n_jobs: Number of parallel jobs (-1 for all available cores)
            
        Returns:
            OptimizationResult with best parameters and all tested results
        """
        start_time = time.time()
        logger.info(f"Starting parameter optimization for {strategy_name} on {symbols}")
        
        # Handle n_jobs
        if n_jobs == -1:
            n_jobs = multiprocessing.cpu_count()
        
        all_results = []
        
        if method == "grid_search":
            # Generate grid of parameters
            param_grid = self._generate_parameter_grid(parameter_ranges, n_iterations)
            
            # Run parallel backtests
            all_results = Parallel(n_jobs=n_jobs)(
                delayed(self.run_backtest)(
                    symbols=symbols,
                    start_date=start_date,
                    end_date=end_date,
                    strategy_name=strategy_name,
                    parameters=params,
                    **kwargs
                ) for params in param_grid
            )
        
        elif method == "random_search":
            # Generate random parameter sets
            param_sets = self._generate_random_parameters(parameter_ranges, n_iterations)
            
            # Run parallel backtests
            all_results = Parallel(n_jobs=n_jobs)(
                delayed(self.run_backtest)(
                    symbols=symbols,
                    start_date=start_date,
                    end_date=end_date,
                    strategy_name=strategy_name,
                    parameters=params,
                    **kwargs
                ) for params in param_sets
            )
        
        elif method in ["bayesian", "differential_evolution"]:
            # These methods require sequential evaluations, so we'll use
            # scipy.optimize to handle them
            
            # Define the objective function (negative of metric to minimize)
            def objective_func(x):
                # Convert optimization parameters to dictionary
                params = {}
                for i, (param_name, _) in enumerate(parameter_ranges.items()):
                    params[param_name] = x[i]
                
                # Run backtest with these parameters
                result = self.run_backtest(
                    symbols=symbols,
                    start_date=start_date,
                    end_date=end_date,
                    strategy_name=strategy_name,
                    parameters=params,
                    **kwargs
                )
                
                # Store result for later
                all_results.append(result)
                
                # Return negative metric (for minimization)
                metric_value = result.metrics.get(optimization_metric, 0)
                return -metric_value
            
            # Set up bounds for optimization
            bounds = [(min_val, max_val) for _, (min_val, max_val) in parameter_ranges.items()]
            
            # Run optimization
            if method == "differential_evolution":
                from scipy.optimize import differential_evolution
                result = differential_evolution(
                    objective_func, 
                    bounds=bounds,
                    maxiter=n_iterations,
                    popsize=15,
                    workers=n_jobs if n_jobs > 0 else None
                )
            else:  # bayesian
                # For Bayesian optimization, we'll use a popular library
                try:
                    from skopt import gp_minimize
                    result = gp_minimize(
                        objective_func,
                        bounds,
                        n_calls=n_iterations,
                        n_jobs=n_jobs if n_jobs > 0 else 1
                    )
                except ImportError:
                    logger.warning("scikit-optimize not installed, falling back to random search")
                    return self.run_optimization(
                        symbols=symbols,
                        start_date=start_date,
                        end_date=end_date,
                        strategy_name=strategy_name,
                        parameter_ranges=parameter_ranges,
                        optimization_metric=optimization_metric,
                        method="random_search",
                        n_iterations=n_iterations,
                        n_jobs=n_jobs,
                        **kwargs
                    )
        
        else:
            raise ValueError(f"Unsupported optimization method: {method}")
        
        # Find best result
        best_result = None
        best_value = float('-inf')
        
        for result in all_results:
            metric_value = result.metrics.get(optimization_metric, 0)
            if metric_value > best_value:
                best_value = metric_value
                best_result = result
        
        optimization_result = OptimizationResult(
            best_parameters=best_result.parameters if best_result else {},
            all_results=all_results,
            optimization_metric=optimization_metric,
            best_value=best_value,
            parameter_ranges=parameter_ranges,
            time_taken=time.time() - start_time,
            strategy_name=strategy_name,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )
        
        logger.info(f"Completed optimization in {optimization_result.time_taken:.2f}s with {len(all_results)} parameter combinations")
        logger.info(f"Best parameters: {optimization_result.best_parameters}")
        logger.info(f"Best {optimization_metric}: {best_value}")
        
        return optimization_result
    
    def run_multi_strategy_backtest(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        strategies: List[str],
        **kwargs
    ) -> Dict[str, BacktestResult]:
        """
        Run backtests for multiple strategies and compare results
        
        Args:
            symbols: List of symbols to backtest
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            strategies: List of strategy names to test
            
        Returns:
            Dictionary of strategy names to backtest results
        """
        results = {}
        
        for strategy_name in strategies:
            results[strategy_name] = self.run_backtest(
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                strategy_name=strategy_name,
                **kwargs
            )
            
        return results
    
    def save_backtest_result(self, result: BacktestResult, output_dir: str = None) -> str:
        """Save backtest result to disk"""
        if output_dir is None:
            output_dir = os.path.join(
                self.config.OUTPUT_DIR, 
                "backtest_results",
                datetime.datetime.now().strftime("%Y%m%d")
            )
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"{result.strategy_name}_{','.join(result.symbols)}_{result.run_id}.pkl"
        filepath = os.path.join(output_dir, filename)
        
        # Save as pickle
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(result, f)
            
        logger.info(f"Saved backtest result to {filepath}")
        return filepath
    
    def load_backtest_result(self, filepath: str) -> BacktestResult:
        """Load backtest result from disk"""
        import pickle
        with open(filepath, 'rb') as f:
            result = pickle.load(f)
            
        return result
    
    def save_optimization_result(self, result: OptimizationResult, output_dir: str = None) -> str:
        """Save optimization result to disk"""
        if output_dir is None:
            output_dir = os.path.join(
                self.config.OUTPUT_DIR, 
                "optimization_results",
                datetime.datetime.now().strftime("%Y%m%d")
            )
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"opt_{result.strategy_name}_{','.join(result.symbols)}_{result.run_id}.pkl"
        filepath = os.path.join(output_dir, filename)
        
        # Save as pickle
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(result, f)
            
        logger.info(f"Saved optimization result to {filepath}")
        return filepath
        
    def load_optimization_result(self, filepath: str) -> OptimizationResult:
        """Load optimization result from disk"""
        import pickle
        with open(filepath, 'rb') as f:
            result = pickle.load(f)
            
        return result
    
    def _get_mock_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str, 
        data_frequency: str = "daily"
    ) -> pd.DataFrame:
        """Generate mock OHLCV data for testing"""
        # Convert dates to pandas datetime
        start = pd.Timestamp(start_date)
        end = pd.Timestamp(end_date)
        
        # Generate date range
        if data_frequency == "daily":
            dates = pd.date_range(start=start, end=end, freq='B')  # Business days
        elif data_frequency == "minute":
            # Generate 1-minute data for market hours only
            dates = []
            current = start
            while current <= end:
                if current.weekday() < 5:  # Mon-Fri
                    for hour in range(9, 16):  # 9:30 AM to 4:00 PM
                        if hour == 9:
                            for minute in range(30, 60):
                                dates.append(current.replace(hour=hour, minute=minute))
                        elif hour == 15:
                            for minute in range(0, 30):
                                dates.append(current.replace(hour=hour, minute=minute))
                        else:
                            for minute in range(0, 60):
                                dates.append(current.replace(hour=hour, minute=minute))
                current += pd.Timedelta(days=1)
            dates = pd.DatetimeIndex(dates)
        else:
            raise ValueError(f"Unsupported data frequency: {data_frequency}")
        
        # Generate random price data
        n = len(dates)
        base_price = 100.0
        
        # Use geometric brownian motion for more realistic prices
        daily_returns = np.random.normal(0.0005, 0.015, n)
        price_path = base_price * np.exp(np.cumsum(daily_returns))
        
        # Generate OHLCV data
        high = price_path * np.random.uniform(1.001, 1.02, n)
        low = price_path * np.random.uniform(0.98, 0.999, n)
        
        # For open, use previous close or a gap
        open_prices = np.zeros(n)
        open_prices[0] = price_path[0] * np.random.uniform(0.99, 1.01)
        for i in range(1, n):
            # Simulate gaps with 20% probability
            if np.random.random() < 0.2:
                gap_factor = np.random.uniform(0.98, 1.02)
                open_prices[i] = price_path[i-1] * gap_factor
            else:
                # Small variation from previous close
                open_prices[i] = price_path[i-1] * np.random.uniform(0.999, 1.001)
        
        # Volume with randomness
        volume = np.random.randint(100000, 1000000, n)
        
        # Create DataFrame
        df = pd.DataFrame({
            'open': open_prices,
            'high': high,
            'low': low,
            'close': price_path,
            'volume': volume
        }, index=dates)
        
        # Add technical indicators
        df = self._add_indicators(df)
        
        return df
    
    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add basic technical indicators to the dataframe"""
        # SMA
        df['sma20'] = df['close'].rolling(20).mean()
        df['sma50'] = df['close'].rolling(50).mean()
        df['sma200'] = df['close'].rolling(200).mean()
        
        # EMA
        df['ema20'] = df['close'].ewm(span=20).mean()
        
        # Bollinger Bands
        sma20 = df['close'].rolling(20).mean()
        std20 = df['close'].rolling(20).std()
        df['upper_band'] = sma20 + (std20 * 2)
        df['lower_band'] = sma20 - (std20 * 2)
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).fillna(0)
        loss = -delta.where(delta < 0, 0).fillna(0)
        
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        
        rs = avg_gain / avg_loss
        df['rsi14'] = 100 - (100 / (1 + rs))
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr14'] = true_range.rolling(14).mean()
        
        return df
    
    def _create_synthetic_spread(
        self,
        symbol: str,
        date: pd.Timestamp,
        direction: str,
        price: float,
        parameters: Dict[str, Any]
    ) -> OptionSpread:
        """Create a synthetic option spread for simulation"""
        # This is a simplified model for backtesting
        # In reality, we would need a more sophisticated options pricing model
        
        spread_type = "BULL_CALL" if direction == "LONG" else "BEAR_PUT"
        expiration = date + pd.Timedelta(days=45)  # Default to 45 DTE
        
        # For backtesting, use simplified cost and reward-risk ratio
        cost = parameters.get("AVG_SPREAD_COST", self.config.AVG_SPREAD_COST)
        reward_risk = parameters.get("AVG_REWARD_RISK", self.config.AVG_REWARD_RISK)
        
        # Create synthetic spread
        spread = OptionSpread(
            symbol=symbol,
            expiration=expiration,
            spread_type=spread_type,
            cost=cost,
            max_profit=cost * reward_risk,
            max_loss=cost,
            delta=0.40,  # Middle of target range
            reward_risk_ratio=reward_risk
        )
        
        return spread
    
    def _calculate_position_size(self, capital: float, price: float) -> int:
        """Calculate appropriate position size based on risk parameters"""
        risk_amount = capital * self.config.RISK_PER_TRADE
        contracts = int(risk_amount / price)
        
        # Cap by max contracts
        max_contracts = self.config.MAX_CONTRACTS_PER_TRADE
        return min(contracts, max_contracts)
    
    def _calculate_stop_price(
        self, 
        data: pd.DataFrame, 
        direction: str, 
        atr_mult: float
    ) -> float:
        """Calculate stop price based on ATR"""
        # Get the last ATR value
        atr = data['atr14'].iloc[-1]
        latest_close = data['close'].iloc[-1]
        
        if direction == "LONG":
            return latest_close - (atr * atr_mult)
        else:  # SHORT
            return latest_close + (atr * atr_mult)
    
    def _check_exit_conditions(
        self, 
        trade: TradeResult, 
        current_price: float, 
        current_date: pd.Timestamp, 
        data: pd.DataFrame
    ) -> Optional[str]:
        """Check if any exit conditions are met"""
        # Stop loss
        if trade.stop_price:
            if trade.direction == "LONG" and current_price <= trade.stop_price:
                return "STOP_LOSS"
            elif trade.direction == "SHORT" and current_price >= trade.stop_price:
                return "STOP_LOSS"
        
        # Time-based exit (45 days max hold)
        days_held = (current_date - trade.entry_date).days
        if days_held >= 45:
            return "TIME_EXIT"
        
        # Profit target
        entry_price = trade.entry_price
        target_multiple = self.config.R_MULTIPLE_TARGET
        atr_value = data['atr14'].iloc[-1]
        
        if trade.direction == "LONG":
            r_value = atr_value * self.config.STOP_LOSS_ATR_MULT
            target_price = entry_price + (r_value * target_multiple)
            if current_price >= target_price:
                return "PROFIT_TARGET"
        else:  # SHORT
            r_value = atr_value * self.config.STOP_LOSS_ATR_MULT
            target_price = entry_price - (r_value * target_multiple)
            if current_price <= target_price:
                return "PROFIT_TARGET"
        
        # Trailing stop (if enabled)
        if self.config.USE_TRAILING_STOP and hasattr(trade, 'highest_price'):
            trail_percent = self.config.TRAILING_STOP_PERCENT
            
            if trade.direction == "LONG":
                if not hasattr(trade, 'highest_price') or current_price > trade.highest_price:
                    trade.highest_price = current_price
                
                trail_stop = trade.highest_price * (1 - trail_percent)
                if current_price < trail_stop:
                    return "TRAILING_STOP"
            else:  # SHORT
                if not hasattr(trade, 'lowest_price') or current_price < trade.lowest_price:
                    trade.lowest_price = current_price
                
                trail_stop = trade.lowest_price * (1 + trail_percent)
                if current_price > trail_stop:
                    return "TRAILING_STOP"
        
        return None
    
    def _simulate_exit_price(
        self, 
        trade: TradeResult, 
        current_price: float, 
        exit_reason: str
    ) -> float:
        """Simulate the exit price with realistic slippage"""
        # For backtesting, add some slippage to the exit
        if exit_reason == "STOP_LOSS":
            # Stops often have more slippage
            slippage = 0.01  # 1% slippage on stops
        else:
            slippage = 0.002  # 0.2% slippage on other exits
        
        if trade.direction == "LONG":
            return current_price * (1 - slippage)
        else:  # SHORT
            return current_price * (1 + slippage)
    
    def _calculate_performance_metrics(
        self, 
        trades: List[TradeResult], 
        equity_curve: pd.Series,
        drawdowns: pd.Series
    ) -> Dict[str, Union[float, int]]:
        """Calculate comprehensive performance metrics"""
        if not trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'avg_profit': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'sortino_ratio': 0,
                'calmar_ratio': 0,
                'annual_return': 0
            }
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        win_rate = win_count / total_trades if total_trades > 0 else 0
        
        gross_profits = sum(t.pnl for t in winning_trades)
        gross_losses = sum(t.pnl for t in losing_trades)
        
        profit_factor = abs(gross_profits / gross_losses) if gross_losses != 0 else float('inf')
        
        avg_win = gross_profits / win_count if win_count > 0 else 0
        avg_loss = gross_losses / loss_count if loss_count > 0 else 0
        
        # Calculate drawdown metrics
        max_drawdown = drawdowns.max()
        
        # Calculate returns for Sharpe ratio
        returns = equity_curve.pct_change().dropna()
        
        # Calculate annual return
        start_date = equity_curve.index[0]
        end_date = equity_curve.index[-1]
        years = (end_date - start_date).days / 365.25
        
        total_return = (equity_curve[-1] / equity_curve[0]) - 1
        annual_return = ((1 + total_return) ** (1 / years)) - 1 if years > 0 else 0
        
        # Calculate risk metrics
        risk_free_rate = 0.02  # Assume 2% risk-free rate
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        
        sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252) if excess_returns.std() > 0 else 0
        
        # Sortino ratio - using only negative returns for denominator
        negative_returns = excess_returns[excess_returns < 0]
        sortino_ratio = (excess_returns.mean() / negative_returns.std()) * np.sqrt(252) if negative_returns.std() > 0 else 0
        
        # Calmar ratio
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_profit': (gross_profits + gross_losses) / total_trades if total_trades > 0 else 0,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'annual_return': annual_return,
            'total_return': total_return
        }
    
    def _generate_parameter_grid(
        self, 
        parameter_ranges: Dict[str, Tuple[float, float]], 
        n_points: int
    ) -> List[Dict[str, float]]:
        """Generate a grid of parameter combinations for grid search"""
        param_values = {}
        for param_name, (min_val, max_val) in parameter_ranges.items():
            param_values[param_name] = np.linspace(min_val, max_val, n_points)
        
        # Generate all combinations
        import itertools
        param_combinations = list(itertools.product(*param_values.values()))
        
        # Convert to list of dictionaries
        param_grid = []
        for combination in param_combinations:
            params = {}
            for i, param_name in enumerate(parameter_ranges.keys()):
                params[param_name] = combination[i]
            param_grid.append(params)
        
        return param_grid
    
    def _generate_random_parameters(
        self, 
        parameter_ranges: Dict[str, Tuple[float, float]], 
        n_samples: int
    ) -> List[Dict[str, float]]:
        """Generate random parameter sets for random search"""
        param_sets = []
        
        for _ in range(n_samples):
            params = {}
            for param_name, (min_val, max_val) in parameter_ranges.items():
                # Generate random value within range
                params[param_name] = min_val + np.random.random() * (max_val - min_val)
            param_sets.append(params)
        
        return param_sets 