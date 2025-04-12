"""Alert delivery system for model monitoring."""

import smtplib
import json
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AlertManager:
    """Manages alert delivery and aggregation."""
    
    def __init__(
        self,
        model_name: str,
        email_config: Optional[Dict[str, str]] = None,
        slack_webhook: Optional[str] = None,
        aggregation_window: timedelta = timedelta(hours=1)
    ):
        """Initialize alert manager.
        
        Args:
            model_name: Name of the model being monitored
            email_config: Email configuration (SMTP settings)
            slack_webhook: Slack webhook URL for notifications
            aggregation_window: Time window for alert aggregation
        """
        self.model_name = model_name
        self.email_config = email_config
        self.slack_webhook = slack_webhook
        self.aggregation_window = aggregation_window
        
        # Alert history for deduplication
        self.alert_history = []
        self.last_aggregation = datetime.now()
    
    def send_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warning",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send an alert through configured channels.
        
        Args:
            alert_type: Type of alert (e.g., "drift", "performance")
            message: Alert message
            severity: Alert severity level
            metadata: Additional alert metadata
        """
        current_time = datetime.now()
        alert = {
            'timestamp': current_time,
            'model': self.model_name,
            'type': alert_type,
            'message': message,
            'severity': severity,
            'metadata': metadata or {}
        }
        
        # Store in history
        self.alert_history.append(alert)
        
        # Check if we should aggregate based on the oldest alert's timestamp
        if len(self.alert_history) > 0:
            oldest_alert_time = min(a['timestamp'] for a in self.alert_history)
            if (current_time - oldest_alert_time) > self.aggregation_window:
                self._send_aggregated_alerts()
                self.last_aggregation = current_time
                # Keep only the current alert
                self.alert_history = [alert]
            elif severity == "critical":
                # Send immediate alert for high severity
                self._deliver_alert(alert)
    
    def _send_aggregated_alerts(self) -> None:
        """Aggregate and send alerts from the current window."""
        if not self.alert_history:
            return
            
        # Group alerts by type
        alerts_by_type = {}
        for alert in self.alert_history:
            alert_type = alert['type']
            if alert_type not in alerts_by_type:
                alerts_by_type[alert_type] = []
            alerts_by_type[alert_type].append(alert)
        
        # Create summary message
        summary = f"Alert Summary for {self.model_name}\n"
        summary += f"Time window: {self.last_aggregation} to {datetime.now()}\n\n"
        
        for alert_type, alerts in alerts_by_type.items():
            summary += f"{alert_type.upper()} Alerts ({len(alerts)}):\n"
            for alert in alerts:
                summary += f"- [{alert['severity']}] {alert['message']}\n"
            summary += "\n"
        
        # Deliver aggregated alert
        self._deliver_alert({
            'timestamp': datetime.now(),
            'model': self.model_name,
            'type': 'summary',
            'message': summary,
            'severity': 'info',
            'metadata': {'alert_count': len(self.alert_history)}
        })
        
        # Clear history
        self.alert_history = []
    
    def _deliver_alert(self, alert: Dict[str, Any]) -> None:
        """Deliver alert through configured channels.
        
        Args:
            alert: Alert information dictionary
        """
        if self.email_config:
            self._send_email_alert(alert)
        
        if self.slack_webhook:
            self._send_slack_alert(alert)
        
        # Always log the alert
        log_level = logging.CRITICAL if alert['severity'] == 'critical' else logging.WARNING
        logger.log(log_level, f"Alert: {alert['message']}")
    
    def _send_email_alert(self, alert: Dict[str, Any]) -> None:
        """Send alert via email.
        
        Args:
            alert: Alert information dictionary
        """
        try:
            msg = MIMEMultipart()
            msg['Subject'] = f"[{alert['severity'].upper()}] {self.model_name} Alert"
            msg['From'] = self.email_config['from']
            msg['To'] = self.email_config['to']
            
            body = f"Model: {self.model_name}\n"
            body += f"Type: {alert['type']}\n"
            body += f"Severity: {alert['severity']}\n"
            body += f"Time: {alert['timestamp']}\n\n"
            body += alert['message']
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.email_config['smtp_server']) as server:
                if self.email_config.get('use_tls', False):
                    server.starttls()
                if 'username' in self.email_config:
                    server.login(
                        self.email_config['username'],
                        self.email_config['password']
                    )
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
    
    def _send_slack_alert(self, alert: Dict[str, Any]) -> None:
        """Send alert to Slack.
        
        Args:
            alert: Alert information dictionary
        """
        try:
            # For aggregated alerts, use the highest severity color from the history
            if alert['type'] == 'summary' and self.alert_history:
                severities = [a['severity'] for a in self.alert_history]
                if 'critical' in severities:
                    severity = 'critical'
                elif 'warning' in severities:
                    severity = 'warning'
                else:
                    severity = 'info'
            else:
                severity = alert['severity']
            
            color = {
                'info': '#36a64f',
                'warning': '#ffcc00',
                'critical': '#ff0000'
            }.get(severity, '#cccccc')
            
            payload = {
                'attachments': [{
                    'color': color,
                    'title': f"{self.model_name} Alert",
                    'text': alert['message'],
                    'fields': [
                        {
                            'title': 'Type',
                            'value': alert['type'],
                            'short': True
                        },
                        {
                            'title': 'Severity',
                            'value': severity,
                            'short': True
                        }
                    ],
                    'ts': int(alert['timestamp'].timestamp())
                }]
            }
            
            requests.post(self.slack_webhook, json=payload, timeout=5)
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}") 