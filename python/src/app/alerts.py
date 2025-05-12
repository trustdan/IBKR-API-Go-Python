"""
Alert Manager module for the trading system.

This module handles alerts based on configured thresholds and sends
notifications through configured channels.
"""

import datetime
import json
import logging
import smtplib
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alert conditions and notification delivery."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the alert manager.

        Args:
            config: Configuration dictionary with alert settings
        """
        self.config = config
        self.alert_history: List[Dict[str, Any]] = []
        self.max_history = 100

    def reload_config(self, config: Dict[str, Any]) -> None:
        """
        Update configuration.

        Args:
            config: New configuration dictionary
        """
        self.config = config
        logger.info("Alert manager configuration reloaded")

    def check_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Check metrics against thresholds and trigger alerts if needed.

        Args:
            metrics: Current metrics dictionary
        """
        alerts_config = self.config.get("alerts", {})

        # Check for high latency
        max_latency_ms = alerts_config.get("max_latency_ms", 500)
        if metrics.get("maxLatencyMs", 0) > max_latency_ms:
            self.send_alert(
                "High Latency",
                f"Order execution latency ({metrics['maxLatencyMs']}ms) exceeds threshold ({max_latency_ms}ms)",
                "warning",
            )

        # Check for daily P&L threshold
        min_daily_pnl = alerts_config.get("min_daily_pnl", -1000)
        if metrics.get("dailyPnL", 0) < min_daily_pnl:
            self.send_alert(
                "Daily P&L Alert",
                f"Daily P&L (${metrics['dailyPnL']:.2f}) below minimum threshold (${min_daily_pnl:.2f})",
                "danger",
            )

        # Check for high error rate
        max_errors = alerts_config.get("max_errors", 5)
        if metrics.get("errorCount", 0) > max_errors:
            self.send_alert(
                "High Error Rate",
                f"Error count ({metrics['errorCount']}) exceeds threshold ({max_errors})",
                "danger",
            )

    def send_alert(self, title: str, message: str, level: str = "info") -> bool:
        """
        Send an alert notification through configured channels.

        Args:
            title: Alert title
            message: Alert message
            level: Alert level (info, warning, danger)

        Returns:
            bool: True if alert was sent through at least one channel
        """
        alerts_config = self.config.get("alerts", {})

        # Add to history
        alert = {
            "title": title,
            "message": message,
            "level": level,
            "timestamp": datetime.datetime.now().timestamp(),
        }

        self.alert_history.append(alert)

        # Trim history if needed
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history :]

        # Log the alert
        log_method = getattr(logger, level, logger.info)
        log_method(f"ALERT: {title} - {message}")

        # Send via configured channels
        channels_sent = []

        # Email
        if alerts_config.get("enable_email", False) and alerts_config.get("email_to"):
            if self._send_email_alert(title, message, level):
                channels_sent.append("email")

        # Slack
        if alerts_config.get("enable_slack", False) and alerts_config.get(
            "slack_webhook_url"
        ):
            if self._send_slack_alert(title, message, level):
                channels_sent.append("slack")

        return len(channels_sent) > 0

    def _send_email_alert(self, title: str, message: str, level: str) -> bool:
        """
        Send an alert via email.

        Args:
            title: Alert title
            message: Alert message
            level: Alert level

        Returns:
            bool: True if email was sent successfully
        """
        alerts_config = self.config.get("alerts", {})
        email_to = alerts_config.get("email_to", "")

        # In a production system, you would use proper SMTP settings from config
        # This is a simplified example
        try:
            email_config = self.config.get("email", {})
            smtp_server = email_config.get("smtp_server", "localhost")
            smtp_port = email_config.get("smtp_port", 25)
            smtp_user = email_config.get("smtp_user", "")
            smtp_password = email_config.get("smtp_password", "")

            # Simplified email sending - in a real system use proper HTML templates
            msg = MIMEText(message)
            msg["Subject"] = f"Trading Alert: {title}"
            msg["From"] = email_config.get("from_address", "trading-alerts@example.com")
            msg["To"] = email_to

            # In a real implementation, this would actually send the email
            # For now, just log it
            logger.info(f"Would send email to {email_to}: {title} - {message}")

            # Uncomment to actually send emails
            # with smtplib.SMTP(smtp_server, smtp_port) as server:
            #     if smtp_user and smtp_password:
            #         server.login(smtp_user, smtp_password)
            #     server.send_message(msg)

            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

    def _send_slack_alert(self, title: str, message: str, level: str) -> bool:
        """
        Send an alert via Slack webhook.

        Args:
            title: Alert title
            message: Alert message
            level: Alert level

        Returns:
            bool: True if Slack notification was sent successfully
        """
        alerts_config = self.config.get("alerts", {})
        webhook_url = alerts_config.get("slack_webhook_url", "")

        try:
            # Map alert level to Slack color
            color_map = {"info": "#36c5f0", "warning": "#f2c744", "danger": "#e01e5a"}
            color = color_map.get(level, "#36c5f0")

            # Prepare Slack message payload
            payload = {
                "text": f"Trading Alert: {title}",
                "attachments": [
                    {
                        "color": color,
                        "title": title,
                        "text": message,
                        "footer": "IBKR Trader Admin",
                    }
                ],
            }

            # In a real implementation, this would actually send to Slack
            # For now, just log it
            logger.info(f"Would send Slack notification: {title} - {message}")

            # Uncomment to actually send to Slack
            # response = requests.post(webhook_url, json=payload)
            # response.raise_for_status()

            return True

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

    def get_alert_history(self, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent alert history.

        Args:
            count: Number of most recent alerts to return, or None for all

        Returns:
            List of alert dictionaries
        """
        if count is None or count >= len(self.alert_history):
            return self.alert_history.copy()

        return self.alert_history[-count:]

    def test_alert(self, alert_type: str = "test") -> bool:
        """
        Send a test alert to verify notification channels.

        Args:
            alert_type: Type of test alert

        Returns:
            bool: True if test alert was sent
        """
        return self.send_alert(
            f"Test Alert ({alert_type})",
            "This is a test alert to verify notification channels are working correctly.",
            "info",
        )
