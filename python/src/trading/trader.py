from typing import Dict, List, Optional, Tuple, Any
import queue
import threading
import time
from datetime import datetime

from src.app.config import Config
from src.models.signals import Signal
from src.models.trades import Trade
from src.trading.scanner_client import ScannerClient
from src.trading.option_selector import OptionSelector
from src.trading.risk_manager import RiskManager
from src.trading.trade_executor import TradeExecutor
from src.utils.logger import log_debug, log_error, log_info, log_warning


class Trader:
    """Main trading controller class."""

    def __init__(self, config_file: str = "config.yaml"):
        """Initialize the trader.

        Args:
            config_file: Path to configuration file
        """
        # Load configuration
        self.config = Config.from_yaml(config_file)
        log_info(f"Initialized trader with {self.config.TRADING_MODE} mode")
        
        # Check if we should use ib_insync
        use_ib_insync = getattr(self.config, "USE_IB_INSYNC", True)
        
        # Connect to IBKR using the appropriate implementation
        from src.brokers import get_broker_api
        self.broker_api = get_broker_api(self.config, use_ib_insync=use_ib_insync)
        
        # Attempt to connect
        connected = self.broker_api.connect()
        if not connected:
            log_error("Failed to connect to IBKR, some functionality may be limited")
        
        # Initialize components with the broker API
        self.scanner = ScannerClient(self.config.SCANNER_HOST, self.config.SCANNER_PORT)
        self.option_selector = OptionSelector(self.config)
        self.risk_manager = RiskManager(self.config, self.broker_api)
        self.trade_executor = TradeExecutor(self.config, self.broker_api)

        # Signal processing queue
        self.signal_queue = queue.Queue()
        self.processing = False
        self.processing_thread = None
        
        # Start processing thread if autostart enabled
        if getattr(self.config, "AUTOSTART_PROCESSING", False):
            self.start_processing()

    def start_processing(self) -> None:
        """Start the signal processing thread."""
        if not self.processing:
            self.processing = True
            self.processing_thread = threading.Thread(target=self._process_signals_thread)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            log_info("Started signal processing thread")

    def stop_processing(self) -> None:
        """Stop the signal processing thread."""
        if self.processing:
            self.processing = False
            if self.processing_thread:
                self.processing_thread.join(timeout=5.0)
            log_info("Stopped signal processing thread")

    def _process_signals_thread(self) -> None:
        """Background thread for processing signals from the queue."""
        while self.processing:
            try:
                # Process any queued signals with a timeout
                try:
                    signal = self.signal_queue.get(timeout=1.0)
                    status, result = self.process_signal(signal)
                    log_debug(f"Signal processing result: {status} - {result}")
                    self.signal_queue.task_done()
                except queue.Empty:
                    # No signals to process
                    pass
                    
                # Process IB callbacks to keep connection alive
                if self.broker_api and hasattr(self.broker_api, 'handle_callbacks'):
                    self.broker_api.handle_callbacks()
                    
                # Periodically update positions from broker
                self.risk_manager.update_positions_from_broker()

                # Process any queued trades
                self.trade_executor.process_queued_trades()
                    
                # Sleep to avoid excessive CPU usage
                time.sleep(0.1)
            except Exception as e:
                log_error(f"Error in signal processing thread: {str(e)}")

    def process_signal(self, signal: Signal) -> Tuple[bool, Dict[str, Any]]:
        """Process a trading signal.
        
        Args:
            signal: Trading signal to process
            
        Returns:
            Tuple of (success, result_info)
        """
        try:
            log_info(f"Processing signal: {signal}")
            
            # 1. Check if we're allowed to trade this symbol based on risk rules
            if not self.risk_manager.can_trade_symbol(signal.symbol):
                return False, {"error": f"Risk management rejected trading {signal.symbol}"}
            
            # 2. Get current market data
            market_data = self.broker_api.get_market_data(signal.symbol)
            if "error" in market_data:
                return False, {"error": f"Could not get market data: {market_data['error']}"}
            
            current_price = market_data.get("last") or market_data.get("bid")
            if not current_price:
                return False, {"error": "Could not determine current price"}
            
            # 3. Select appropriate option spread
            option_spread = self.option_selector.select_vertical_spread(
                signal.symbol, signal.direction, current_price
            )
            
            if not option_spread:
                return False, {"error": "Could not find suitable option spread"}
            
            # 4. Create and execute trade
            trade = Trade(
                signal=signal,
                option_spread=option_spread,
                entry_time=datetime.now(),
                status="PENDING"
            )
            
            # Queue the trade for execution
            success = self.trade_executor.queue_trade(trade)
            
            if success:
                return True, {"trade_id": trade.id, "option_spread": str(option_spread)}
            else:
                return False, {"error": "Failed to queue trade for execution"}
            
        except Exception as e:
            log_error(f"Error processing signal: {str(e)}")
            return False, {"error": str(e)}
            
    def add_signal(self, signal: Signal) -> bool:
        """Add a signal to the processing queue.
        
        Args:
            signal: Trading signal to add
            
        Returns:
            True if successfully added
        """
        try:
            self.signal_queue.put(signal)
            return True
        except Exception as e:
            log_error(f"Error adding signal to queue: {str(e)}")
            return False
            
    def get_account_summary(self) -> Dict[str, Any]:
        """Get current account summary.
        
        Returns:
            Account summary information
        """
        if not self.broker_api:
            return {"error": "Broker API not initialized"}
            
        if hasattr(self.broker_api, 'get_account_summary'):
            return self.broker_api.get_account_summary()
        else:
            return {"error": "Account summary not supported by broker API"}
            
    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get current positions.
        
        Returns:
            Dictionary of positions by symbol
        """
        if not self.broker_api:
            return {}
            
        if hasattr(self.broker_api, 'get_positions'):
            return self.broker_api.get_positions()
        else:
            return {}
            
    def debug_account_info(self) -> Dict[str, Any]:
        """Get comprehensive account debugging information.
        
        Returns:
            Dictionary with account and debugging info
        """
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "connected": False,
            "connection_details": {},
            "account_summary": {},
            "positions": {}
        }
        
        if not self.broker_api:
            debug_info["error"] = "Broker API not initialized"
            return debug_info
        
        # Get connection status
        if hasattr(self.broker_api, 'connected'):
            debug_info["connected"] = self.broker_api.connected
        
        # Get connection details
        for attr in ['host', 'port', 'client_id', 'account_id']:
            if hasattr(self.broker_api, attr):
                debug_info["connection_details"][attr] = getattr(self.broker_api, attr)
        
        # Get account summary
        if hasattr(self.broker_api, 'get_account_summary'):
            debug_info["account_summary"] = self.broker_api.get_account_summary()
        
        # Get positions
        if hasattr(self.broker_api, 'get_positions'):
            debug_info["positions"] = self.broker_api.get_positions()
        
        # Check if the account data was properly loaded
        if not debug_info["account_summary"] or not any(v for k, v in debug_info["account_summary"].items() 
                                                     if k not in ['timestamp', 'account_id', 'error']):
            debug_info["warning"] = "Account data appears to be empty or missing important values"
        
        # Log the debug info
        log_info(f"Connection status: {'Connected' if debug_info['connected'] else 'Disconnected'}")
        
        if debug_info["account_summary"]:
            nlv = debug_info["account_summary"].get("net_liquidation")
            equity = debug_info["account_summary"].get("equity_with_loan")
            log_info(f"Account values - NLV: ${nlv if nlv else 0:.2f}, Equity: ${equity if equity else 0:.2f}")
        
        pos_count = len(debug_info["positions"])
        log_info(f"Positions: {pos_count}")
        
        return debug_info
            
    def shutdown(self) -> None:
        """Shutdown the trader and release resources."""
        self.stop_processing()
        
        if self.broker_api and hasattr(self.broker_api, 'disconnect'):
            self.broker_api.disconnect()
            
        log_info("Trader shutdown complete") 