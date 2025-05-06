"""
Performance monitoring for the trading system.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import time
import math
from collections import defaultdict
import threading
import statistics
import psutil
import os

from .logger import log_debug, log_info, log_warning, log_error


class PerformanceMonitor:
    """
    Monitors performance metrics for the trading system.
    
    Features:
    - Track execution times for key operations
    - Monitor system resource usage
    - Generate alerts for performance degradation
    - Provide performance reporting
    """
    
    def __init__(self, config, alert_system=None):
        """
        Initialize the performance monitor.
        
        Args:
            config: Configuration parameters
            alert_system: Alert system for notifications
        """
        self.config = config
        self.alert_system = alert_system
        self.metrics = defaultdict(list)
        self.start_time = time.time()
        self.component_timers = {}
        self.thresholds = self._get_thresholds()
        
        # Initialize resource monitoring if enabled
        self.resource_monitoring = getattr(self.config, 'ENABLE_RESOURCE_MONITORING', True)
        self.resource_monitor_thread = None
        
        if self.resource_monitoring:
            self._start_resource_monitoring()
            
    def _get_thresholds(self) -> Dict[str, Dict[str, float]]:
        """
        Get performance thresholds from config.
        
        Returns:
            Dictionary of thresholds by component and metric
        """
        thresholds = {
            'api_request': {
                'warning': getattr(self.config, 'API_REQUEST_WARNING_THRESHOLD', 1.0),
                'critical': getattr(self.config, 'API_REQUEST_CRITICAL_THRESHOLD', 5.0)
            },
            'option_selection': {
                'warning': getattr(self.config, 'OPTION_SELECTION_WARNING_THRESHOLD', 2.0),
                'critical': getattr(self.config, 'OPTION_SELECTION_CRITICAL_THRESHOLD', 10.0)
            },
            'order_execution': {
                'warning': getattr(self.config, 'ORDER_EXECUTION_WARNING_THRESHOLD', 2.0),
                'critical': getattr(self.config, 'ORDER_EXECUTION_CRITICAL_THRESHOLD', 5.0)
            },
            'data_processing': {
                'warning': getattr(self.config, 'DATA_PROCESSING_WARNING_THRESHOLD', 1.0),
                'critical': getattr(self.config, 'DATA_PROCESSING_CRITICAL_THRESHOLD', 5.0)
            },
            'scanning': {
                'warning': getattr(self.config, 'SCANNING_WARNING_THRESHOLD', 5.0),
                'critical': getattr(self.config, 'SCANNING_CRITICAL_THRESHOLD', 20.0)
            },
            'system': {
                'cpu_warning': getattr(self.config, 'CPU_WARNING_THRESHOLD', 80.0),
                'cpu_critical': getattr(self.config, 'CPU_CRITICAL_THRESHOLD', 95.0),
                'memory_warning': getattr(self.config, 'MEMORY_WARNING_THRESHOLD', 80.0),
                'memory_critical': getattr(self.config, 'MEMORY_CRITICAL_THRESHOLD', 95.0)
            }
        }
        
        return thresholds
        
    def _start_resource_monitoring(self) -> None:
        """Start a background thread to monitor system resources."""
        def monitor_resources():
            while self.resource_monitoring:
                try:
                    # Get CPU and memory usage
                    cpu_percent = psutil.cpu_percent(interval=5)
                    memory_percent = psutil.virtual_memory().percent
                    
                    # Record metrics
                    self.record_metric('system', 'cpu_percent', cpu_percent)
                    self.record_metric('system', 'memory_percent', memory_percent)
                    
                    # Check thresholds and send alerts if needed
                    self._check_resource_thresholds(cpu_percent, memory_percent)
                    
                    # Sleep between measurements
                    time.sleep(getattr(self.config, 'RESOURCE_MONITORING_INTERVAL', 30))
                except Exception as e:
                    log_error(f"Error in resource monitoring: {str(e)}")
                    time.sleep(60)  # Longer sleep on error
        
        self.resource_monitor_thread = threading.Thread(
            target=monitor_resources,
            daemon=True  # Make daemon so it exits when main thread exits
        )
        self.resource_monitor_thread.start()
        
    def _check_resource_thresholds(self, cpu_percent: float, memory_percent: float) -> None:
        """
        Check resource usage against thresholds and send alerts if needed.
        
        Args:
            cpu_percent: CPU usage percentage
            memory_percent: Memory usage percentage
        """
        # Check CPU usage
        if cpu_percent >= self.thresholds['system']['cpu_critical']:
            log_error(f"CRITICAL: CPU usage at {cpu_percent}% (threshold: {self.thresholds['system']['cpu_critical']}%)")
            if self.alert_system:
                self.alert_system.send_performance_alert(
                    'CPU Usage',
                    cpu_percent,
                    self.thresholds['system']['cpu_critical'],
                    'Critical CPU usage detected - system may become unresponsive'
                )
        elif cpu_percent >= self.thresholds['system']['cpu_warning']:
            log_warning(f"WARNING: CPU usage at {cpu_percent}% (threshold: {self.thresholds['system']['cpu_warning']}%)")
            if self.alert_system:
                self.alert_system.send_performance_alert(
                    'CPU Usage',
                    cpu_percent,
                    self.thresholds['system']['cpu_warning'],
                    'High CPU usage detected'
                )
                
        # Check memory usage
        if memory_percent >= self.thresholds['system']['memory_critical']:
            log_error(f"CRITICAL: Memory usage at {memory_percent}% (threshold: {self.thresholds['system']['memory_critical']}%)")
            if self.alert_system:
                self.alert_system.send_performance_alert(
                    'Memory Usage',
                    memory_percent,
                    self.thresholds['system']['memory_critical'],
                    'Critical memory usage detected - system may become unstable'
                )
        elif memory_percent >= self.thresholds['system']['memory_warning']:
            log_warning(f"WARNING: Memory usage at {memory_percent}% (threshold: {self.thresholds['system']['memory_warning']}%)")
            if self.alert_system:
                self.alert_system.send_performance_alert(
                    'Memory Usage',
                    memory_percent,
                    self.thresholds['system']['memory_warning'],
                    'High memory usage detected'
                )
                
    def start_timer(self, component: str, operation: str) -> str:
        """
        Start a timer for measuring execution time of an operation.
        
        Args:
            component: Component name (e.g., 'api', 'scanner')
            operation: Operation name (e.g., 'fetch_data', 'scan_symbols')
            
        Returns:
            Timer ID to pass to stop_timer
        """
        timer_id = f"{component}:{operation}:{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.component_timers[timer_id] = time.time()
        return timer_id
        
    def stop_timer(self, timer_id: str) -> float:
        """
        Stop a timer and record the execution time.
        
        Args:
            timer_id: Timer ID from start_timer
            
        Returns:
            Execution time in seconds
        """
        if timer_id not in self.component_timers:
            log_warning(f"Timer {timer_id} not found")
            return 0.0
            
        start_time = self.component_timers.pop(timer_id)
        execution_time = time.time() - start_time
        
        # Parse component and operation from timer_id
        parts = timer_id.split(':', 2)
        if len(parts) >= 2:
            component, operation = parts[0], parts[1]
            self.record_operation_time(component, operation, execution_time)
            
        return execution_time
        
    def record_operation_time(self, component: str, operation: str, execution_time: float) -> None:
        """
        Record execution time for an operation.
        
        Args:
            component: Component name
            operation: Operation name
            execution_time: Execution time in seconds
        """
        key = f"{component}:{operation}"
        self.metrics[key].append({
            'timestamp': datetime.now(),
            'execution_time': execution_time
        })
        
        # Check if we need to alert on slow operation
        self._check_execution_threshold(component, operation, execution_time)
        
        # Log the execution time
        if execution_time > 1.0:  # Only log operations taking more than 1 second
            log_debug(f"{component.capitalize()} {operation} completed in {execution_time:.2f}s")
            
    def _check_execution_threshold(self, component: str, operation: str, execution_time: float) -> None:
        """
        Check if execution time exceeds thresholds and send alert if needed.
        
        Args:
            component: Component name
            operation: Operation name
            execution_time: Execution time in seconds
        """
        # Map specific operation types to threshold categories
        threshold_category = component
        if component == 'api' and operation in ['get_market_data', 'get_option_chain']:
            threshold_category = 'api_request'
        elif component == 'option_selector':
            threshold_category = 'option_selection'
        elif component == 'trade_executor' and operation in ['execute_trade', 'place_order']:
            threshold_category = 'order_execution'
        elif component == 'data' and operation in ['process', 'transform']:
            threshold_category = 'data_processing'
        elif component == 'scanner' and operation == 'scan':
            threshold_category = 'scanning'
            
        # Check if threshold category exists
        if threshold_category not in self.thresholds:
            return
            
        # Check against critical threshold
        if 'critical' in self.thresholds[threshold_category] and \
           execution_time >= self.thresholds[threshold_category]['critical']:
            log_error(
                f"CRITICAL: {component.capitalize()} {operation} took {execution_time:.2f}s "
                f"(threshold: {self.thresholds[threshold_category]['critical']}s)"
            )
            if self.alert_system:
                self.alert_system.send_performance_alert(
                    f"{component.capitalize()} {operation} Time",
                    execution_time,
                    self.thresholds[threshold_category]['critical'],
                    'Critical performance degradation detected'
                )
        # Check against warning threshold
        elif 'warning' in self.thresholds[threshold_category] and \
             execution_time >= self.thresholds[threshold_category]['warning']:
            log_warning(
                f"WARNING: {component.capitalize()} {operation} took {execution_time:.2f}s "
                f"(threshold: {self.thresholds[threshold_category]['warning']}s)"
            )
            if self.alert_system:
                self.alert_system.send_performance_alert(
                    f"{component.capitalize()} {operation} Time",
                    execution_time,
                    self.thresholds[threshold_category]['warning'],
                    'Performance degradation detected'
                )
                
    def record_metric(self, category: str, name: str, value: float) -> None:
        """
        Record a custom performance metric.
        
        Args:
            category: Metric category
            name: Metric name
            value: Metric value
        """
        key = f"{category}:{name}"
        self.metrics[key].append({
            'timestamp': datetime.now(),
            'value': value
        })
        
    def record_scan_performance(self, symbols_count: int, scan_time: float) -> None:
        """
        Record scanner performance metrics.
        
        Args:
            symbols_count: Number of symbols scanned
            scan_time: Time taken to scan in seconds
        """
        # Calculate symbols per second
        symbols_per_second = symbols_count / scan_time if scan_time > 0 else 0
        
        # Record metrics
        self.record_metric('scanner', 'scan_time', scan_time)
        self.record_metric('scanner', 'symbols_count', symbols_count)
        self.record_metric('scanner', 'symbols_per_second', symbols_per_second)
        
        # Check against thresholds
        min_symbols_per_second = getattr(self.config, 'MIN_SYMBOLS_PER_SECOND', 50)
        if symbols_per_second < min_symbols_per_second:
            log_warning(
                f"Scanner throughput below threshold: {symbols_per_second:.2f} symbols/sec "
                f"(threshold: {min_symbols_per_second})"
            )
            if self.alert_system:
                self.alert_system.send_performance_alert(
                    'Scanner Throughput',
                    symbols_per_second,
                    min_symbols_per_second,
                    f'Processed {symbols_count} symbols in {scan_time:.2f}s'
                )
                
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status.
        
        Returns:
            Dictionary with system status metrics
        """
        status = {
            'uptime': time.time() - self.start_time,
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'process_memory_mb': psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        }
        
        return status
        
    def get_metrics_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """
        Get a summary of performance metrics over the specified time window.
        
        Args:
            minutes: Time window in minutes
            
        Returns:
            Dictionary of summarized metrics
        """
        summary = {
            'system': self.get_system_status(),
            'operations': {},
            'components': {}
        }
        
        # Get time threshold
        threshold_time = datetime.now() - timedelta(minutes=minutes)
        
        # Process operation metrics
        for key, values in self.metrics.items():
            # Filter to recent values
            recent_values = [v for v in values if v['timestamp'] >= threshold_time]
            
            if not recent_values:
                continue
                
            if ':' in key:
                category, name = key.split(':', 1)
                
                # Handle operation time metrics
                if category in ['api', 'option_selector', 'trade_executor', 'data', 'scanner']:
                    if category not in summary['operations']:
                        summary['operations'][category] = {}
                        
                    # Calculate statistics
                    times = [v['execution_time'] for v in recent_values]
                    summary['operations'][category][name] = {
                        'count': len(times),
                        'min': min(times),
                        'max': max(times),
                        'avg': sum(times) / len(times),
                        'median': statistics.median(times),
                        'p95': self._percentile(times, 95) if len(times) >= 20 else None
                    }
                # Handle component metrics
                else:
                    if category not in summary['components']:
                        summary['components'][category] = {}
                        
                    # Calculate statistics
                    values_list = [v['value'] for v in recent_values]
                    summary['components'][category][name] = {
                        'count': len(values_list),
                        'last': values_list[-1],
                        'min': min(values_list),
                        'max': max(values_list),
                        'avg': sum(values_list) / len(values_list)
                    }
                    
        return summary
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """
        Calculate percentile value from a list.
        
        Args:
            values: List of values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        values.sort()
        k = (len(values) - 1) * percentile / 100
        f = int(k)
        c = math.ceil(k)
        
        if f == c:
            return values[int(k)]
        
        d0 = values[f] * (c - k)
        d1 = values[c] * (k - f)
        return d0 + d1
        
    def run_health_check(self) -> Dict[str, str]:
        """
        Run a health check for all components of the system.
        
        Returns:
            Dictionary of component health statuses
        """
        health = {}
        
        # System health
        system_status = self.get_system_status()
        if system_status['cpu_percent'] > self.thresholds['system']['cpu_critical'] or \
           system_status['memory_percent'] > self.thresholds['system']['memory_critical']:
            health['system'] = 'CRITICAL'
        elif system_status['cpu_percent'] > self.thresholds['system']['cpu_warning'] or \
             system_status['memory_percent'] > self.thresholds['system']['memory_warning']:
            health['system'] = 'WARNING'
        else:
            health['system'] = 'OK'
            
        # IBKR API health
        api_key = 'api:request'
        api_operations = [k for k in self.metrics.keys() if k.startswith('api:')]
        if not api_operations:
            health['api'] = 'UNKNOWN'
        else:
            recent_errors = sum(1 for k in api_operations if k.endswith('error') and self.metrics[k])
            if recent_errors > 3:
                health['api'] = 'CRITICAL'
            elif recent_errors > 0:
                health['api'] = 'WARNING'
            else:
                health['api'] = 'OK'
                
        # Scanner health
        scanner_key = 'scanner:scan'
        if scanner_key in self.metrics and self.metrics[scanner_key]:
            recent_scans = [v for v in self.metrics[scanner_key] 
                          if v['timestamp'] >= datetime.now() - timedelta(hours=1)]
            if not recent_scans:
                health['scanner'] = 'WARNING'  # No recent scans
            else:
                avg_time = sum(v['execution_time'] for v in recent_scans) / len(recent_scans)
                if avg_time > self.thresholds['scanning']['critical']:
                    health['scanner'] = 'CRITICAL'
                elif avg_time > self.thresholds['scanning']['warning']:
                    health['scanner'] = 'WARNING'
                else:
                    health['scanner'] = 'OK'
        else:
            health['scanner'] = 'UNKNOWN'
            
        # Add more component checks as needed
            
        return health
        
    def get_all_health_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive health and performance metrics.
        
        Returns:
            Dictionary with all health and performance metrics
        """
        return {
            'health': self.run_health_check(),
            'metrics': self.get_metrics_summary(minutes=60),
            'thresholds': self.thresholds
        } 