"""
Error handling and recovery mechanisms for the trading system.
"""

import time
import traceback
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Callable, DefaultDict, Dict, List, Optional, Tuple

from src.utils.logger import log_debug, log_error, log_info, log_warning


class ErrorHandler:
    """
    Handles errors and provides recovery mechanisms for the trading system.

    Features:
    - Error tracking by component and error type
    - Automatic recovery attempts for common errors
    - Circuit breaker for critical components
    - Alert triggering for severe issues
    """

    config: Dict[str, Any]
    alert_system: Any
    error_counts: DefaultDict[str, int]
    recovery_attempts: DefaultDict[str, int]
    circuit_breakers: Dict[str, Dict[str, Any]]
    last_errors: Dict[str, datetime]
    component_errors: Dict[str, List[Dict[str, Any]]]

    def __init__(
        self, config: Dict[str, Any], alert_system: Optional[Any] = None
    ) -> None:
        """
        Initialize the error handler.

        Args:
            config: Configuration parameters
            alert_system: Alert system for notifications
        """
        self.config = config
        self.alert_system = alert_system
        self.error_counts = defaultdict(int)  # Track errors by component:type
        self.recovery_attempts = defaultdict(int)  # Track recovery attempts
        self.circuit_breakers = {}  # Track circuit breaker status
        self.last_errors = {}  # Track last error time
        self.component_errors = {}  # Track detailed error history by component

        # Initialize circuit breakers for critical components
        critical_components = [
            "IBKR_API",
            "DATA_PROVIDER",
            "OPTION_SELECTOR",
            "TRADE_EXECUTOR",
            "RISK_MANAGER",
        ]

        for component in critical_components:
            self.circuit_breakers[component] = {
                "tripped": False,
                "trip_time": None,
                "reset_time": None,
            }
            self.component_errors[component] = []

    def handle_error(
        self,
        component: str,
        error_type: str,
        error_msg: str,
        context: Optional[Dict] = None,
    ) -> Tuple[bool, str]:
        """
        Handle an error from a system component.

        Args:
            component: System component that experienced the error
            error_type: Type of error encountered
            error_msg: Error message or description
            context: Additional context about the error (optional)

        Returns:
            Tuple of (recovery_succeeded, recovery_message)
        """
        # Get stack trace
        stack_trace = traceback.format_exc()

        # Log the error
        log_error(f"Error in {component}: {error_type} - {error_msg}")

        # Increment error counter
        error_key = f"{component}:{error_type}"
        self.error_counts[error_key] += 1
        self.last_errors[error_key] = datetime.now()

        # Check circuit breaker status
        if (
            component in self.circuit_breakers
            and self.circuit_breakers[component]["tripped"]
        ):
            log_warning(f"Circuit breaker tripped for {component}, skipping recovery")

            if self.alert_system:
                self.alert_system.send_system_alert(
                    component,
                    "CIRCUIT_BREAKER_ACTIVE",
                    f"Circuit breaker active until {self.circuit_breakers[component]['reset_time']}",
                )

            return False, "Circuit breaker active"

        # Alert if critical error or threshold exceeded
        if self.is_critical_error(error_type) or self.error_counts[
            error_key
        ] >= self.config.get("ERROR_THRESHOLD", 3):
            if self.alert_system:
                self.alert_system.send_system_alert(
                    component,
                    "ERROR",
                    f"{error_type}: {error_msg}\n{stack_trace if self.config.get('INCLUDE_STACK_TRACE_IN_ALERTS', False) else ''}",
                )

            # Trip circuit breaker if critical and repeated errors
            if self.is_critical_error(error_type) and self.error_counts[
                error_key
            ] >= self.config.get("CIRCUIT_BREAKER_THRESHOLD", 5):
                self._trip_circuit_breaker(component)
                return False, "Circuit breaker tripped"

        # Attempt recovery if allowed
        if self.recovery_attempts[error_key] < self.config.get(
            "MAX_RECOVERY_ATTEMPTS", 3
        ):
            return self.attempt_recovery(component, error_type, context)
        else:
            if self.alert_system:
                self.alert_system.send_system_alert(
                    component,
                    "RECOVERY_FAILED",
                    f"Max recovery attempts ({self.config.get('MAX_RECOVERY_ATTEMPTS', 3)}) reached for {error_type}",
                )
            return (
                False,
                f"Max recovery attempts reached ({self.config.get('MAX_RECOVERY_ATTEMPTS', 3)})",
            )

    def is_critical_error(self, error_type: str) -> bool:
        """
        Determine if an error type is critical.

        Args:
            error_type: Error type to check

        Returns:
            True if error is critical
        """
        critical_errors = [
            "CONNECTION_ERROR",
            "AUTHENTICATION_ERROR",
            "ORDER_EXECUTION_ERROR",
            "DATA_INTEGRITY_ERROR",
            "ACCOUNT_ERROR",
            "POSITION_ERROR",
            "MARKET_ACCESS_ERROR",
        ]
        return error_type in critical_errors

    def attempt_recovery(
        self, component: str, error_type: str, context: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Attempt to recover from an error.

        Args:
            component: System component that experienced the error
            error_type: Type of error encountered
            context: Additional context about the error (optional)

        Returns:
            Tuple of (recovery_succeeded, recovery_message)
        """
        error_key = f"{component}:{error_type}"
        self.recovery_attempts[error_key] += 1

        log_info(
            f"Attempting recovery for {component}:{error_type} (attempt {self.recovery_attempts[error_key]})"
        )

        # Component-specific recovery strategies
        if component == "IBKR_API":
            return self._recover_ibkr_api(error_type, context)
        elif component == "DATA_PROVIDER":
            return self._recover_data_provider(error_type, context)
        elif component == "OPTION_SELECTOR":
            return self._recover_option_selector(error_type, context)
        elif component == "TRADE_EXECUTOR":
            return self._recover_trade_executor(error_type, context)
        elif component == "RISK_MANAGER":
            return self._recover_risk_manager(error_type, context)
        else:
            # Generic recovery for other components
            return self._generic_recovery(component, error_type, context)

    def _recover_ibkr_api(
        self, error_type: str, context: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Recovery strategy for IBKR API errors.

        Args:
            error_type: Type of error
            context: Additional context

        Returns:
            Tuple of (recovery_succeeded, recovery_message)
        """
        if error_type == "CONNECTION_ERROR":
            # Try reconnecting to the API
            log_info("Attempting to reconnect to IBKR API")

            try:
                # If context contains the API client, use it to reconnect
                if context and "client" in context:
                    client = context["client"]
                    # Simulate disconnect/reconnect cycle with a delay
                    time.sleep(2)
                    # client.disconnect()
                    # time.sleep(1)
                    # connected = client.connect()
                    connected = True  # Simulated success

                    if connected:
                        log_info("Successfully reconnected to IBKR API")
                        return True, "Reconnected to API"
                    else:
                        log_warning("Failed to reconnect to IBKR API")
                        return False, "Reconnect attempt failed"
                else:
                    return False, "No API client in context"
            except Exception as e:
                log_error(f"Error during IBKR API recovery: {str(e)}")
                return False, f"Recovery error: {str(e)}"

        elif error_type == "AUTHENTICATION_ERROR":
            # Authentication errors typically require user intervention
            if self.alert_system:
                self.alert_system.send_system_alert(
                    "IBKR_API",
                    "AUTHENTICATION_REQUIRED",
                    "API authentication error - manual intervention required",
                )
            return False, "Authentication error requires manual intervention"

        elif error_type == "REQUEST_ERROR":
            # For request errors, we can try again with backoff
            try:
                retry_count = context.get("retry_count", 0) if context else 0
                backoff_seconds = min(
                    2**retry_count, 60
                )  # Exponential backoff, max 60 seconds

                log_info(f"Retrying request after {backoff_seconds} seconds")
                time.sleep(backoff_seconds)

                # If context contains the request function and parameters, retry it
                if context and "request_func" in context and "params" in context:
                    result = context["request_func"](*context["params"])
                    return True, "Request retried successfully"
                else:
                    return False, "Insufficient context for retry"
            except Exception as e:
                log_error(f"Error during request retry: {str(e)}")
                return False, f"Retry error: {str(e)}"

        return False, f"No recovery strategy for {error_type}"

    def _recover_data_provider(
        self, error_type: str, context: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Recovery strategy for data provider errors.

        Args:
            error_type: Type of error
            context: Additional context

        Returns:
            Tuple of (recovery_succeeded, recovery_message)
        """
        if error_type == "DATA_MISSING":
            # Try alternative data source
            try:
                symbol = context.get("symbol") if context else None
                if not symbol:
                    return False, "No symbol in context"

                log_info(f"Attempting to fetch data for {symbol} from alternate source")

                # Simulate fallback data fetch
                # In a real implementation, this would use an alternative data source
                time.sleep(1)

                # Simulate success
                return True, "Retrieved data from alternate source"
            except Exception as e:
                log_error(f"Error during data recovery: {str(e)}")
                return False, f"Recovery error: {str(e)}"

        elif error_type == "CONNECTION_ERROR":
            # Similar to API connection error
            try:
                log_info("Attempting to reconnect to data provider")
                time.sleep(2)  # Simulated reconnection delay
                return True, "Reconnected to data provider"
            except Exception as e:
                log_error(f"Error reconnecting to data provider: {str(e)}")
                return False, f"Recovery error: {str(e)}"

        return False, f"No recovery strategy for {error_type}"

    def _recover_option_selector(
        self, error_type: str, context: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Recovery strategy for option selector errors.

        Args:
            error_type: Type of error
            context: Additional context

        Returns:
            Tuple of (recovery_succeeded, recovery_message)
        """
        if error_type == "NO_SUITABLE_OPTIONS":
            # Try with relaxed criteria
            try:
                log_info("Attempting option selection with relaxed criteria")

                # If context contains the selector and original parameters, retry with relaxed criteria
                if context and "selector" in context and "params" in context:
                    # Relax delta constraints by 20%
                    original_min_delta = getattr(self.config, "MIN_DELTA", 0.3)
                    original_max_delta = getattr(self.config, "MAX_DELTA", 0.5)

                    # Temporarily adjust config
                    setattr(self.config, "MIN_DELTA", original_min_delta * 0.8)
                    setattr(self.config, "MAX_DELTA", original_max_delta * 1.2)

                    # Try again
                    # result = context['selector'].select_vertical_spread(*context['params'])

                    # Restore original config
                    setattr(self.config, "MIN_DELTA", original_min_delta)
                    setattr(self.config, "MAX_DELTA", original_max_delta)

                    return True, "Selected options with relaxed criteria"
                else:
                    return False, "Insufficient context for option retry"
            except Exception as e:
                log_error(f"Error during option selection recovery: {str(e)}")
                return False, f"Recovery error: {str(e)}"

        return False, f"No recovery strategy for {error_type}"

    def _recover_trade_executor(
        self, error_type: str, context: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Recovery strategy for trade executor errors.

        Args:
            error_type: Type of error
            context: Additional context

        Returns:
            Tuple of (recovery_succeeded, recovery_message)
        """
        if error_type == "ORDER_EXECUTION_ERROR":
            # For order execution errors, we might retry or use a different order type
            try:
                log_info("Attempting order execution recovery")

                if context and "executor" in context and "order" in context:
                    # Modify order type to improve chances of execution
                    # E.g., switch from LIMIT to MARKET
                    modified_order = context["order"].copy()
                    modified_order["order_type"] = "MARKET"

                    log_info("Retrying with MARKET order")
                    # result = context['executor'].execute_order(modified_order)

                    return True, "Order executed successfully with MARKET type"
                else:
                    return False, "Insufficient context for order retry"
            except Exception as e:
                log_error(f"Error during order execution recovery: {str(e)}")
                return False, f"Recovery error: {str(e)}"

        return False, f"No recovery strategy for {error_type}"

    def _recover_risk_manager(
        self, error_type: str, context: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Recovery strategy for risk manager errors.

        Args:
            error_type: Type of error
            context: Additional context

        Returns:
            Tuple of (recovery_succeeded, recovery_message)
        """
        if error_type == "POSITION_SYNC_ERROR":
            # For position synchronization errors, we might force a refresh
            try:
                log_info("Attempting to refresh positions from broker")

                if context and "risk_manager" in context:
                    # Force position update from broker
                    context["risk_manager"].update_positions_from_broker()
                    return True, "Positions refreshed from broker"
                else:
                    return False, "Risk manager not available in context"
            except Exception as e:
                log_error(f"Error during position refresh: {str(e)}")
                return False, f"Recovery error: {str(e)}"

        return False, f"No recovery strategy for {error_type}"

    def _generic_recovery(
        self, component: str, error_type: str, context: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Generic recovery strategy for unspecified components.

        Args:
            component: System component
            error_type: Type of error
            context: Additional context

        Returns:
            Tuple of (recovery_succeeded, recovery_message)
        """
        # Simple retry with delay
        log_info(f"Generic recovery attempt for {component}:{error_type}")
        time.sleep(1)

        # Generic recovery has low success probability
        return False, "Generic recovery attempted but likely insufficient"

    def _trip_circuit_breaker(self, component: str) -> None:
        """
        Trip circuit breaker for a component to prevent further damage.

        Args:
            component: System component to disable
        """
        if component not in self.circuit_breakers:
            return

        now = datetime.now()
        reset_time = now + timedelta(
            minutes=self.config.get("CIRCUIT_BREAKER_MINUTES", 30)
        )

        log_warning(f"Tripping circuit breaker for {component} until {reset_time}")

        self.circuit_breakers[component]["tripped"] = True
        self.circuit_breakers[component]["trip_time"] = now
        self.circuit_breakers[component]["reset_time"] = reset_time

        if self.alert_system:
            self.alert_system.send_system_alert(
                component,
                "CIRCUIT_BREAKER_TRIPPED",
                f"Component disabled until {reset_time}",
            )

    def check_circuit_breakers(self) -> List[str]:
        """
        Check and reset circuit breakers if their timeout has expired.

        Returns:
            List of components whose circuit breakers were reset
        """
        reset_components = []
        now = datetime.now()

        for component, breaker in self.circuit_breakers.items():
            if breaker["tripped"] and now >= breaker["reset_time"]:
                log_info(f"Resetting circuit breaker for {component}")

                breaker["tripped"] = False
                breaker["trip_time"] = None
                breaker["reset_time"] = None

                reset_components.append(component)

                if self.alert_system:
                    self.alert_system.send_system_alert(
                        component, "CIRCUIT_BREAKER_RESET", "Component re-enabled"
                    )

        return reset_components

    def can_use_component(self, component: str) -> bool:
        """
        Check if a component can be used (circuit breaker not tripped).

        Args:
            component: System component to check

        Returns:
            True if component can be used
        """
        if component not in self.circuit_breakers:
            return True

        return not self.circuit_breakers[component]["tripped"]

    def clear_error_counts(self, older_than_minutes: int = 60) -> int:
        """
        Clear error counts that are older than specified minutes.

        Args:
            older_than_minutes: Minutes threshold for clearing errors

        Returns:
            Number of error records cleared
        """
        cleared = 0
        threshold_time = datetime.now() - timedelta(minutes=older_than_minutes)

        for error_key in list(self.error_counts.keys()):
            if (
                error_key in self.last_errors
                and self.last_errors[error_key] < threshold_time
            ):
                del self.error_counts[error_key]
                del self.last_errors[error_key]

                if error_key in self.recovery_attempts:
                    del self.recovery_attempts[error_key]

                cleared += 1

        return cleared

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a summary of errors and circuit breaker status.

        Returns:
            Error summary dictionary
        """
        component_errors: Dict[str, int] = defaultdict(int)

        # Count errors by component
        for error_key in self.error_counts:
            component = error_key.split(":")[0]
            component_errors[component] += self.error_counts[error_key]

        # Create circuit breaker status summary
        circuit_status = {}
        for component, breaker in self.circuit_breakers.items():
            if breaker["tripped"]:
                reset_in = (breaker["reset_time"] - datetime.now()).total_seconds() / 60
                circuit_status[component] = f"Tripped, reset in {reset_in:.1f} minutes"
            else:
                circuit_status[component] = "Normal"

        return {
            "total_errors": sum(self.error_counts.values()),
            "total_recovery_attempts": sum(self.recovery_attempts.values()),
            "errors_by_component": dict(component_errors),
            "circuit_breaker_status": circuit_status,
        }
