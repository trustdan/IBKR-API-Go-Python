# Comprehensive Implementation Plan: Auto Vertical Spread Trader

Based on both sets of feedback, here's a comprehensive and refined implementation plan that addresses all identified gaps while maintaining the Python-Go hybrid architecture:

## 1. Objectives & Refined Architecture

- Python orchestrator for business logic, configuration, strategy implementation, and API interactions
- Go service for high-performance concurrent market scanning
- API Contract defined via gRPC/Protobuf
- Early-stage backtesting framework
- Robust error handling with recovery mechanisms
- Containerized deployment for consistent dependencies

## Dual Execution Modes

A key enhancement to the system is the implementation of dual execution modes to accommodate differences between paper trading and live trading environments:

1. **Paper Trading Mode**:
   - Executes orders at exact bid/ask prices
   - Uses market orders to ensure fills
   - Necessary for IBKR TWS paper trading which requires hitting the bid/ask directly

2. **Live Trading Mode**:
   - Attempts price improvement by placing limit orders
   - Uses configurable price improvement factor to split the bid/ask spread
   - Aims to achieve better execution prices than the exact market prices

This dual-mode implementation ensures the system can seamlessly transition from testing to production while accounting for the different execution mechanics of paper vs. live trading environments.

```plaintext
[ Market Data/API ] ↔ [ Python Orchestrator ] ←gRPC→ [ Go Scanner Service ]
         ↓                      ↓                           ↓
[ Data Cache Layer ] [ Strategy & Options Logic ]   [ Performance Metrics ]
         ↓                      ↓                           ↓
[ Backtesting Engine ]  [ IBKR API / Order Management ]  [ Monitoring ]
                               ↓
                   [ Alerting & Notification System ]
```

## 2. Core Strategy Implementation

```python
class StrategyFactory:
    def get_strategy(self, strategy_type):
        strategies = {
            "HIGH_BASE": HighBaseStrategy(),
            "LOW_BASE": LowBaseStrategy(),
            "BULL_PULLBACK": BullPullbackStrategy(),
            "BEAR_RALLY": BearRallyStrategy()
        }
        return strategies.get(strategy_type)

class BaseStrategy:
    def compute_indicators(self, df):
        # Common indicators used by all strategies
        df['ATR14'] = df.ta.atr(length=14)
        df['RSI14'] = df.ta.rsi(length=14)
        # Add other common indicators
        return df
    
    def should_execute(self, current_time):
        # Trade timing logic - implement after 3 PM ET rule
        et_time = convert_to_eastern(current_time)
        return et_time.hour >= 15  # Execute after 3 PM ET

class HighBaseStrategy(BaseStrategy):
    def generate_signals(self, df, config):
        signals = []
        for row in df.itertuples():
            if (row.close > row.ATR14 * config.HIGH_BASE_MAX_ATR_RATIO and
                row.RSI14 > config.HIGH_BASE_MIN_RSI):
                signals.append(('LONG', row.symbol))
        return signals

class LowBaseStrategy(BaseStrategy):
    def generate_signals(self, df, config):
        signals = []
        for row in df.itertuples():
            if (row.close < row.ATR14 * config.LOW_BASE_MIN_ATR_RATIO and
                row.RSI14 < config.LOW_BASE_MAX_RSI):
                signals.append(('SHORT', row.symbol))
        return signals

class BullPullbackStrategy(BaseStrategy):
    def generate_signals(self, df, config):
        signals = []
        # Check for uptrend using moving averages
        df['MA50'] = df.ta.sma(length=50)
        df['MA200'] = df.ta.sma(length=200)
        
        for i in range(len(df) - 1):
            # Check for uptrend (MA50 > MA200)
            if df['MA50'].iloc[i] > df['MA200'].iloc[i]:
                # Check for pullback (RSI dipped below threshold)
                if df['RSI14'].iloc[i] < config.BULL_PULLBACK_RSI_THRESHOLD and \
                   df['RSI14'].iloc[i+1] > config.BULL_PULLBACK_RSI_THRESHOLD:
                    signals.append(('LONG', df.iloc[i+1].symbol))
        return signals

class BearRallyStrategy(BaseStrategy):
    def generate_signals(self, df, config):
        signals = []
        # Check for downtrend using moving averages
        df['MA50'] = df.ta.sma(length=50)
        df['MA200'] = df.ta.sma(length=200)
        
        for i in range(len(df) - 1):
            # Check for downtrend (MA50 < MA200)
            if df['MA50'].iloc[i] < df['MA200'].iloc[i]:
                # Check for rally (RSI moved above threshold)
                if df['RSI14'].iloc[i] > config.BEAR_RALLY_RSI_THRESHOLD and \
                   df['RSI14'].iloc[i+1] < config.BEAR_RALLY_RSI_THRESHOLD:
                    signals.append(('SHORT', df.iloc[i+1].symbol))
        return signals
```

### Cucumber Scenario for Strategy Implementation:

```gherkin
Feature: Multiple Trading Strategies
  Scenario: High Base Strategy Execution
    Given market data for "AAPL" with closing price above HIGH_BASE_MAX_ATR_RATIO * ATR
    And RSI14 above HIGH_BASE_MIN_RSI threshold
    And current time is after 3 PM ET
    When the high base strategy evaluates the data
    Then it should generate a LONG signal for "AAPL"
    
  Scenario: Low Base Strategy Execution
    Given market data for "MSFT" with closing price below LOW_BASE_MIN_ATR_RATIO * ATR
    And RSI14 below LOW_BASE_MAX_RSI threshold
    When the low base strategy evaluates the data
    Then it should generate a SHORT signal for "MSFT"
    
  Scenario: Bull Pullback Strategy Execution
    Given market data for "GOOGL" with MA50 above MA200
    And RSI14 falling below BULL_PULLBACK_RSI_THRESHOLD then rising above it
    When the bull pullback strategy evaluates the data
    Then it should generate a LONG signal for "GOOGL"
    
  Scenario: Bear Rally Strategy Execution
    Given market data for "NFLX" with MA50 below MA200
    And RSI14 rising above BEAR_RALLY_RSI_THRESHOLD then falling below it
    When the bear rally strategy evaluates the data
    Then it should generate a SHORT signal for "NFLX"
```

## 3. Option Selection Logic

```python
class OptionSelector:
    def __init__(self, config):
        self.config = config
        
    def select_vertical_spread(self, symbol, direction, current_price):
        # Fetch available options
        options_chain = fetch_options_chain(symbol)
        
        # Filter by expiration (prefer 30-45 DTE)
        valid_expirations = filter_by_dte(options_chain, 
                                         self.config.MIN_DTE, 
                                         self.config.MAX_DTE)
        
        if direction == "LONG":
            # For bullish trades, find call verticals
            spreads = self.create_call_vertical_spreads(valid_expirations)
        else:
            # For bearish trades, find put verticals
            spreads = self.create_put_vertical_spreads(valid_expirations)
            
        # Filter by criteria
        filtered_spreads = self.filter_spreads(spreads)
        
        # Rank by reward-to-risk ratio
        ranked_spreads = self.rank_by_reward_risk(filtered_spreads)
        
        return ranked_spreads[0] if ranked_spreads else None
        
    def filter_spreads(self, spreads):
        return [spread for spread in spreads if 
                self.config.MIN_DELTA <= spread.delta <= self.config.MAX_DELTA and
                spread.cost <= self.config.MAX_SPREAD_COST and
                spread.reward_risk_ratio >= self.config.MIN_REWARD_RISK]
                
    def create_call_vertical_spreads(self, option_chains):
        """
        Create bull call spreads by:
        1. Buying a lower strike call
        2. Selling a higher strike call
        Both with the same expiration
        """
        spreads = []
        for expiry, chain in option_chains.items():
            calls = sorted([opt for opt in chain if opt.option_type == 'call'], 
                          key=lambda x: x.strike)
            
            for i in range(len(calls) - 1):
                long_call = calls[i]
                short_call = calls[i + 1]
                
                # Create the spread
                spread = OptionSpread(
                    symbol=long_call.symbol,
                    expiration=expiry,
                    spread_type="BULL_CALL",
                    long_leg=long_call,
                    short_leg=short_call,
                    cost=long_call.ask - short_call.bid,
                    max_profit=short_call.strike - long_call.strike - (long_call.ask - short_call.bid),
                    max_loss=long_call.ask - short_call.bid,
                    delta=long_call.delta - short_call.delta
                )
                
                spread.reward_risk_ratio = spread.max_profit / spread.max_loss if spread.max_loss > 0 else 0
                spreads.append(spread)
                
        return spreads
                
    def create_put_vertical_spreads(self, option_chains):
        """
        Create bear put spreads by:
        1. Buying a higher strike put
        2. Selling a lower strike put
        Both with the same expiration
        """
        spreads = []
        for expiry, chain in option_chains.items():
            puts = sorted([opt for opt in chain if opt.option_type == 'put'], 
                         key=lambda x: x.strike)
            
            for i in range(len(puts) - 1):
                short_put = puts[i]
                long_put = puts[i + 1]
                
                # Create the spread
                spread = OptionSpread(
                    symbol=long_put.symbol,
                    expiration=expiry,
                    spread_type="BEAR_PUT",
                    long_leg=long_put,
                    short_leg=short_put,
                    cost=long_put.ask - short_put.bid,
                    max_profit=long_put.strike - short_put.strike - (long_put.ask - short_put.bid),
                    max_loss=long_put.ask - short_put.bid,
                    delta=long_put.delta - short_put.delta
                )
                
                spread.reward_risk_ratio = spread.max_profit / spread.max_loss if spread.max_loss > 0 else 0
                spreads.append(spread)
                
        return spreads
```

### Cucumber Scenario for Option Selection:

```gherkin
Feature: Option Vertical Spread Selection
  Scenario: Select optimal bull call vertical spread
    Given a LONG signal for "MSFT"
    And options with 30-45 days to expiration
    When the option selector evaluates available spreads
    Then it selects a spread where:
      | Delta              | Between 0.30 and 0.50 |
      | Max Cost           | <= $500               |
      | Reward-to-Risk     | >= 1.5                |
      | Spread Type        | BULL_CALL             |
      
  Scenario: Select optimal bear put vertical spread
    Given a SHORT signal for "AAPL"
    And options with 30-45 days to expiration
    When the option selector evaluates available spreads
    Then it selects a spread where:
      | Delta              | Between 0.30 and 0.50 |
      | Max Cost           | <= $500               |
      | Reward-to-Risk     | >= 1.5                |
      | Spread Type        | BEAR_PUT              |
```

## 4. Trade Execution & Management

```python
class TradeExecutor:
    def __init__(self, config, broker_api, alert_system):
        self.config = config
        self.broker_api = broker_api
        self.alert_system = alert_system
        self.queued_trades = []
        self.trading_mode = config.TRADING_MODE
        
    def execute_trade(self, trade_signal, option_spread, position_size):
        current_time = datetime.now()
        
        # Verify trading hours and preferred execution time
        if not self.is_valid_execution_time(current_time):
            queued_trade = {
                'signal': trade_signal,
                'spread': option_spread,
                'size': position_size,
                'queued_at': current_time
            }
            self.queued_trades.append(queued_trade)
            
            # Send alert about queued trade
            self.alert_system.send_alert(
                f"Trade queued for {trade_signal.symbol}",
                f"Direction: {trade_signal.direction}, Size: {position_size}",
                severity="INFO"
            )
            
            return "QUEUED", "Trade queued for execution after 3PM ET"
        
        # Execute the trade
        try:
            start_time = time.time()
            
            # Different execution methods based on trading mode
            if self.trading_mode == "PAPER":
                order_id = self._execute_paper_trade(trade_signal, option_spread, position_size)
            else:  # LIVE mode
                order_id = self._execute_live_trade(trade_signal, option_spread, position_size)
            
            execution_time = time.time() - start_time
            
            # Record execution latency for performance monitoring
            self.record_execution_latency(execution_time)
            
            # Send alert about executed trade
            self.alert_system.send_alert(
                f"Trade executed for {trade_signal.symbol}",
                f"Direction: {trade_signal.direction}, Size: {position_size}, Order ID: {order_id}",
                severity="INFO"
            )
            
            return "EXECUTED", order_id
        except Exception as e:
            error_msg = str(e)
            log_error("Trade execution failed", error_msg)
            
            # Send alert about failed trade
            self.alert_system.send_alert(
                f"Trade execution failed for {trade_signal.symbol}",
                error_msg,
                severity="HIGH"
            )
            
            return "FAILED", error_msg
    
    def _execute_paper_trade(self, trade_signal, option_spread, position_size):
        """Paper trading execution - hits the bid/ask directly without price improvement"""
        # For paper trading, we need to use exact bid/ask prices as price improvement isn't modeled
        if trade_signal.direction == "LONG":
            # For LONG trades in paper mode, pay the ask price
            price = option_spread.long_leg.ask - option_spread.short_leg.bid
        else:
            # For SHORT trades in paper mode, sell at the bid price
            price = option_spread.long_leg.bid - option_spread.short_leg.ask
            
        # Place the order at market prices (no price improvement)
        return self.broker_api.place_order(
            symbol=trade_signal.symbol,
            direction=trade_signal.direction,
            contracts=position_size,
            option_spread=option_spread,
            price_type="MARKET",
            limit_price=None
        )
    
    def _execute_live_trade(self, trade_signal, option_spread, position_size):
        """Live trading execution - attempts to get price improvement by splitting bid/ask"""
        # For live trading, attempt to get price improvement by placing limit orders
        if trade_signal.direction == "LONG":
            # For LONG trades in live mode, try to get fill between bid and ask
            # Calculate midpoint or slightly better than midpoint price
            bid = option_spread.long_leg.bid - option_spread.short_leg.ask
            ask = option_spread.long_leg.ask - option_spread.short_leg.bid
            # Start with price improvement at 40% of the spread (closer to the bid)
            improvement_factor = self.config.PRICE_IMPROVEMENT_FACTOR if hasattr(self.config, 'PRICE_IMPROVEMENT_FACTOR') else 0.4
            limit_price = bid + (ask - bid) * improvement_factor
        else:
            # For SHORT trades in live mode, try to get fill between bid and ask
            bid = option_spread.long_leg.bid - option_spread.short_leg.ask
            ask = option_spread.long_leg.ask - option_spread.short_leg.bid
            # Start with price improvement at 60% of the spread (closer to the ask)
            improvement_factor = 1 - (self.config.PRICE_IMPROVEMENT_FACTOR if hasattr(self.config, 'PRICE_IMPROVEMENT_FACTOR') else 0.4)
            limit_price = bid + (ask - bid) * improvement_factor
            
        # Place the order with limit price for price improvement
        return self.broker_api.place_order(
            symbol=trade_signal.symbol,
            direction=trade_signal.direction,
            contracts=position_size,
            option_spread=option_spread,
            price_type="LIMIT",
            limit_price=limit_price
        )
            
    def is_valid_execution_time(self, current_time):
        # Convert to Eastern Time
        et_time = convert_to_eastern(current_time)
        
        # Check if market is open
        if not is_market_open(et_time):
            return False
            
        # Check if after 3 PM ET
        if et_time.hour >= 15:
            return True
            
        # Check if close to market close and exception allowed
        if et_time.hour == 14 and et_time.minute >= 45 and self.config.ALLOW_LATE_DAY_ENTRY:
            return True
            
        return False
        
    def process_queued_trades(self):
        current_time = datetime.now()
        
        if not self.is_valid_execution_time(current_time):
            return
            
        # Process all queued trades
        for queued_trade in self.queued_trades[:]:
            status, result = self.execute_trade(
                queued_trade['signal'],
                queued_trade['spread'],
                queued_trade['size']
            )
            
            if status == "EXECUTED":
                self.queued_trades.remove(queued_trade)
                
    def record_execution_latency(self, latency):
        if latency > self.config.MAX_ORDER_LATENCY:
            log_warning(f"Order execution latency above threshold: {latency:.2f}s > {self.config.MAX_ORDER_LATENCY}s")
            
            # Send alert if latency is too high
            if latency > self.config.CRITICAL_ORDER_LATENCY:
                self.alert_system.send_alert(
                    "Critical order execution latency",
                    f"Latency: {latency:.2f}s",
                    severity="HIGH"
                )
```

### Cucumber Scenario for Trade Execution Timing:

```gherkin
Feature: Trade Execution Timing
  Scenario: Trade during preferred execution window
    Given a valid trade signal for "AAPL"
    And current time is 15:30 ET (after 3 PM)
    When the trade executor processes the signal
    Then the trade should be executed immediately
    And return status "EXECUTED" with an order ID
    
  Scenario: Queue trade outside preferred execution window
    Given a valid trade signal for "MSFT"
    And current time is 11:15 ET (before 3 PM)
    When the trade executor processes the signal
    Then the trade should be queued
    And return status "QUEUED"
    
  Scenario: Process queued trades at preferred time
    Given 3 queued trades
    And current time is 15:05 ET (after 3 PM)
    When the trade executor processes queued trades
    Then all queued trades should be executed
    And the queue should be empty
    
  Scenario: Paper Trading Mode Order Execution
    Given the system is configured for "PAPER" trading mode
    And a valid trade signal for "AAPL" LONG
    When the trade executor processes the signal
    Then the order should be placed at market prices
    And use the exact bid/ask prices without price improvement
    
  Scenario: Live Trading Mode Order Execution
    Given the system is configured for "LIVE" trading mode
    And a valid trade signal for "MSFT" LONG
    And PRICE_IMPROVEMENT_FACTOR set to 0.4
    When the trade executor processes the signal
    Then the order should be placed as a limit order
    And the limit price should be between bid and ask
    And be closer to the bid based on the improvement factor
```

## 5. Data Management & Caching Strategy

```python
class DataManager:
    def __init__(self, config):
        self.config = config
        self.cache = {}
        self.cache_expiry = {}
        self.go_client = None  # gRPC client for Go scanner service
        
    def set_go_client(self, client):
        self.go_client = client
        
    def get_data(self, symbol, timeframe, start_date=None, end_date=None):
        """Get market data with caching"""
        cache_key = f"{symbol}:{timeframe}:{start_date}:{end_date}"
        
        # Check if data is in cache and not expired
        current_time = time.time()
        if (cache_key in self.cache and 
            cache_key in self.cache_expiry and 
            current_time < self.cache_expiry[cache_key]):
            return self.cache[cache_key]
            
        # Fetch fresh data
        if timeframe == 'daily':
            data = self.fetch_daily_data(symbol, start_date, end_date)
        elif timeframe == 'minute':
            data = self.fetch_minute_data(symbol, start_date, end_date)
        else:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
            
        # Store in cache with expiry
        self.cache[cache_key] = data
        
        # Set expiry based on timeframe
        if timeframe == 'daily':
            # Daily data expires after market close
            self.cache_expiry[cache_key] = get_next_market_close_timestamp()
        elif timeframe == 'minute':
            # Minute data expires after configured minutes
            self.cache_expiry[cache_key] = current_time + self.config.MINUTE_DATA_CACHE_EXPIRY
            
        return data
        
    def fetch_daily_data(self, symbol, start_date=None, end_date=None):
        """Fetch daily historical data from data provider"""
        # Implementation depends on the data provider API
        pass
        
    def fetch_minute_data(self, symbol, start_date=None, end_date=None):
        """Fetch minute historical data from data provider"""
        # Implementation depends on the data provider API
        pass
        
    def prefetch_universe_data(self, symbols, timeframe):
        """Prefetch data for the entire universe in parallel using Go service"""
        if not self.go_client:
            raise ValueError("Go client not initialized")
            
        # Send bulk request to Go service
        response = self.go_client.bulk_fetch(symbols, timeframe)
        
        # Update cache
        for symbol, data in response.items():
            cache_key = f"{symbol}:{timeframe}::"
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = time.time() + self.config.UNIVERSE_CACHE_EXPIRY
            
    def clear_expired_cache(self):
        """Remove expired items from cache"""
        current_time = time.time()
        expired_keys = [key for key, expiry in self.cache_expiry.items() 
                       if current_time > expiry]
                       
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            del self.cache_expiry[key]
            
        return len(expired_keys)
        
    def get_options_chain(self, symbol):
        """Fetch options chain with caching"""
        cache_key = f"options:{symbol}"
        
        # Check cache
        current_time = time.time()
        if (cache_key in self.cache and 
            cache_key in self.cache_expiry and 
            current_time < self.cache_expiry[cache_key]):
            return self.cache[cache_key]
            
        # Fetch options data
        options_data = self.fetch_options_data(symbol)
        
        # Cache the data
        self.cache[cache_key] = options_data
        self.cache_expiry[cache_key] = current_time + self.config.OPTIONS_CACHE_EXPIRY
        
        return options_data
        
    def fetch_options_data(self, symbol):
        """Fetch options chain from provider"""
        # Implementation depends on the options data provider API
        pass
```

### Cucumber Scenario for Data Management:

```gherkin
Feature: Market Data Caching
  Scenario: Cache hit for recent data
    Given cached daily data for "AAPL" that is not expired
    When the system requests daily data for "AAPL"
    Then the data should be retrieved from cache
    And no external API calls should be made
    
  Scenario: Cache miss for expired data
    Given cached minute data for "MSFT" that is expired
    When the system requests minute data for "MSFT"
    Then fresh data should be fetched from the data provider
    And the cache should be updated with the new data
    
  Scenario: Prefetch universe data
    Given a universe of 100 symbols
    When the prefetch_universe_data method is called
    Then the Go scanner service should process the request
    And all symbols' data should be stored in cache
    And the system can process them at > 100 symbols per second
```

## 6. Error Handling & Recovery

```python
class ErrorHandler:
    def __init__(self, config, alert_system):
        self.config = config
        self.alert_system = alert_system
        self.error_counts = defaultdict(int)
        self.recovery_attempts = defaultdict(int)
        
    def handle_error(self, component, error_type, error_msg, context=None):
        # Log the error
        log_error(f"Error in {component}: {error_type}", error_msg, context)
        
        # Increment error counter
        error_key = f"{component}:{error_type}"
        self.error_counts[error_key] += 1
        
        # Alert if critical or threshold exceeded
        if self.is_critical_error(error_type) or self.error_counts[error_key] >= self.config.ERROR_THRESHOLD:
            self.alert_system.send_alert(
                f"Critical error in {component}: {error_type}",
                error_msg,
                severity="HIGH"
            )
        
        # Attempt recovery
        if self.recovery_attempts[error_key] < self.config.MAX_RECOVERY_ATTEMPTS:
            return self.attempt_recovery(component, error_type, context)
        else:
            return False
            
    def is_critical_error(self, error_type):
        """Determine if an error type is critical"""
        critical_errors = [
            "CONNECTION_ERROR",
            "AUTHENTICATION_ERROR",
            "ORDER_EXECUTION_ERROR",
            "DATA_INTEGRITY_ERROR"
        ]
        return error_type in critical_errors
            
    def attempt_recovery(self, component, error_type, context):
        self.recovery_attempts[f"{component}:{error_type}"] += 1
        
        # Component-specific recovery strategies
        if component == "IBKR_API" and error_type == "CONNECTION_ERROR":
            return self.recover_api_connection()
        elif component == "DATA_PROVIDER" and error_type == "DATA_MISSING":
            return self.recover_missing_data(context.get("symbol"))
        elif component == "PANDAS_TA" and error_type == "CALCULATION_ERROR":
            return self.recover_calculation(context.get("indicator"))
        elif component == "GO_SCANNER" and error_type == "GRPC_ERROR":
            return self.recover_scanner_connection()
            
        return False
        
    def recover_api_connection(self):
        """Attempt to recover IBKR API connection"""
        try:
            # Reconnect logic
            log_info("Attempting to reconnect to IBKR API")
            # Implementation depends on the broker API
            return True
        except Exception as e:
            log_error("Failed to recover API connection", str(e))
            return False
            
    def recover_missing_data(self, symbol):
        """Attempt to recover missing market data"""
        try:
            log_info(f"Attempting to recover data for {symbol}")
            # Try alternative data source or use cached data
            return True
        except Exception as e:
            log_error(f"Failed to recover data for {symbol}", str(e))
            return False
            
    def recover_calculation(self, indicator):
        """Attempt to recover from calculation error"""
        try:
            log_info(f"Attempting alternative calculation for {indicator}")
            # Implement fallback calculation method
            return True
        except Exception as e:
            log_error(f"Failed to recover calculation for {indicator}", str(e))
            return False
            
    def recover_scanner_connection(self):
        """Attempt to recover Go scanner connection"""
        try:
            log_info("Attempting to reconnect to Go scanner service")
            # Implementation depends on the gRPC setup
            return True
        except Exception as e:
            log_error("Failed to recover scanner connection", str(e))
            return False
```

### Cucumber Scenario for Error Handling:

```gherkin
Feature: Error Handling and Recovery
  Scenario: Connection error recovery
    Given the system loses connection to IBKR API
    When the error handler processes the "CONNECTION_ERROR"
    Then it should attempt to reconnect to the API
    And log the recovery attempt
    And send an alert if the recovery fails
    
  Scenario: Indicator calculation error fallback
    Given an error occurs calculating RSI with pandas-ta
    When the error handler processes the "CALCULATION_ERROR"
    Then it should attempt an alternative calculation method
    And log the recovery attempt
    
  Scenario: Multiple repeated errors trigger alert
    Given ERROR_THRESHOLD is set to 3
    When the same error occurs 3 times
    Then an alert should be sent to all configured channels
    And the alert should include error details
```

## 7. Backtesting Framework

```python
class BacktestEngine:
    def __init__(self, config, strategies, option_selector, risk_manager):
        self.config = config
        self.strategies = strategies
        self.option_selector = option_selector
        self.risk_manager = risk_manager
        self.results = defaultdict(list)
        self.data_manager = DataManager(config)
        
    def run_backtest(self, symbols, start_date, end_date, strategies=None):
        """Run backtest for specified symbols and date range"""
        if strategies is None:
            strategies = self.strategies
            
        results = {}
        for symbol in symbols:
            log_info(f"Backtesting {symbol} from {start_date} to {end_date}")
            
            # Fetch historical data
            historical_data = self.data_manager.get_data(
                symbol, 'daily', start_date, end_date
            )
            
            # Run each strategy
            symbol_results = {}
            for strategy_name, strategy in strategies.items():
                strategy_results = self.backtest_strategy(
                    strategy, strategy_name, symbol, historical_data
                )
                symbol_results[strategy_name] = strategy_results
                
            results[symbol] = symbol_results
            
        # Calculate aggregate metrics
        metrics = self.calculate_aggregate_metrics(results)
        
        return {
            'detailed_results': results,
            'metrics': metrics
        }
        
    def backtest_strategy(self, strategy, strategy_name, symbol, historical_data):
        """Backtest a single strategy on a single symbol"""
        # Initialize tracking variables
        trades = []
        current_position = None
        equity_curve = [self.config.INITIAL_EQUITY]
        
        # Add indicators
        data_with_indicators = strategy.compute_indicators(historical_data)
        
        # Simulate day by day
        for i in range(len(data_with_indicators)):
            current_day = data_with_indicators.iloc[i:i+1]
            current_date = current_day.index[0]
            
            # Set time to 3 PM ET for signal generation check
            simulated_time = pd.Timestamp(current_date) + pd.Timedelta(hours=15)
            
            # Check for entry signals if no position
            if current_position is None and strategy.should_execute(simulated_time):
                signals = strategy.generate_signals(current_day, self.config)
                
                if signals:
                    for direction, _ in signals:
                        # Simulate option selection
                        spread = self.simulate_option_selection(
                            symbol, direction, current_day['close'].iloc[0], current_date
                        )
                        
                        if spread:
                            # Calculate position size
                            position_size = self.risk_manager.calculate_position_size(
                                equity_curve[-1], spread.cost
                            )
                            
                            # Create position
                            current_position = {
                                'symbol': symbol,
                                'entry_date': current_date,
                                'entry_price': spread.cost,
                                'direction': direction,
                                'size': position_size,
                                'spread': spread,
                                'stop_price': self.calculate_stop_price(
                                    current_day, direction, self.config.STOP_LOSS_ATR_MULT
                                )
                            }
            
            # Check for exit signals if position exists
            if current_position is not None:
                exit_signals = self.check_exit_conditions(
                    current_position, current_day, current_date
                )
                
                if exit_signals:
                    # Close position
                    exit_price = self.simulate_exit_price(
                        current_position, current_day, exit_signals[0]
                    )
                    
                    # Calculate PnL
                    pnl = self.calculate_pnl(
                        current_position, exit_price, exit_signals[0]
                    )
                    
                    # Update equity
                    equity_curve.append(equity_curve[-1] + pnl)
                    
                    # Record trade
                    trade = {
                        'symbol': symbol,
                        'strategy': strategy_name,
                        'entry_date': current_position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': current_position['entry_price'],
                        'exit_price': exit_price,
                        'direction': current_position['direction'],
                        'size': current_position['size'],
                        'pnl': pnl,
                        'exit_reason': exit_signals[0]
                    }
                    trades.append(trade)
                    
                    # Reset position
                    current_position = None
            
            # Update equity curve on days with no changes
            if len(equity_curve) <= i:
                equity_curve.append(equity_curve[-1])
                
        # Calculate strategy metrics
        metrics = self.calculate_strategy_metrics(trades, equity_curve)
        
        return {
            'trades': trades,
            'equity_curve': equity_curve,
            'metrics': metrics
        }
        
    def simulate_option_selection(self, symbol, direction, current_price, date):
        """Simulate option chain and selection for backtesting"""
        # For backtesting, generate a simplified synthetic option chain
        # In a real implementation, you'd use historical options data if available
        
        # Create a synthetic spread with realistic properties
        if direction == "LONG":
            spread_type = "BULL_CALL"
        else:
            spread_type = "BEAR_PUT"
            
        # Create synthetic spread with average properties
        spread = {
            'symbol': symbol,
            'expiration': date + pd.Timedelta(days=45),  # 45 DTE
            'spread_type': spread_type,
            'cost': self.config.AVG_SPREAD_COST,
            'max_profit': self.config.AVG_SPREAD_COST * self.config.AVG_REWARD_RISK,
            'max_loss': self.config.AVG_SPREAD_COST,
            'delta': 0.40,  # Middle of target range
            'reward_risk_ratio': self.config.AVG_REWARD_RISK
        }
        
        return spread
        
    def calculate_strategy_metrics(self, trades, equity_curve):
        """Calculate performance metrics for a strategy"""
        if not trades:
            return {
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'total_trades': 0,
                'net_profit': 0
            }
            
        # Calculate basic metrics
        wins = [t['pnl'] for t in trades if t['pnl'] > 0]
        losses = [t['pnl'] for t in trades if t['pnl'] <= 0]
        
        win_rate = len(wins) / len(trades) if trades else 0
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        profit_factor = abs(sum(wins) / sum(losses)) if sum(losses) != 0 else float('inf')
        
        # Calculate drawdown
        max_drawdown = 0
        peak = equity_curve[0]
        
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
            
        # Calculate Sharpe ratio (assuming daily returns)
        daily_returns = [
            (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            for i in range(1, len(equity_curve))
        ]
        
        sharpe_ratio = 0
        if daily_returns:
            mean_return = sum(daily_returns) / len(daily_returns)
            std_dev = (sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns)) ** 0.5
            sharpe_ratio = (mean_return / std_dev) * (252 ** 0.5) if std_dev > 0 else 0
            
        return {
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'total_trades': len(trades),
            'net_profit': equity_curve[-1] - equity_curve[0]
        }
        
    def calculate_aggregate_metrics(self, results):
        """Calculate aggregate metrics across all symbols and strategies"""
        all_trades = []
        all_metrics = {}
        
        for symbol, symbol_results in results.items():
            for strategy, strategy_results in symbol_results.items():
                all_trades.extend(strategy_results['trades'])
                
        # Combine all trades and calculate overall metrics
        # This is a simplified version - could be expanded
        wins = [t['pnl'] for t in all_trades if t['pnl'] > 0]
        losses = [t['pnl'] for t in all_trades if t['pnl'] <= 0]
        
        all_metrics['overall_win_rate'] = len(wins) / len(all_trades) if all_trades else 0
        all_metrics['total_trades'] = len(all_trades)
        all_metrics['net_profit'] = sum(t['pnl'] for t in all_trades)
        
        return all_metrics
```

### Cucumber Scenario for Backtesting:

```gherkin
Feature: Strategy Backtesting
  Scenario: Backtest performance evaluation
    Given historical data for "SPY" from "2023-01-01" to "2023-12-31"
    When I run the backtest for the "HIGH_BASE" strategy
    Then the system calculates the following metrics:
      | Win Rate               | > 50%                 |
      | Average Profit         | > Average Loss        |
      | Profit Factor          | > 1.5                 |
      | Max Drawdown           | < 15%                 |
      | Sharpe Ratio           | > 1.0                 |
      
  Scenario: Multi-strategy backtest comparison
    Given historical data for 10 symbols from "2023-01-01" to "2023-12-31"
    When I run the backtest for all 4 strategies
    Then the system ranks strategies by performance
    And generates a comparative analysis report
    
  Scenario: Parameter optimization
    Given historical data for "QQQ" from "2023-01-01" to "2023-12-31"
    When I run the backtest for the "BULL_PULLBACK" strategy with multiple parameter sets
    Then the system identifies the optimal parameter values
    And displays the performance metrics for each parameter set
```

## 8. Performance Metrics & Benchmarks

```python
class PerformanceMonitor:
    def __init__(self, config):
        self.config = config
        self.metrics = defaultdict(dict)
        self.start_time = time.time()
        
    def record_scan_performance(self, symbols_count, scan_time):
        """Record scanner performance metrics"""
        component = "scanner"
        
        # Calculate symbols per second
        symbols_per_second = symbols_count / scan_time if scan_time > 0 else 0
        
        # Add to metrics history
        timestamp = time.time()
        self.metrics[component][timestamp] = {
            'scan_time': scan_time,
            'symbols_count': symbols_count,
            'symbols_per_second': symbols_per_second
        }
        
        # Calculate rolling averages
        self.update_rolling_averages(component)
        
        # Check against benchmarks
        self.check_performance_thresholds(component)
        
    def record_execution_latency(self, order_placement_time):
        """Record order execution latency"""
        component = "execution"
        
        # Add to metrics history
        timestamp = time.time()
        self.metrics[component][timestamp] = {
            'latency': order_placement_time
        }
        
        # Calculate rolling averages
        self.update_rolling_averages(component)
        
        # Check against benchmarks
        self.check_performance_thresholds(component)
        
    def update_rolling_averages(self, component):
        """Calculate rolling averages for a component"""
        if component not in self.metrics or not self.metrics[component]:
            return
            
        # Get timestamps and sort chronologically
        timestamps = sorted(self.metrics[component].keys())
        
        # Filter to recent period (last hour)
        recent_period = time.time() - 3600  # 1 hour
        recent_timestamps = [ts for ts in timestamps if ts >= recent_period]
        
        if not recent_timestamps:
            return
            
        # Calculate averages based on component type
        if component == "scanner":
            avg_scan_time = sum(self.metrics[component][ts]['scan_time'] for ts in recent_timestamps) / len(recent_timestamps)
            avg_symbols_per_second = sum(self.metrics[component][ts]['symbols_per_second'] for ts in recent_timestamps) / len(recent_timestamps)
            
            # Update rolling averages
            self.metrics[component]['avg_scan_time_1h'] = avg_scan_time
            self.metrics[component]['avg_symbols_per_second_1h'] = avg_symbols_per_second
            
        elif component == "execution":
            avg_latency = sum(self.metrics[component][ts]['latency'] for ts in recent_timestamps) / len(recent_timestamps)
            
            # Update rolling average
            self.metrics[component]['avg_latency_1h'] = avg_latency
            
    def check_performance_thresholds(self, component):
        """Check metrics against defined thresholds"""
        if component == "scanner":
            # Check scan performance
            if 'avg_scan_time_1h' in self.metrics[component]:
                avg_scan_time = self.metrics[component]['avg_scan_time_1h']
                
                if avg_scan_time > self.config.MAX_SCAN_TIME:
                    log_warning(f"Scanner performance below threshold: {avg_scan_time:.2f}s > {self.config.MAX_SCAN_TIME}s")
                    
            if 'avg_symbols_per_second_1h' in self.metrics[component]:
                avg_symbols_per_second = self.metrics[component]['avg_symbols_per_second_1h']
                
                if avg_symbols_per_second < self.config.MIN_SYMBOLS_PER_SECOND:
                    log_warning(f"Scanner throughput below threshold: {avg_symbols_per_second:.2f} < {self.config.MIN_SYMBOLS_PER_SECOND}")
                    
        elif component == "execution":
            # Check execution latency
            if 'avg_latency_1h' in self.metrics[component]:
                avg_latency = self.metrics[component]['avg_latency_1h']
                
                if avg_latency > self.config.MAX_ORDER_LATENCY:
                    log_warning(f"Order execution latency above threshold: {avg_latency:.2f}s > {self.config.MAX_ORDER_LATENCY}s")
                    
    def get_performance_report(self):
        """Generate a comprehensive performance report"""
        report = {
            'uptime': time.time() - self.start_time,
            'components': {}
        }
        
        # Add scanner metrics
        if 'scanner' in self.metrics:
            report['components']['scanner'] = {
                'avg_scan_time_1h': self.metrics['scanner'].get('avg_scan_time_1h', 0),
                'avg_symbols_per_second_1h': self.metrics['scanner'].get('avg_symbols_per_second_1h', 0),
                'scan_count': len(self.metrics['scanner']) - 2,  # Subtract the two average keys
                'thresholds': {
                    'max_scan_time': self.config.MAX_SCAN_TIME,
                    'min_symbols_per_second': self.config.MIN_SYMBOLS_PER_SECOND
                }
            }
            
        # Add execution metrics
        if 'execution' in self.metrics:
            report['components']['execution'] = {
                'avg_latency_1h': self.metrics['execution'].get('avg_latency_1h', 0),
                'execution_count': len(self.metrics['execution']) - 1,  # Subtract the average key
                'thresholds': {
                    'max_order_latency': self.config.MAX_ORDER_LATENCY
                }
            }
            
        return report
```

### Cucumber Scenario for Performance Monitoring:

```gherkin
Feature: Performance Monitoring
  Scenario: Scanner performance threshold alert
    Given the scanner completes a scan of 500 symbols in 15 seconds
    When the performance monitor evaluates the metrics
    Then it should log a warning for scan time exceeding threshold
    And calculate the symbols per second as 33.33
    
  Scenario: Order execution latency monitoring
    Given an order is placed with an execution time of 0.8 seconds
    When the performance monitor records the latency
    Then it should log a warning for exceeding MAX_ORDER_LATENCY
    And update the average latency in the metrics
    
  Scenario: Performance report generation
    Given the system has been running for 24 hours
    When a performance report is requested
    Then it should include uptime, scanner metrics, and execution metrics
    And show all metrics compared to their respective thresholds
```

## 9. Alerting & Notifications System

```python
class AlertSystem:
    def __init__(self, config):
        self.config = config
        self.notification_channels = self.setup_channels()
        self.alert_history = []
        
    def setup_channels(self):
        channels = {}
        if self.config.USE_EMAIL_ALERTS:
            channels['email'] = EmailNotifier(self.config.EMAIL_SETTINGS)
        if self.config.USE_SMS_ALERTS:
            channels['sms'] = SMSNotifier(self.config.SMS_SETTINGS)
        if self.config.USE_SLACK_ALERTS:
            channels['slack'] = SlackNotifier(self.config.SLACK_SETTINGS)
        return channels
        
    def send_alert(self, message, details=None, severity="INFO", channels=None):
        if severity not in self.config.ALERT_LEVELS:
            severity = "INFO"
            
        # Determine which channels to use
        if channels is None:
            # Use default channels for this severity
            channels = self.config.SEVERITY_CHANNELS.get(severity, ["email"])
            
        # Format the alert
        formatted_alert = self.format_alert(message, details, severity)
        
        # Send through each channel
        for channel in channels:
            if channel in self.notification_channels:
                try:
                    self.notification_channels[channel].send(formatted_alert)
                except Exception as e:
                    log_error(f"Failed to send alert through {channel}", str(e))
                    
        # Record in history
        self.alert_history.append({
            'timestamp': datetime.now(),
            'message': message,
            'details': details,
            'severity': severity,
            'channels': channels
        })
                    
    def format_alert(self, message, details, severity):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{severity}] {timestamp} - {message}"
        if details:
            formatted += f"\nDetails: {details}"
        return formatted
        
    def send_trade_alert(self, action, symbol, direction, quantity, price=None, reason=None):
        """Send alert for trade actions"""
        message = f"Trade {action}: {symbol} {direction} x{quantity}"
        details = f"Price: {price if price else 'Market'}"
        
        if reason:
            details += f", Reason: {reason}"
            
        # Determine severity based on action
        severity = "INFO"
        if action == "ERROR":
            severity = "HIGH"
        elif action == "STOPPED":
            severity = "WARNING"
            
        self.send_alert(message, details, severity)
        
    def send_system_alert(self, component, status, details=None):
        """Send alert for system status"""
        message = f"System: {component} {status}"
        
        # Determine severity based on status
        severity = "INFO"
        if status == "ERROR" or status == "FAILED":
            severity = "HIGH"
        elif status == "WARNING":
            severity = "WARNING"
            
        self.send_alert(message, details, severity)
        
    def send_performance_alert(self, metric, value, threshold, details=None):
        """Send alert for performance issues"""
        message = f"Performance: {metric} {value} (threshold: {threshold})"
        
        # Always warning severity for performance
        severity = "WARNING"
        
        self.send_alert(message, details, severity)
```

### Cucumber Scenario for Alerting:

```gherkin
Feature: Alerting System
  Scenario: Trade execution alert
    Given a successful trade execution for "AAPL" LONG x2 contracts
    When the alert system sends a trade alert
    Then an "INFO" severity alert should be sent
    And the alert should contain the symbol, direction, and quantity
    
  Scenario: System error alert
    Given a system component "IBKR_API" has status "ERROR"
    When the alert system sends a system alert
    Then a "HIGH" severity alert should be sent
    And all configured channels for HIGH severity should receive the alert
    
  Scenario: Performance threshold alert
    Given scanner performance of 20 symbols per second
    And MIN_SYMBOLS_PER_SECOND is 50
    When the alert system sends a performance alert
    Then a "WARNING" severity alert should be sent
    And the alert should contain the current value and threshold
```

## 10. API Contract & gRPC Service Definition

```proto
syntax = "proto3";

package scanner;

service ScannerService {
  // Scan a list of symbols for trading signals
  rpc Scan (ScanRequest) returns (ScanResponse);
  
  // Fetch historical data for multiple symbols
  rpc BulkFetch (BulkFetchRequest) returns (BulkFetchResponse);
  
  // Get real-time performance metrics
  rpc GetMetrics (MetricsRequest) returns (MetricsResponse);
}

message DateRange {
  string start_date = 1;
  string end_date = 2;
}

message ScanRequest {
  repeated string symbols = 1;
  DateRange date_range = 2;
  repeated string strategies = 3;
}

message SignalList {
  repeated string signal_types = 1; // ["LONG", "SHORT"]
}

message ScanResponse {
  map<string, SignalList> signals = 1;
  float scan_time_seconds = 2;
}

message BulkFetchRequest {
  repeated string symbols = 1;
  string timeframe = 2; // "daily", "minute"
  DateRange date_range = 3;
}

message BulkFetchResponse {
  map<string, bytes> data = 1; // Serialized market data
  float fetch_time_seconds = 2;
}

message MetricsRequest {
  // Empty request
}

message MetricsResponse {
  float avg_scan_time_seconds = 1;
  float symbols_per_second = 2;
  int32 total_scans = 3;
  float memory_usage_mb = 4;
  float cpu_usage_percent = 5;
}
```

## 11. Go Scanner Implementation

```go
package main

import (
	"context"
	"sync"
	"time"

	"github.com/sirupsen/logrus"
	pb "github.com/your-org/auto-vertical-spread-trader/proto/scanner"
	"google.golang.org/grpc"
)

type ScannerService struct {
	config        *Config
	dataProvider  DataProvider
	metricTracker *MetricTracker
}

func NewScannerService(config *Config) *ScannerService {
	return &ScannerService{
		config:        config,
		dataProvider:  NewDataProvider(config),
		metricTracker: NewMetricTracker(),
	}
}

func (s *ScannerService) Scan(ctx context.Context, req *pb.ScanRequest) (*pb.ScanResponse, error) {
	startTime := time.Now()
	
	// Create result map
	signals := make(map[string]*pb.SignalList)
	var mu sync.Mutex
	
	// Create a worker pool to limit concurrency
	workerPool := make(chan struct{}, s.config.MaxConcurrency)
	var wg sync.WaitGroup
	
	// Process each symbol concurrently
	for _, symbol := range req.Symbols {
		wg.Add(1)
		
		// Add job to worker pool
		workerPool <- struct{}{}
		
		go func(sym string) {
			defer wg.Done()
			defer func() { <-workerPool }() // Release worker
			
			// Fetch data for this symbol
			data, err := s.dataProvider.GetHistoricalData(sym, req.DateRange.StartDate, req.DateRange.EndDate)
			if err != nil {
				logrus.Errorf("Error fetching data for %s: %v", sym, err)
				return
			}
			
			// Apply strategies
			signalTypes := s.evaluateStrategies(data, req.Strategies)
			
			// Store results with mutex to avoid race conditions
			if len(signalTypes) > 0 {
				mu.Lock()
				signals[sym] = &pb.SignalList{SignalTypes: signalTypes}
				mu.Unlock()
			}
		}(symbol)
	}
	
	// Wait for all goroutines to complete
	wg.Wait()
	close(workerPool)
	
	// Calculate scan time
	scanTime := time.Since(startTime).Seconds()
	
	// Track metrics
	s.metricTracker.RecordScan(len(req.Symbols), scanTime)
	
	return &pb.ScanResponse{
		Signals:         signals,
		ScanTimeSeconds: float32(scanTime),
	}, nil
}

func (s *ScannerService) BulkFetch(ctx context.Context, req *pb.BulkFetchRequest) (*pb.BulkFetchResponse, error) {
	startTime := time.Now()
	
	// Create result map
	data := make(map[string][]byte)
	var mu sync.Mutex
	
	// Create a worker pool
	workerPool := make(chan struct{}, s.config.MaxConcurrency)
	var wg sync.WaitGroup
	
	// Process each symbol concurrently
	for _, symbol := range req.Symbols {
		wg.Add(1)
		
		// Add job to worker pool
		workerPool <- struct{}{}
		
		go func(sym string) {
			defer wg.Done()
			defer func() { <-workerPool }() // Release worker
			
			// Fetch data for this symbol
			marketData, err := s.dataProvider.GetHistoricalData(sym, req.DateRange.StartDate, req.DateRange.EndDate)
			if err != nil {
				logrus.Errorf("Error fetching data for %s: %v", sym, err)
				return
			}
			
			// Serialize the data
			serialized, err := s.serializeMarketData(marketData)
			if err != nil {
				logrus.Errorf("Error serializing data for %s: %v", sym, err)
				return
			}
			
			// Store in result map
			mu.Lock()
			data[sym] = serialized
			mu.Unlock()
		}(symbol)
	}
	
	// Wait for all goroutines to complete
	wg.Wait()
	close(workerPool)
	
	// Calculate fetch time
	fetchTime := time.Since(startTime).Seconds()
	
	// Track metrics
	s.metricTracker.RecordFetch(len(req.Symbols), fetchTime)
	
	return &pb.BulkFetchResponse{
		Data:             data,
		FetchTimeSeconds: float32(fetchTime),
	}, nil
}

func (s *ScannerService) GetMetrics(ctx context.Context, req *pb.MetricsRequest) (*pb.MetricsResponse, error) {
	metrics := s.metricTracker.GetMetrics()
	
	return &pb.MetricsResponse{
		AvgScanTimeSeconds: float32(metrics.AvgScanTime),
		SymbolsPerSecond:   float32(metrics.SymbolsPerSecond),
		TotalScans:         int32(metrics.TotalScans),
		MemoryUsageMb:      float32(metrics.MemoryUsage),
		CpuUsagePercent:    float32(metrics.CPUUsage),
	}, nil
}

func (s *ScannerService) evaluateStrategies(data interface{}, strategies []string) []string {
	// Implementation depends on the data format and strategy definitions
	// This would evaluate indicators and apply trading rules
	
	// For now, return a placeholder
	return []string{"LONG"}
}

func (s *ScannerService) serializeMarketData(data interface{}) ([]byte, error) {
	// Implementation depends on the serialization format chosen
	// This could use protobuf, JSON, or a custom binary format
	
	// For now, return a placeholder
	return []byte{}, nil
}

func main() {
	// Load configuration
	config := LoadConfig()
	
	// Create scanner service
	service := NewScannerService(config)
	
	// Create gRPC server
	server := grpc.NewServer()
	pb.RegisterScannerServiceServer(server, service)
	
	// Start listening
	logrus.Infof("Starting scanner service on %s", config.ServerAddress)
	// Implementation of server listening and serving
}
```

## 12. Configuration Parameters

```python
class Config:
    """Centralized configuration with all parameters"""
    
    # Strategy Parameters
    HIGH_BASE_MAX_ATR_RATIO = 2.0
    HIGH_BASE_MIN_RSI = 60
    LOW_BASE_MIN_ATR_RATIO = 0.5
    LOW_BASE_MAX_RSI = 40
    BULL_PULLBACK_RSI_THRESHOLD = 45
    BEAR_RALLY_RSI_THRESHOLD = 55
    
    # Trade Execution Mode
    TRADING_MODE = "PAPER"  # Options: "PAPER" or "LIVE"
    PRICE_IMPROVEMENT_FACTOR = 0.4  # For live trading: 0.5 = midpoint, <0.5 = closer to bid, >0.5 = closer to ask
    
    # Risk Management Parameters
    MAX_POSITIONS = 5
    MAX_DAILY_TRADES = 3
    STOP_LOSS_ATR_MULT = 2.0
    RISK_PER_TRADE = 0.02  # 2% account risk per trade
    MAX_CONTRACTS_PER_TRADE = 10
    
    # Option Selection Parameters
    MIN_DTE = 30
    MAX_DTE = 45
    MIN_DELTA = 0.30
    MAX_DELTA = 0.50
    MAX_SPREAD_COST = 500
    MIN_REWARD_RISK = 1.5
    
    # Exit Strategy Parameters
    USE_FIBO_TARGETS = True
    FIBO_TARGET_LEVEL = 1.618
    USE_R_MULTIPLE = True
    R_MULTIPLE_TARGET = 2.0
    USE_ATR_TARGET = True
    ATR_TARGET_MULTIPLE = 3.0
    MIN_DAYS_TO_EXIT = 14
    
    # Universe Filtering
    MIN_MARKET_CAP = 10_000_000_000  # $10B
    MIN_PRICE = 20
    MIN_VOLUME = 1_000_000
    
    # Trade Execution Timing
    ALLOW_LATE_DAY_ENTRY = True
    
    # Performance Benchmarks
    MAX_SCAN_TIME = 5.0  # seconds
    MIN_SYMBOLS_PER_SECOND = 50
    MAX_ORDER_LATENCY = 0.5  # seconds
    CRITICAL_ORDER_LATENCY = 2.0  # seconds
    
    # Caching Parameters
    MINUTE_DATA_CACHE_EXPIRY = 60  # seconds
    UNIVERSE_CACHE_EXPIRY = 1800  # 30 minutes
    OPTIONS_CACHE_EXPIRY = 300  # 5 minutes
    
    # Error Handling
    ERROR_THRESHOLD = 3
    MAX_RECOVERY_ATTEMPTS = 2
    
    # Alerting Configuration
    ALERT_LEVELS = ["INFO", "WARNING", "HIGH", "CRITICAL"]
    SEVERITY_CHANNELS = {
        "INFO": ["email"],
        "WARNING": ["email", "slack"],
        "HIGH": ["email", "slack", "sms"],
        "CRITICAL": ["email", "slack", "sms"]
    }
    USE_EMAIL_ALERTS = True
    USE_SMS_ALERTS = True
    USE_SLACK_ALERTS = True
    
    # Backtesting Parameters
    INITIAL_EQUITY = 100000
    AVG_SPREAD_COST = 300
    AVG_REWARD_RISK = 1.8
    
    # Go Scanner Configuration
    GO_SCANNER_HOST = "localhost"
    GO_SCANNER_PORT = 50051
    MAX_CONCURRENCY = 50
```

## 13. Deployment & CI/CD

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install
      - name: Lint with black and mypy
        run: |
          poetry run black --check .
          poetry run mypy .
      - name: Run tests
        run: |
          poetry run pytest

  test-go:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Go
        uses: actions/setup-go@v3
        with:
          go-version: '1.20'
      - name: Install dependencies
        run: |
          go mod download
      - name: Run tests
        run: |
          go test -v ./...

  build-and-push:
    needs: [test-python, test-go]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
          
      - name: Build and push Python Orchestrator
        uses: docker/build-push-action@v4
        with:
          context: ./python
          push: true
          tags: your-org/vertical-spread-python:latest
          
      - name: Build and push Go Scanner
        uses: docker/build-push-action@v4
        with:
          context: ./go
          push: true
          tags: your-org/vertical-spread-go:latest
          
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Staging
        run: |
          # Deployment scripts using kubectl, Helm, etc.
          echo "Deploying to staging environment"
```

## 14. Docker Compose for Local Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  python-orchestrator:
    build:
      context: ./python
      dockerfile: Dockerfile.dev
    volumes:
      - ./python:/app
    ports:
      - "8000:8000"
    environment:
      - GO_SCANNER_HOST=go-scanner
      - GO_SCANNER_PORT=50051
    depends_on:
      - go-scanner
    restart: unless-stopped

  go-scanner:
    build:
      context: ./go
      dockerfile: Dockerfile.dev
    volumes:
      - ./go:/app
    ports:
      - "50051:50051"
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:v2.42.0
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:9.4.7
    volumes:
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  grafana-data:
```

## 15. Rollout Roadmap (Revised)

- Weeks 1-2

  :

  - Repo setup with Poetry, pytest, black, mypy
  - Core Python orchestrator implementation
    - Strategy implementations (all four core strategies)
    - Data management infrastructure
    - API contract definition via Protobuf
  - Backtesting framework foundation

- Weeks 3-4

  :

  - Go scanner service implementation
    - Concurrent symbol processing
    - Performance metrics and benchmarking
    - Data serialization and caching
  - Option selection logic implementation
  - Docker Compose for local development

- Weeks 5-6

  :

  - Risk management and position sizing
  - Exit strategies implementation
  - Trade execution timing constraints
  - Error handling and recovery mechanisms
  - Alerting and notification system

- Weeks 7-8

  :

  - Integration testing
  - Complete backtesting validation of all strategies
  - CI/CD pipeline implementation
  - Monitoring and observability with Prometheus/Grafana
  - Deployment scripts and documentation

## 16. Key Technical Decisions

1. **Python and Go Hybrid Architecture**:
   - Python for business logic, strategy implementation, and order management
   - Go for high-performance concurrent scanning
   - gRPC/Protobuf for typed interface between services
2. **Dependency Management**:
   - Poetry for Python dependency management
   - Docker containers for consistent environments
   - Minimal external dependencies (pandas-ta instead of TA-Lib)
3. **Performance Optimization**:
   - Efficient data caching strategy with expiry policies
   - Concurrent processing in Go
   - Benchmark-driven development with specific targets
4. **Testing and Quality**:
   - Cucumber/Gherkin scenarios for behavior specification
   - pytest for Python unit and integration testing
   - CI pipeline for continuous validation
5. **Monitoring and Observability**:
   - Structured JSON logging
   - Prometheus metrics for performance and health
   - Grafana dashboards for visualization

This comprehensive plan addresses all the feedback points while maintaining the Python-Go hybrid architecture. The implementation is now more robust with detailed specifications for all four trading strategies, explicit option selection logic, trade execution timing constraints, specific risk management parameters, comprehensive exit strategies, robust error handling, a prioritized backtesting framework, concrete performance metrics, an efficient data caching strategy, and a detailed alerting system.