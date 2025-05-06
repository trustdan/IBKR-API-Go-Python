# Auto Vertical Spread Trader - Project Intentions

## End-State Goals

The Auto Vertical Spread Trader aims to create a robust, production-ready automated trading system that:

1. **Automates Vertical Spread Trading** - Execute vertical option spreads based on technical setups with minimal human intervention
2. **Implements Four Core Strategies**:
   - **Bull Pullbacks**: Long call verticals on bullish stocks pulling back to 50-day MA
   - **Bear Rallies**: Long put verticals on bearish stocks rallying to 50-day MA
   - **High Base**: Long call verticals on stocks consolidating near 52-week highs
   - **Low Base**: Long put verticals on stocks consolidating near 52-week lows
3. **Manages Risk Automatically** - Implements ATR-based stop losses, position limits, and portfolio diversification
4. **Provides Monitoring & Alerting** - Sends notifications on entries, exits, and errors
5. **Offers Configurability** - Allows customization of parameters without code changes
6. **Ensures Reliability** - Handles connectivity issues, market data problems, and API limitations gracefully

## Plan of Attack

Our development approach follows these key phases:

1. **Universe Selection & Filtering**
   - Filter S&P 500 for stocks with sufficient market cap (≥$10B)
   - Filter for minimum price (>$20) and optionability
   - Implement volume filtering (≥1,000,000 daily volume)

2. **Technical Analysis Engine**
   - Fetch historical data with appropriate caching
   - Calculate key indicators (50 DMA, ATR, 52-week highs/lows)
   - Implement scans for each strategy with well-defined entry criteria

3. **Option Selection Logic**
   - Select liquid option contracts based on:
     - Target delta range (0.30-0.50)
     - Maximum cost ($500 per spread)
     - Minimum reward-to-risk ratio (≥1.0)
     - Maximum bid-ask spread (≤15% of mid-price)

4. **Trade Execution & Management**
   - Place trades at optimal times (after 3 PM ET)
   - Implement stop-loss monitoring based on ATR (2.0 × ATR)
   - Manage trade exits based on configurable profit target strategies

5. **System Architecture**
   - Create modular, testable components
   - Implement proper error handling and recovery
   - Allow for both automated and manual operation modes

## System Structure

The system is structured around these core components:

1. **Universe Management** (`universe.py`)
   - Loads S&P 500 tickers from local file or web source
   - Filters stocks based on market cap, price, and optionability
   - Manages the tradable universe with appropriate caching

2. **Technical Scanning** (`scans.py`)
   - Implements scan functions for all four strategies
   - Handles data fetching and indicator calculation
   - Provides parallelized scanning capabilities

3. **Trade Execution** (`executor.py`)
   - Selects optimal option contracts
   - Places vertical spread orders
   - Handles order management and status tracking

4. **Risk Management** (`exits.py`, `monitor.py`)
   - Implements stop-loss monitoring
   - Manages profit targets and exit strategies
   - Enforces position and portfolio limits

5. **Runner & Controller** (`runner.py`, `auto_vertical_spread_trader.py`)
   - Orchestrates the overall system flow
   - Handles scheduling and event-based triggers
   - Provides command-line interface and logging

## Key Parameters

The system is governed by these core parameters (from `config.py`):

### Universe Filters
- `MIN_MARKET_CAP`: $10 billion minimum market cap
- `MIN_PRICE`: $20 minimum stock price
- `MIN_VOLUME`: 1,000,000 minimum daily volume

### Option Parameters
- `TARGET_EXPIRY_INDEX`: 1 (next expiration cycle)
- `MIN_DELTA`: 0.30 (minimum absolute delta)
- `MAX_DELTA`: 0.50 (maximum absolute delta)
- `MAX_COST`: $500 (maximum spread cost)
- `MIN_REWARD_RISK_RATIO`: 1.0 (minimum reward-to-risk ratio)
- `MAX_BID_ASK_PCT`: 0.15 (maximum bid-ask spread as % of mid)

### Risk Management
- `STOP_LOSS_ATR_MULT`: 2.0 (ATR multiplier for stop-loss)
- `MAX_DAILY_TRADES`: 3 (maximum new trades per day)
- `MAX_POSITIONS`: 10 (maximum open positions)

### Pattern Parameters
- `HIGH_BASE_MAX_ATR_RATIO`: 0.8 (max ATR ratio for consolidation)
- `PRICE_NEAR_HIGH_PCT`: 0.95 (within 5% of 52-week high)
- `PRICE_NEAR_LOW_PCT`: 1.05 (within 5% of 52-week low)
- `TIGHT_RANGE_FACTOR`: 0.8 (daily range below 80% of average)

### Exit Strategies
- `USE_FIBONACCI_TARGETS`: True (use Fibonacci extensions)
- `FIBONACCI_EXTENSION`: 1.618 (golden ratio target)
- `USE_R_MULTIPLE_TARGETS`: False (alternative target strategy)
- `TARGET_R_MULTIPLE`: 2.0 (target as multiple of risk)
- `USE_ATR_TARGETS`: False (alternative target strategy)
- `TARGET_ATR_MULTIPLE`: 3.0 (target as multiple of ATR)

## TA-Lib Migration Status

We recently migrated from TA-Lib to pandas-ta for several important benefits:

1. **Simplified Installation**: No C/C++ dependencies required
2. **Cross-Platform Compatibility**: Works consistently across all OS platforms
3. **DataFrame-Centric API**: More intuitive and pythonic usage
4. **Extensive Indicator Library**: Access to 130+ technical indicators

### Key API Differences

```python
# TA-Lib (old):
import talib
df['ATR14'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
df['RSI14'] = talib.RSI(df['close'], timeperiod=14)

# pandas-ta (new):
import pandas_ta as ta
df['ATR14'] = df.ta.atr(length=14)
df['RSI14'] = df.ta.rsi(length=14)
```

## TA-Lib Installation Issues (Historical)

Prior to migration, we experienced several issues with TA-Lib installation that are now resolved by using pandas-ta. For reference, these included:

### 1. Symbol Issues in CI Builds
- **Problem**: Undefined symbol errors (TA_AVGDEV_Lookback) in CI
- **Root Cause**: Mismatch between C library and Python wrapper naming
- **Solution**: Created symlinks between naming conventions and added ldconfig calls

### 2. Ubuntu Package Availability
- **Problem**: "Unable to locate package libta-lib-dev" errors
- **Root Causes**: 
  - On Ubuntu 24.04+: Package unavailable in repositories
  - On Ubuntu 22.04: Universe repository not enabled in CI
  - In GitHub Actions: Azure mirror issues
- **Solutions**: Added repository switching and fallback build options

### 3. macOS Installation Path Issues
- **Problem**: Library not found on macOS, especially Apple Silicon
- **Root Cause**: Non-standard Homebrew install locations
- **Solution**: Dynamic prefix detection with proper flag setting

### 4. Windows Wheel Installation
- **Problem**: 404 errors downloading pre-built wheels
- **Root Cause**: URL format changes and version-specific wheels
- **Solution**: Dynamic version detection and fallback options

## Next Steps

1. **Performance Optimization**
   - Improve scanning speed with more efficient filtering
   - Enhance parallel processing for larger universes
   - Optimize caching strategies for data efficiency

2. **Extended Strategy Library**
   - Add momentum-based entry strategies
   - Implement earnings-based volatility strategies
   - Create sector-rotation overlay parameters

3. **Enhanced Monitoring & Reporting**
   - Develop comprehensive performance dashboard
   - Implement automated daily/weekly reports
   - Add alerting through additional channels (SMS, Slack, etc.)

4. **Improved Testing Framework**
   - Expand unit test coverage to all core components
   - Implement integration tests with IB simulated environment
   - Create backtesting framework for strategy evaluation

5. **Documentation & Deployment**
   - Complete user guide with installation instructions
   - Create administrator guide for system monitoring
   - Develop deployment scripts for cloud hosting 