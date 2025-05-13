from typing import Any, Dict, List, Optional, Tuple
import threading
import time
from datetime import datetime, date

from ib_insync import IB, util
from ib_insync import Contract, Stock, Option as IBOption, ComboLeg, TagValue
from ib_insync import Order, LimitOrder, MarketOrder
from ib_insync import Ticker, Trade, Position as IBPosition
import pytz

from src.app.config import Config
from src.models.option import Option, OptionSpread
from src.utils.logger import log_debug, log_error, log_info, log_warning


class IBKRIBInsyncApi:
    """Implementation of IBKR API using ib_insync library."""
    
    def __init__(self, config: Config):
        """Initialize the IBKR API client.

        Args:
            config: Application configuration
        """
        self.config = config
        self.connected = False
        
        # Connection details
        self.host = config.IBKR_HOST if hasattr(config, "IBKR_HOST") else "127.0.0.1"
        self.port = config.IBKR_PORT if hasattr(config, "IBKR_PORT") else 7497
        self.client_id = config.IBKR_CLIENT_ID if hasattr(config, "IBKR_CLIENT_ID") else 1
        self.account_id = config.IBKR_ACCOUNT_ID if hasattr(config, "IBKR_ACCOUNT_ID") else ""
        self.read_only = config.IBKR_READ_ONLY if hasattr(config, "IBKR_READ_ONLY") else False
        
        # Create IB instance
        self.ib = IB()
        
        # Order tracking
        self.next_order_id = 1
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.positions: Dict[str, Dict[str, Any]] = {}

        # Lock for thread safety
        self.lock = threading.Lock() 

    def _setup_event_handlers(self):
        """Set up event handlers for IB events."""
        
        # Handle connection status
        self.ib.connectedEvent += self._on_connected
        self.ib.disconnectedEvent += self._on_disconnected
        
        # Handle order status changes
        self.ib.orderStatusEvent += self._on_order_status
        
        # Handle execution details (fills)
        self.ib.execDetailsEvent += self._on_execution
        self.ib.commissionReportEvent += self._on_commission_report
        
        # Handle position updates
        self.ib.positionEvent += self._on_position
        
        # Error handling
        self.ib.errorEvent += self._on_error

    def _on_connected(self):
        """Handle connection event."""
        self.connected = True
        log_info("Connection to IBKR established")

    def _on_disconnected(self):
        """Handle disconnection events."""
        self.connected = False
        log_warning("Disconnected from IBKR")

    def _on_order_status(self, trade):
        """Handle order status updates."""
        order_id = str(trade.order.orderId)
        
        with self.lock:
            if order_id in self.orders:
                order_info = self.orders[order_id]
                order_info["status"] = trade.orderStatus.status
                order_info["filled"] = trade.orderStatus.filled
                order_info["remaining"] = trade.orderStatus.remaining
                
                log_debug(f"Order {order_id} status: {trade.orderStatus.status}")

    def _on_execution(self, trade, fill):
        """Handle order executions (fills)."""
        order_id = str(trade.order.orderId)
        
        with self.lock:
            if order_id in self.orders:
                order_info = self.orders[order_id]
                order_info["status"] = trade.orderStatus.status
                
                # Track the execution
                if "executions" not in order_info:
                    order_info["executions"] = []
                
                order_info["executions"].append({
                    "time": fill.execution.time,
                    "shares": fill.execution.shares,
                    "price": fill.execution.price,
                    "execution_id": fill.execution.execId
                })
                
                log_info(f"Order {order_id} fill: {fill.execution.shares} shares at ${fill.execution.price:.2f}")

    def _on_commission_report(self, trade, fill, report):
        """Handle commission reports."""
        order_id = str(trade.order.orderId)
        
        with self.lock:
            if order_id in self.orders:
                order_info = self.orders[order_id]
                
                # Update commission info
                if "commissions" not in order_info:
                    order_info["commissions"] = []
                
                order_info["commissions"].append({
                    "execution_id": report.execId,
                    "commission": report.commission,
                    "currency": report.currency,
                    "realized_pnl": report.realizedPNL
                })

    def _on_position(self, position):
        """Handle position updates."""
        with self.lock:
            symbol = position.contract.symbol
            
            if symbol not in self.positions:
                self.positions[symbol] = {
                    "quantity": 0,
                    "avg_price": 0,
                    "market_price": 0,
                    "market_value": 0,
                    "unrealized_pnl": 0,
                    "realized_pnl": 0,
                    "account": position.account,
                    "trades": []
                }
            
            # Update position
            self.positions[symbol]["quantity"] = position.position
            self.positions[symbol]["avg_price"] = position.avgCost
            
            # Try to get market price and value if available
            if hasattr(position, 'marketPrice') and not util.isNan(position.marketPrice):
                self.positions[symbol]["market_price"] = position.marketPrice
            
            if hasattr(position, 'marketValue') and not util.isNan(position.marketValue):
                self.positions[symbol]["market_value"] = position.marketValue
            
            log_debug(f"Position update: {symbol}, {position.position} shares, avg cost ${position.avgCost:.2f}")

    def _on_error(self, reqId, errorCode, errorString, contract):
        """Handle error events."""
        if errorCode in (502, 504):  # Connection issues
            log_error(f"IBKR connection error: {errorString}")
            self.connected = False
        elif errorCode == 2104 or errorCode == 2106:  # Market data farm connection
            log_warning(f"IBKR market data warning: {errorString}")
        elif errorCode == 1100:  # Connection lost
            log_error("IBKR connection lost")
            self.connected = False
        elif errorCode == 1300:  # TWS or Gateway not running
            log_error("IBKR TWS/Gateway not running")
            self.connected = False
        else:
            log_error(f"IBKR error {errorCode}: {errorString}, reqId: {reqId}")
    
    def connect(self) -> bool:
        """Connect to the IBKR TWS/Gateway.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            log_info(f"Connecting to IBKR at {self.host}:{self.port} with client ID {self.client_id}")
            
            # Connect to IB with timeout and retry logic
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    self.ib.connect(
                        host=self.host,
                        port=self.port,
                        clientId=self.client_id,
                        readonly=self.read_only,
                        account=self.account_id,
                        timeout=20  # 20 second timeout
                    )
                    break  # Connection successful
                except Exception as e:
                    if attempt < max_attempts:
                        log_warning(f"Connection attempt {attempt} failed: {str(e)}. Retrying...")
                        time.sleep(2)  # Wait before retrying
                    else:
                        raise  # Re-raise the exception if all attempts failed
            
            # Check if really connected
            if self.ib.isConnected():
                self.connected = True
                log_info("Successfully connected to IBKR")
                
                # Set up event handlers
                self._setup_event_handlers()
                
                # Request account updates
                if self.account_id:
                    self.ib.reqAccountUpdates(True, self.account_id)
                
                # Initialize managed accounts if account not specified
                if not self.account_id and self.ib.managedAccounts():
                    self.account_id = self.ib.managedAccounts()[0]
                    log_info(f"Using account: {self.account_id}")
                
                # Get the next valid order ID
                self.next_order_id = self.ib.client.getReqId()
                
                return True
            else:
                log_error("Failed to connect to IBKR")
                return False
        except Exception as e:
            log_error(f"Failed to connect to IBKR: {str(e)}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from the IBKR TWS/Gateway."""
        try:
            if self.connected:
                # Cancel any subscriptions if needed
                # self.ib.cancelPositions()
                # self.ib.cancelAccountUpdates()
                
                self.ib.disconnect()
                log_info("Disconnected from IBKR")
                self.connected = False
        except Exception as e:
            log_error(f"Error disconnecting from IBKR: {str(e)}")
            self.connected = False

    def handle_callbacks(self) -> None:
        """Process IB API callbacks.
        
        This should be called periodically to ensure the IB API works properly.
        """
        if self.connected:
            try:
                self.ib.sleep(0)  # Allow IB to process messages
            except Exception as e:
                log_error(f"Error handling callbacks: {str(e)}")
                
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time market data for a symbol.
        
        Args:
            symbol: Symbol to get data for
            
        Returns:
            Market data dictionary
        """
        if not self.connected:
            log_warning("Not connected to IBKR when requesting market data")
            return {
                "symbol": symbol,
                "error": "Not connected"
            }
        
        try:
            # Create contract
            contract = Stock(symbol, 'SMART', 'USD')
            
            # Qualify contract
            try:
                qualified_contracts = self.ib.qualifyContracts(contract)
                if not qualified_contracts:
                    log_error(f"Could not qualify contract for {symbol}")
                    return {
                        "symbol": symbol,
                        "error": "Invalid symbol"
                    }
                contract = qualified_contracts[0]
            except Exception as e:
                log_error(f"Error qualifying contract for {symbol}: {str(e)}")
                return {
                    "symbol": symbol,
                    "error": f"Invalid symbol: {str(e)}"
                }
            
            # Request market data
            ticker = self.ib.reqMktData(contract)
            
            # Wait for data to arrive
            timeout = 3  # seconds
            for _ in range(timeout * 10):  # Check every 0.1 seconds
                self.ib.sleep(0.1)
                if not (util.isNan(ticker.last) and util.isNan(ticker.bid) and util.isNan(ticker.ask)):
                    break
            
            # Gather data
            data = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "last": ticker.last if not util.isNan(ticker.last) else None,
                "bid": ticker.bid if not util.isNan(ticker.bid) else None,
                "ask": ticker.ask if not util.isNan(ticker.ask) else None,
                "volume": ticker.volume if not util.isNan(ticker.volume) else None,
                "high": ticker.high if not util.isNan(ticker.high) else None,
                "low": ticker.low if not util.isNan(ticker.low) else None,
                "close": ticker.close if not util.isNan(ticker.close) else None,
            }
            
            # Cancel market data to conserve resources
            self.ib.cancelMktData(contract)
            
            return data
        
        except Exception as e:
            log_error(f"Error getting market data for {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "error": str(e)
            }

    def get_option_chain(self, symbol: str) -> List[Option]:
        """Get the full option chain for a symbol.
        
        Args:
            symbol: Underlying symbol
            
        Returns:
            List of options
        """
        if not self.connected:
            log_error("Not connected to IBKR")
            return []
        
        try:
            # Create stock contract
            contract = Stock(symbol, 'SMART', 'USD')
            
            # Qualify contract
            try:
                qualified_contracts = self.ib.qualifyContracts(contract)
                if not qualified_contracts:
                    log_error(f"Could not qualify contract for {symbol}")
                    return []
                contract = qualified_contracts[0]
            except Exception as e:
                log_error(f"Error qualifying contract for {symbol}: {str(e)}")
                return []
            
            # Request contract details to get contract ID
            details = self.ib.reqContractDetails(contract)
            
            if not details:
                log_error(f"No contract details found for {symbol}")
                return []
            
            # Request option chain parameters
            chains = self.ib.reqSecDefOptParams(
                underlyingSymbol=symbol, 
                futFopExchange='', 
                underlyingSecType='STK', 
                underlyingConId=contract.conId
            )
            
            if not chains:
                log_error(f"No option chains found for {symbol}")
                return []
            
            # Get first chain (usually there's only one)
            chain = chains[0]
            
            # Get current price for determining which strikes to include
            market_data = self.get_market_data(symbol)
            current_price = market_data.get('last')
            if current_price is None:
                current_price = market_data.get('bid', 0)
                if current_price is None:
                    current_price = market_data.get('ask', 100.0)
                    if current_price is None:
                        current_price = 100.0  # Default if no price available
            
            # Create a list to store all options
            options = []
            
            # Define how many expirations and strikes to include
            max_expirations = 4  # Limit number of expirations to reduce API load
            max_strikes_per_expiry_and_type = 6  # Limit number of strikes per expiration and type
            
            # Request each expiration
            for expiration in chain.expirations[:max_expirations]:
                for right in ['C', 'P']:  # Calls and puts
                    # Get strikes around ATM
                    price_range = 0.3  # Get strikes within 30% of current price
                    min_strike = current_price * (1 - price_range)
                    max_strike = current_price * (1 + price_range)
                    
                    relevant_strikes = [
                        strike for strike in chain.strikes 
                        if min_strike <= strike <= max_strike
                    ]
                    
                    # If we have too many strikes, select a subset centered around ATM
                    if len(relevant_strikes) > max_strikes_per_expiry_and_type:
                        # Sort strikes
                        relevant_strikes.sort(key=lambda x: abs(x - current_price))
                        relevant_strikes = relevant_strikes[:max_strikes_per_expiry_and_type]
                        # Sort back to normal order
                        relevant_strikes.sort()
                    
                    # Process each strike
                    for strike in relevant_strikes:
                        # Create option contract
                        option_contract = IBOption(
                            symbol=symbol,
                            lastTradeDateOrContractMonth=expiration,
                            strike=strike,
                            right=right,
                            exchange=chain.exchange
                        )
                        
                        try:
                            # Qualify the contract
                            qualified_options = self.ib.qualifyContracts(option_contract)
                            
                            if not qualified_options:
                                continue
                            
                            qualified_option = qualified_options[0]
                            
                            # Request market data
                            ticker = self.ib.reqMktData(qualified_option, '', False, False)
                            
                            # Wait for market data to arrive (with timeout)
                            timeout = 1  # seconds
                            for _ in range(timeout * 10):  # Check every 0.1 seconds
                                self.ib.sleep(0.1)
                                if not (util.isNan(ticker.last) and util.isNan(ticker.bid) and util.isNan(ticker.ask)):
                                    break
                            
                            # Convert to our Option model
                            exp_date = datetime.strptime(expiration, '%Y%m%d').date()
                            
                            # Extract implied volatility and greeks
                            implied_vol = ticker.impliedVolatility if hasattr(ticker, 'impliedVolatility') and not util.isNan(ticker.impliedVolatility) else 0.0
                            
                            # Get greeks from model or compute them
                            delta = gamma = theta = vega = rho = 0.0
                            
                            if hasattr(ticker, 'modelGreeks') and ticker.modelGreeks:
                                delta = ticker.modelGreeks.delta if not util.isNan(ticker.modelGreeks.delta) else 0.0
                                gamma = ticker.modelGreeks.gamma if not util.isNan(ticker.modelGreeks.gamma) else 0.0
                                theta = ticker.modelGreeks.theta if not util.isNan(ticker.modelGreeks.theta) else 0.0
                                vega = ticker.modelGreeks.vega if not util.isNan(ticker.modelGreeks.vega) else 0.0
                                rho = ticker.modelGreeks.rho if not util.isNan(ticker.modelGreeks.rho) else 0.0
                            
                            option = Option(
                                symbol=qualified_option.localSymbol,
                                underlying=symbol,
                                option_type="call" if right == 'C' else "put",
                                strike=strike,
                                expiration=exp_date,
                                bid=ticker.bid if not util.isNan(ticker.bid) else 0.0,
                                ask=ticker.ask if not util.isNan(ticker.ask) else 0.0,
                                last=ticker.last if not util.isNan(ticker.last) else 0.0,
                                volume=int(ticker.volume) if not util.isNan(ticker.volume) else 0,
                                open_interest=int(ticker.openInterest) if hasattr(ticker, 'openInterest') and not util.isNan(ticker.openInterest) else 0,
                                implied_volatility=implied_vol,
                                delta=delta,
                                gamma=gamma,
                                theta=theta,
                                vega=vega,
                                rho=rho
                            )
                            
                            options.append(option)
                            
                            # Cancel market data to conserve resources
                            self.ib.cancelMktData(qualified_option)
                        
                        except Exception as e:
                            log_warning(f"Error processing option {symbol} {expiration} {right} {strike}: {str(e)}")
                            continue
            
            log_info(f"Retrieved {len(options)} options for {symbol}")
            return options
        
        except Exception as e:
            log_error(f"Error getting option chain for {symbol}: {str(e)}")
            return []

    def get_next_order_id(self) -> int:
        """Get the next available order ID.
        
        Returns:
            Next order ID
        """
        with self.lock:
            order_id = self.next_order_id
            self.next_order_id += 1
            return order_id

    def place_order(
        self,
        symbol: str,
        direction: str,
        contracts: int,
        option_spread: OptionSpread,
        price_type: str = "LIMIT",
        limit_price: Optional[float] = None,
    ) -> str:
        """Place an option spread order.
        
        Args:
            symbol: Underlying symbol
            direction: Trade direction ("LONG" or "SHORT")
            contracts: Number of contracts to trade
            option_spread: The option spread to trade
            price_type: Order type ("MARKET" or "LIMIT")
            limit_price: Limit price if price_type is "LIMIT"
            
        Returns:
            Order ID string
            
        Raises:
            ValueError: If not connected or invalid parameters
            RuntimeError: If order placement fails
        """
        if not self.connected:
            raise ValueError("Not connected to IBKR")
        
        # Validate parameters
        if contracts <= 0:
            raise ValueError(f"Invalid number of contracts: {contracts}")
        
        if price_type == "LIMIT" and limit_price is None:
            raise ValueError("Limit price required for LIMIT orders")
        
        try:
            # Create contract objects for legs
            expiry = option_spread.expiration.strftime("%Y%m%d")
            
            # Create contracts based on spread type and direction
            if option_spread.spread_type == "BULL_CALL":
                # For bull call spread: Buy lower strike call, sell higher strike call
                long_option_type = 'C'
                short_option_type = 'C'
                long_strike = option_spread.long_leg.strike
                short_strike = option_spread.short_leg.strike
            elif option_spread.spread_type == "BEAR_PUT":
                # For bear put spread: Buy higher strike put, sell lower strike put
                long_option_type = 'P'
                short_option_type = 'P'
                long_strike = option_spread.long_leg.strike
                short_strike = option_spread.short_leg.strike
            else:
                raise ValueError(f"Unsupported spread type: {option_spread.spread_type}")
            
            # Create option contracts
            long_contract = IBOption(
                symbol, 
                expiry, 
                long_strike, 
                long_option_type,
                exchange='SMART', 
                currency='USD'
            )
            
            short_contract = IBOption(
                symbol, 
                expiry, 
                short_strike, 
                short_option_type,
                exchange='SMART', 
                currency='USD'
            )
            
            # Qualify the contracts to get their conIds
            try:
                qualified_long = self.ib.qualifyContracts(long_contract)[0]
                qualified_short = self.ib.qualifyContracts(short_contract)[0]
            except Exception as e:
                log_error(f"Failed to qualify option contracts: {str(e)}")
                raise ValueError("Invalid option contracts")
            
            # Create bag contract for the spread
            bag = Contract()
            bag.symbol = symbol
            bag.secType = 'BAG'
            bag.currency = 'USD'
            bag.exchange = 'SMART'
            
            # Define the legs
            leg1 = ComboLeg()
            leg1.conId = qualified_long.conId
            leg1.ratio = 1
            leg1.action = 'BUY' if direction == 'LONG' else 'SELL'
            leg1.exchange = 'SMART'
            
            leg2 = ComboLeg()
            leg2.conId = qualified_short.conId
            leg2.ratio = 1
            leg2.action = 'SELL' if direction == 'LONG' else 'BUY'
            leg2.exchange = 'SMART'
            
            bag.comboLegs = [leg1, leg2]
            
            # Create order
            if price_type == "LIMIT":
                order = LimitOrder(
                    'BUY' if direction == 'LONG' else 'SELL',
                    contracts,
                    limit_price
                )
            else:  # MARKET
                order = MarketOrder(
                    'BUY' if direction == 'LONG' else 'SELL',
                    contracts
                )
            
            # Set order properties
            order.orderRef = f"{option_spread.spread_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            order.transmit = True  # Transmit order immediately
            
            # Place the order
            trade = self.ib.placeOrder(bag, order)
            order_id = str(trade.order.orderId)
            
            # Store the order details
            with self.lock:
                self.orders[order_id] = {
                    "id": order_id,
                    "symbol": symbol,
                    "direction": direction,
                    "contracts": contracts,
                    "spread_type": option_spread.spread_type,
                    "price_type": price_type,
                    "limit_price": limit_price,
                    "status": trade.orderStatus.status,
                    "filled_price": None,
                    "submit_time": datetime.now(),
                    "fill_time": None,
                    "trade": trade,
                    "option_spread": {
                        "long_strike": long_strike,
                        "short_strike": short_strike,
                        "expiration": expiry,
                        "option_type": long_option_type if option_spread.spread_type == "BULL_CALL" else short_option_type
                    }
                }
            
            log_info(
                f"Placed order #{order_id}: {symbol} {direction} {contracts} contracts "
                f"of {option_spread.spread_type} at {price_type} "
                f"price {'$' + str(limit_price) if limit_price else 'MARKET'}"
            )
            
            return order_id
        
        except Exception as e:
            log_error(f"Error placing order: {str(e)}")
            raise RuntimeError(f"Order placement failed: {str(e)}")

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get the status of an order.
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Order status details or empty dict if not found
        """
        with self.lock:
            if order_id not in self.orders:
                return {}
            
            order_info = self.orders[order_id].copy()
            trade = order_info.get("trade")
            
            if trade:
                # Update status from trade object
                order_info["status"] = trade.orderStatus.status
                order_info["filled"] = trade.orderStatus.filled
                order_info["remaining"] = trade.orderStatus.remaining
                
                if trade.orderStatus.status == 'Filled':
                    order_info["filled_price"] = trade.orderStatus.avgFillPrice
                    if not order_info.get("fill_time"):
                        order_info["fill_time"] = datetime.now()
                
                # Don't return the trade object in the dict
                if "trade" in order_info:
                    del order_info["trade"]
            
            return order_info

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if cancel successful, False otherwise
        """
        try:
            if not self.connected:
                log_warning("Not connected to IBKR when attempting to cancel order")
                return False
            
            with self.lock:
                if order_id not in self.orders:
                    log_warning(f"Order {order_id} not found when attempting to cancel")
                    return False
                
                order_info = self.orders[order_id]
                trade = order_info.get("trade")
                
                if not trade:
                    log_warning(f"Trade object not found for order {order_id}")
                    return False
                
                order_status = trade.orderStatus.status
                if order_status in ['Filled', 'Cancelled', 'ApiCancelled']:
                    log_warning(f"Cannot cancel order {order_id} with status {order_status}")
                    return False
                
                # Cancel the order
                self.ib.cancelOrder(trade.order)
                log_info(f"Cancellation request sent for order {order_id}")
                
                # Wait briefly for cancellation to process
                for _ in range(5):  # Try for up to 5 * 0.2 = 1 second
                    self.ib.sleep(0.2)
                    # Check if cancelled
                    if trade.orderStatus.status in ['Cancelled', 'ApiCancelled']:
                        log_info(f"Order {order_id} successfully cancelled")
                        order_info["status"] = trade.orderStatus.status
                        return True
                
                # If we get here, we didn't see the cancellation confirmed
                log_warning(f"Order {order_id} cancellation request sent but not confirmed")
                return True  # Return true since we sent the request
            
        except Exception as e:
            log_error(f"Error cancelling order {order_id}: {str(e)}")
            return False

    def get_account_summary(self) -> Dict[str, Any]:
        """Get account summary data.
        
        Returns:
            Account summary information
        """
        if not self.connected:
            return {
                "error": "Not connected to IBKR",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Get account values
            account_values = self.ib.accountValues()
            
            # Extract the values we want
            summary = {
                "timestamp": datetime.now().isoformat(),
                "account_id": self.account_id
            }
            
            # Log all available tags for debugging
            log_debug(f"Account values received: {len(account_values)}")
            all_tags = set()
            for val in account_values:
                all_tags.add(val.tag)
                if val.currency == "USD":
                    log_debug(f"Found tag: {val.tag} = {val.value} {val.currency}")
            
            log_debug(f"Available account value tags: {sorted(list(all_tags))}")
            
            # Map of tag names to our key names
            account_fields = {
                "NetLiquidation": "net_liquidation",
                "CashBalance": "cash_balance",
                "EquityWithLoanValue": "equity_with_loan",
                "InitMarginReq": "initial_margin_req",
                "MaintMarginReq": "maintenance_margin_req",
                "AvailableFunds": "available_funds",
                "ExcessLiquidity": "excess_liquidity",
                "BuyingPower": "buying_power",
                "DayTradesRemaining": "day_trades_remaining",
                "GrossPositionValue": "gross_position_value",
                "TotalCashValue": "total_cash_value",
                # Add additional mappings that might be present in TWS
                "TotalCashBalance": "total_cash_balance",
                "AccruedCash": "accrued_cash",
                "FullAvailableFunds": "full_available_funds",
                "FullExcessLiquidity": "full_excess_liquidity",
                "FullInitMarginReq": "full_init_margin_req",
                "FullMaintMarginReq": "full_maint_margin_req",
                "FuturesPNL": "futures_pnl",
                "LookAheadAvailableFunds": "look_ahead_available_funds",
                "LookAheadExcessLiquidity": "look_ahead_excess_liquidity",
                "LookAheadInitMarginReq": "look_ahead_init_margin_req",
                "LookAheadMaintMarginReq": "look_ahead_maint_margin_req",
                "OptionMarketValue": "option_market_value",
                "StockMarketValue": "stock_market_value",
                "UnrealizedPnL": "unrealized_pnl",
                "RealizedPnL": "realized_pnl"
            }
            
            # Initialize with None values
            for value in account_fields.values():
                summary[value] = None
                
            # Fill in the values we have
            for value in account_values:
                # Only use USD values for now
                if value.currency != "USD":
                    continue
                    
                # Map the tag to our field name
                if value.tag in account_fields:
                    field_name = account_fields[value.tag]
                    
                    # Try to convert to float if possible
                    try:
                        summary[field_name] = float(value.value)
                    except ValueError:
                        summary[field_name] = value.value
            
            # Request portfolio directly to get positions value
            portfolio = self.ib.portfolio()
            if portfolio:
                total_value = sum(item.marketValue for item in portfolio if not util.isNan(item.marketValue))
                summary["portfolio_value"] = total_value
                log_debug(f"Portfolio market value: ${total_value:.2f}")
            
            log_info(f"Account summary: Net Liquidation=${summary.get('net_liquidation', 0):.2f}, " +
                     f"Equity=${summary.get('equity_with_loan', 0):.2f}, " +
                     f"Buying Power=${summary.get('buying_power', 0):.2f}")
            
            return summary
        except Exception as e:
            log_error(f"Error getting account summary: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get current positions.
        
        Returns:
            Dictionary of positions by symbol
        """
        with self.lock:
            if not self.connected:
                return {}
            
            # If we already have positions, return what we have
            if self.positions:
                return self.positions.copy()
            
            try:
                # Request positions from TWS
                ib_positions = self.ib.positions()
                positions = {}
                
                # Convert IB positions to our format
                for pos in ib_positions:
                    symbol = pos.contract.symbol
                    
                    if symbol not in positions:
                        positions[symbol] = {
                            "symbol": symbol,
                            "quantity": 0,
                            "avg_price": 0,
                            "market_price": 0,
                            "market_value": 0,
                            "unrealized_pnl": 0,
                            "realized_pnl": 0,
                            "account": pos.account,
                            "trades": []
                        }
                    
                    # Update position
                    positions[symbol]["quantity"] += pos.position
                    positions[symbol]["avg_price"] = pos.avgCost
                    
                    # Try to get market price and value
                    if hasattr(pos, 'marketPrice') and not util.isNan(pos.marketPrice):
                        positions[symbol]["market_price"] = pos.marketPrice
                        
                    if hasattr(pos, 'marketValue') and not util.isNan(pos.marketValue):
                        positions[symbol]["market_value"] = pos.marketValue
                
                # Store for future use
                self.positions = positions
                
                return positions.copy()
            
            except Exception as e:
                log_error(f"Error getting positions: {str(e)}")
                return {} 