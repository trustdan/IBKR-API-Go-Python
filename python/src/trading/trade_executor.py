from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, time
import pytz
import time as time_module

from ..models.option import OptionSpread
from ..utils.logger import log_debug, log_info, log_warning, log_error
from ..app.config import Config
from ..utils.time_utils import convert_to_eastern, is_market_open


class TradeExecutor:
    """Handles the execution of option spread trades with IBKR."""
    
    def __init__(self, config: Config, broker_api=None, alert_system=None):
        """Initialize the trade executor.
        
        Args:
            config: Configuration parameters
            broker_api: IBKR API client (optional)
            alert_system: Alert system for notifications (optional)
        """
        self.config = config
        self.broker_api = broker_api
        self.alert_system = alert_system
        self.queued_trades = []
        self.trading_mode = config.TRADING_MODE or "PAPER"  # Default to paper trading
        self.execution_metrics = {
            "total_trades": 0,
            "successful_trades": 0,
            "failed_trades": 0,
            "avg_execution_time": 0
        }
        
    def execute_trade(self, trade_signal: Dict, option_spread: OptionSpread, position_size: int) -> Tuple[str, Any]:
        """Execute a trade based on a signal and selected option spread.
        
        Args:
            trade_signal: The trade signal (containing symbol, direction, etc.)
            option_spread: The selected option spread to trade
            position_size: Number of contracts to trade
            
        Returns:
            Tuple of (status, result) where status is one of:
            "EXECUTED", "QUEUED", "FAILED" and result is order_id or error message
        """
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
            
            # Send alert about queued trade if alert_system is available
            if self.alert_system:
                self.alert_system.send_alert(
                    f"Trade queued for {trade_signal['symbol']}",
                    f"Direction: {trade_signal['direction']}, Size: {position_size}",
                    severity="INFO"
                )
            
            log_info(f"Trade queued for {trade_signal['symbol']} ({trade_signal['direction']}) - "
                    f"Will execute after 3PM ET")
            return "QUEUED", "Trade queued for execution after 3PM ET"
        
        # Execute the trade
        try:
            start_time = time_module.time()
            
            # Different execution methods based on trading mode
            if self.trading_mode == "PAPER":
                order_id = self._execute_paper_trade(trade_signal, option_spread, position_size)
            else:  # LIVE mode
                order_id = self._execute_live_trade(trade_signal, option_spread, position_size)
            
            execution_time = time_module.time() - start_time
            
            # Update execution metrics
            self.execution_metrics["total_trades"] += 1
            self.execution_metrics["successful_trades"] += 1
            self._update_avg_execution_time(execution_time)
            
            # Send alert about executed trade if alert_system is available
            if self.alert_system:
                self.alert_system.send_alert(
                    f"Trade executed for {trade_signal['symbol']}",
                    f"Direction: {trade_signal['direction']}, Size: {position_size}, Order ID: {order_id}",
                    severity="INFO"
                )
            
            log_info(f"Trade executed for {trade_signal['symbol']} ({trade_signal['direction']}) - "
                    f"Order ID: {order_id}, Execution time: {execution_time:.2f}s")
            
            return "EXECUTED", order_id
        except Exception as e:
            error_msg = str(e)
            self.execution_metrics["total_trades"] += 1
            self.execution_metrics["failed_trades"] += 1
            
            log_error(f"Trade execution failed for {trade_signal['symbol']}: {error_msg}")
            
            # Send alert about failed trade if alert_system is available
            if self.alert_system:
                self.alert_system.send_alert(
                    f"Trade execution failed for {trade_signal['symbol']}",
                    error_msg,
                    severity="HIGH"
                )
            
            return "FAILED", error_msg
    
    def _execute_paper_trade(self, trade_signal: Dict, option_spread: OptionSpread, position_size: int) -> str:
        """Execute a paper trade - hits the bid/ask directly without price improvement.
        
        Args:
            trade_signal: The trade signal
            option_spread: The option spread to trade
            position_size: Number of contracts to trade
            
        Returns:
            Order ID string
        """
        # In paper trading, we need to use exact bid/ask prices as price improvement isn't modeled
        if trade_signal['direction'] == "LONG":
            # For LONG trades in paper mode, pay the ask price
            price = option_spread.long_leg.ask - option_spread.short_leg.bid
        else:
            # For SHORT trades in paper mode, sell at the bid price
            price = option_spread.long_leg.bid - option_spread.short_leg.ask
            
        # For now, simulate a broker API call with a delay
        time_module.sleep(0.5)  # Simulate network latency
        
        # Create a synthetic order ID
        order_id = f"PAPER-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        log_debug(f"PAPER trade: {trade_signal['symbol']} {trade_signal['direction']} x{position_size} "
                f"contracts at ${price:.2f} using {option_spread.spread_type}")
        
        # If we had a real broker API, we would call something like:
        # if self.broker_api:
        #     return self.broker_api.place_order(
        #         symbol=trade_signal['symbol'],
        #         direction=trade_signal['direction'],
        #         contracts=position_size,
        #         option_spread=option_spread,
        #         price_type="MARKET",
        #         limit_price=None
        #     )
        
        return order_id
    
    def _execute_live_trade(self, trade_signal: Dict, option_spread: OptionSpread, position_size: int) -> str:
        """Execute a live trade - attempts to get price improvement with limit orders.
        
        Args:
            trade_signal: The trade signal
            option_spread: The option spread to trade
            position_size: Number of contracts to trade
            
        Returns:
            Order ID string
        """
        # For live trading, attempt to get price improvement by placing limit orders
        if trade_signal['direction'] == "LONG":
            # For LONG trades in live mode, try to get fill between bid and ask
            # Calculate midpoint or slightly better than midpoint price
            bid = option_spread.long_leg.bid - option_spread.short_leg.ask
            ask = option_spread.long_leg.ask - option_spread.short_leg.bid
            # Use price improvement factor (default to 0.4 if not in config, meaning closer to bid)
            improvement_factor = getattr(self.config, 'PRICE_IMPROVEMENT_FACTOR', 0.4)
            limit_price = bid + (ask - bid) * improvement_factor
        else:
            # For SHORT trades in live mode, try to get fill between bid and ask
            bid = option_spread.long_leg.bid - option_spread.short_leg.ask
            ask = option_spread.long_leg.ask - option_spread.short_leg.bid
            # Use price improvement factor (default to 0.6 if not in config, meaning closer to ask)
            improvement_factor = 1 - getattr(self.config, 'PRICE_IMPROVEMENT_FACTOR', 0.4)
            limit_price = bid + (ask - bid) * improvement_factor
        
        # For now, simulate a broker API call with a delay
        time_module.sleep(0.7)  # Simulate network latency with longer delay for limit orders
        
        # Create a synthetic order ID
        order_id = f"LIVE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        log_debug(f"LIVE trade: {trade_signal['symbol']} {trade_signal['direction']} x{position_size} "
                f"contracts with limit price ${limit_price:.2f} using {option_spread.spread_type}")
        
        # If we had a real broker API, we would call something like:
        # if self.broker_api:
        #     return self.broker_api.place_order(
        #         symbol=trade_signal['symbol'],
        #         direction=trade_signal['direction'],
        #         contracts=position_size,
        #         option_spread=option_spread,
        #         price_type="LIMIT",
        #         limit_price=limit_price
        #     )
        
        return order_id
            
    def is_valid_execution_time(self, current_time: datetime) -> bool:
        """Check if current time is valid for trade execution.
        
        Args:
            current_time: Current datetime
            
        Returns:
            True if valid execution time, False otherwise
        """
        # Convert to Eastern Time
        et_time = convert_to_eastern(current_time)
        
        # Check if market is open
        if not is_market_open(et_time):
            log_debug(f"Market is closed at {et_time}")
            return False
            
        # Check if after 3 PM ET
        if et_time.hour >= 15:
            return True
            
        # Check if close to market close and exception allowed
        if et_time.hour == 14 and et_time.minute >= 45 and getattr(self.config, 'ALLOW_LATE_DAY_ENTRY', True):
            log_debug("Late day entry allowed (after 2:45 PM ET)")
            return True
            
        log_debug(f"Not a valid execution time: {et_time.strftime('%H:%M:%S')} ET (before 3 PM)")
        return False
        
    def process_queued_trades(self) -> int:
        """Process all queued trades if current time is valid.
        
        Returns:
            Number of trades processed
        """
        current_time = datetime.now()
        
        if not self.is_valid_execution_time(current_time):
            return 0
            
        trades_processed = 0
        
        # Process all queued trades
        for queued_trade in self.queued_trades[:]:  # Create a copy for safe iteration
            status, result = self.execute_trade(
                queued_trade['signal'],
                queued_trade['spread'],
                queued_trade['size']
            )
            
            if status == "EXECUTED":
                self.queued_trades.remove(queued_trade)
                trades_processed += 1
                
                # Log successful execution from queue
                queue_time = current_time - queued_trade['queued_at']
                log_info(f"Processed queued trade for {queued_trade['signal']['symbol']} after "
                        f"{queue_time.total_seconds() / 60:.1f} minutes in queue")
        
        return trades_processed
                
    def _update_avg_execution_time(self, new_time: float) -> None:
        """Update the average execution time metric.
        
        Args:
            new_time: New execution time in seconds
        """
        if self.execution_metrics["successful_trades"] == 1:
            self.execution_metrics["avg_execution_time"] = new_time
        else:
            # Calculate running average
            successful_trades = self.execution_metrics["successful_trades"]
            current_avg = self.execution_metrics["avg_execution_time"]
            self.execution_metrics["avg_execution_time"] = (
                (current_avg * (successful_trades - 1) + new_time) / successful_trades
            )
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics.
        
        Returns:
            Dictionary of execution metrics
        """
        return {
            "total_trades": self.execution_metrics["total_trades"],
            "successful_trades": self.execution_metrics["successful_trades"],
            "failed_trades": self.execution_metrics["failed_trades"],
            "avg_execution_time": self.execution_metrics["avg_execution_time"],
            "success_rate": (
                self.execution_metrics["successful_trades"] / self.execution_metrics["total_trades"]
                if self.execution_metrics["total_trades"] > 0 else 0
            ),
            "queued_trades": len(self.queued_trades)
        } 