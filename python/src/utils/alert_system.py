"""
AlertSystem for sending trading and system notifications.
"""

import json
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, Union

import requests
from src.utils.logger import log_debug, log_error, log_info, log_warning


class AlertSystem:
    """Handles alerts and notifications for the trading system."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the alert system.

        Args:
            config: Configuration parameters
        """
        self.config = config
        self.notification_channels = self.setup_channels()
        self.alert_history = []

    def setup_channels(self) -> Dict[str, Any]:
        """Set up notification channels based on configuration.

        Returns:
            Dictionary of notification channel handlers
        """
        channels: Dict[str, Any] = {}

        # Email notifications
        if getattr(self.config, "USE_EMAIL_ALERTS", False):
            channels["email"] = EmailNotifier(
                getattr(self.config, "EMAIL_SETTINGS", {})
            )

        # SMS notifications (via email-to-SMS or third-party API)
        if getattr(self.config, "USE_SMS_ALERTS", False):
            channels["sms"] = SMSNotifier(getattr(self.config, "SMS_SETTINGS", {}))

        # Slack notifications
        if getattr(self.config, "USE_SLACK_ALERTS", False):
            channels["slack"] = SlackNotifier(
                getattr(self.config, "SLACK_SETTINGS", {})
            )

        return channels

    def send_alert(
        self,
        message: str,
        details: Optional[str] = None,
        severity: str = "INFO",
        channels: Optional[List[str]] = None,
    ) -> bool:
        """Send an alert through configured notification channels.

        Args:
            message: Alert message
            details: Additional details (optional)
            severity: Alert severity level (INFO, WARNING, HIGH, CRITICAL)
            channels: List of channels to use (if None, uses default for severity)

        Returns:
            True if alert was sent successfully to at least one channel
        """
        # Default severity
        if severity not in ["INFO", "WARNING", "HIGH", "CRITICAL"]:
            severity = "INFO"

        # Determine which channels to use
        if channels is None:
            # Use default channels for this severity
            severity_channels = getattr(self.config, "SEVERITY_CHANNELS", {})
            channels = severity_channels.get(severity, ["email"])

        # Format the alert
        formatted_alert = self.format_alert(message, details, severity)

        # Send through each channel
        success = False
        for channel in channels:
            if channel in self.notification_channels:
                try:
                    self.notification_channels[channel].send(formatted_alert)
                    success = True
                    log_debug(f"Alert sent via {channel}: {message}")
                except Exception as e:
                    log_error(f"Failed to send alert through {channel}: {str(e)}")

        # Record in history
        self.alert_history.append(
            {
                "timestamp": datetime.now(),
                "message": message,
                "details": details,
                "severity": severity,
                "channels": channels,
                "success": success,
            }
        )

        return success

    def format_alert(self, message: str, details: Optional[str], severity: str) -> str:
        """Format alert message with timestamp and severity.

        Args:
            message: Alert message
            details: Additional details
            severity: Alert severity level

        Returns:
            Formatted alert message
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{severity}] {timestamp} - {message}"
        if details:
            formatted += f"\nDetails: {details}"
        return formatted

    def send_trade_alert(
        self,
        action: str,
        symbol: str,
        direction: str,
        quantity: int,
        price: Optional[float] = None,
        reason: Optional[str] = None,
    ) -> bool:
        """Send alert for trade actions.

        Args:
            action: Trade action (EXECUTED, QUEUED, ERROR, etc.)
            symbol: Trading symbol
            direction: Trade direction (LONG, SHORT)
            quantity: Number of contracts
            price: Trade price (optional)
            reason: Reason for the action (optional)

        Returns:
            True if alert was sent successfully
        """
        message = f"Trade {action}: {symbol} {direction} x{quantity}"
        details = f"Price: {price if price else 'Market'}"

        if reason:
            details += f", Reason: {reason}"

        # Determine severity based on action
        severity = "INFO"
        if action == "ERROR":
            severity = "HIGH"
        elif action in ["CLOSED", "STOPPED"]:
            severity = "WARNING"

        return self.send_alert(message, details, severity)

    def send_system_alert(
        self, component: str, status: str, details: Optional[str] = None
    ) -> bool:
        """Send alert for system status.

        Args:
            component: System component
            status: Component status
            details: Additional details (optional)

        Returns:
            True if alert was sent successfully
        """
        message = f"System: {component} {status}"

        # Determine severity based on status
        severity = "INFO"
        if status in ["ERROR", "FAILED", "CRASHED"]:
            severity = "CRITICAL"
        elif status == "WARNING":
            severity = "WARNING"

        return self.send_alert(message, details, severity)

    def send_performance_alert(
        self, metric: str, value: float, threshold: float, details: Optional[str] = None
    ) -> bool:
        """Send alert for performance issues.

        Args:
            metric: Performance metric
            value: Current metric value
            threshold: Threshold value that was exceeded/not met
            details: Additional details (optional)

        Returns:
            True if alert was sent successfully
        """
        message = f"Performance: {metric} {value:.2f} (threshold: {threshold:.2f})"

        # Always warning severity for performance
        severity = "WARNING"

        return self.send_alert(message, details, severity)

    def send_risk_alert(self, risk_type: str, details: str) -> bool:
        """Send alert for risk management issues.

        Args:
            risk_type: Type of risk issue
            details: Risk details

        Returns:
            True if alert was sent successfully
        """
        message = f"Risk Management: {risk_type}"

        # Use HIGH severity for risk alerts
        severity = "HIGH"

        return self.send_alert(message, details, severity)

    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent alerts.

        Args:
            count: Number of alerts to retrieve

        Returns:
            List of recent alerts
        """
        return self.alert_history[-count:] if self.alert_history else []


class EmailNotifier:
    """Email notification handler."""

    def __init__(self, settings: Dict[str, Any]):
        """Initialize email notifier.

        Args:
            settings: Email configuration settings
        """
        self.smtp_server = settings.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = settings.get("smtp_port", 587)
        self.username = settings.get("username", "")
        self.password = settings.get("password", "")
        self.from_address = settings.get("from_address", self.username)
        self.to_addresses = settings.get("to_addresses", [])

    def send(self, message: str) -> bool:
        """Send email notification.

        Args:
            message: Alert message

        Returns:
            True if sent successfully
        """
        if not self.to_addresses:
            log_warning("No email recipients configured")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_address
            msg["To"] = ", ".join(self.to_addresses)
            msg["Subject"] = "Trading System Alert"

            msg.attach(MIMEText(message, "plain"))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            return True
        except Exception as e:
            log_error(f"Failed to send email: {str(e)}")
            return False


class SMSNotifier:
    """SMS notification handler."""

    def __init__(self, settings: Dict[str, Any]):
        """Initialize SMS notifier.

        Args:
            settings: SMS configuration settings
        """
        self.service = settings.get("service", "email")  # email or api
        self.api_key = settings.get("api_key", "")
        self.api_url = settings.get("api_url", "")
        self.phone_numbers = settings.get("phone_numbers", [])

        # For email-to-SMS
        self.email_notifier = None
        if self.service == "email":
            email_settings = settings.get("email_settings", {})
            if email_settings:
                self.email_notifier = EmailNotifier(email_settings)

    def send(self, message: str) -> bool:
        """Send SMS notification.

        Args:
            message: Alert message

        Returns:
            True if sent successfully
        """
        if not self.phone_numbers:
            log_warning("No SMS recipients configured")
            return False

        if self.service == "email" and self.email_notifier:
            # Use email-to-SMS gateway
            return self.email_notifier.send(message)
        elif self.service == "api":
            # Use SMS API
            try:
                for phone in self.phone_numbers:
                    response = requests.post(
                        self.api_url,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        data=json.dumps(
                            {
                                "to": phone,
                                "message": message[
                                    :160
                                ],  # SMS typically limited to 160 chars
                            }
                        ),
                    )

                    if response.status_code != 200:
                        log_error(f"SMS API error: {response.text}")
                        return False

                return True
            except Exception as e:
                log_error(f"Failed to send SMS via API: {str(e)}")
                return False
        else:
            log_warning(f"Unsupported SMS service: {self.service}")
            return False


class SlackNotifier:
    """Slack notification handler."""

    def __init__(self, settings: Dict[str, Any]):
        """Initialize Slack notifier.

        Args:
            settings: Slack configuration settings
        """
        self.webhook_url = settings.get("webhook_url", "")
        self.channel = settings.get("channel", "#alerts")
        self.username = settings.get("username", "Trading Bot")

    def send(self, message: str) -> bool:
        """Send Slack notification.

        Args:
            message: Alert message

        Returns:
            True if sent successfully
        """
        if not self.webhook_url:
            log_warning("No Slack webhook URL configured")
            return False

        try:
            payload = {
                "channel": self.channel,
                "username": self.username,
                "text": message,
                "icon_emoji": ":chart_with_upwards_trend:",
            }

            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )

            if response.status_code != 200:
                log_error(f"Slack API error: {response.text}")
                return False

            return True
        except Exception as e:
            log_error(f"Failed to send Slack notification: {str(e)}")
            return False
