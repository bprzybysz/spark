"""Tests for alert delivery system."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.ml.monitoring.alerts import AlertManager

@pytest.fixture
def alert_manager():
    """Create an AlertManager instance for testing."""
    return AlertManager(
        model_name="test_model",
        email_config={
            "smtp_server": "smtp.test.com",
            "from": "test@example.com",
            "to": "alerts@example.com"
        },
        slack_webhook="https://hooks.slack.com/test",
        aggregation_window=timedelta(hours=1)
    )

def test_alert_creation(alert_manager):
    """Test basic alert creation."""
    with patch('src.ml.monitoring.alerts.requests.post') as mock_post:
        alert_manager.send_alert(
            alert_type="drift",
            message="Drift detected",
            severity="warning"
        )
        assert len(alert_manager.alert_history) == 1
        alert = alert_manager.alert_history[0]
        assert alert['type'] == "drift"
        assert alert['message'] == "Drift detected"
        assert alert['severity'] == "warning"
        assert isinstance(alert['timestamp'], datetime)

def test_alert_history_management(alert_manager):
    """Test alert history management and aggregation window."""
    # Send alerts with different timestamps
    with patch('src.ml.monitoring.alerts.datetime') as mock_datetime:
        # First alert at t=0
        current_time = datetime(2024, 1, 1, 12, 0)
        mock_datetime.now.return_value = current_time
        alert_manager.send_alert("drift", "First alert")
        
        # Second alert at t+30min
        current_time = datetime(2024, 1, 1, 12, 30)
        mock_datetime.now.return_value = current_time
        alert_manager.send_alert("performance", "Second alert")
        
        # Third alert at t+2h (outside window)
        current_time = datetime(2024, 1, 1, 14, 0)
        mock_datetime.now.return_value = current_time
        alert_manager.send_alert("drift", "Third alert")
        
        # History should be cleared after aggregation window
        assert len(alert_manager.alert_history) == 1
        assert alert_manager.alert_history[0]['message'] == "Third alert"

def test_alert_aggregation(alert_manager):
    """Test alert aggregation functionality."""
    with patch('src.ml.monitoring.alerts.requests.post') as mock_post:
        # Send multiple alerts
        alert_manager.send_alert("drift", "Drift alert 1")
        alert_manager.send_alert("performance", "Performance alert 1")
        alert_manager.send_alert("drift", "Drift alert 2")
        
        # Force aggregation
        alert_manager._send_aggregated_alerts()
        
        # Check if aggregated message was sent
        mock_post.assert_called()
        payload = mock_post.call_args[1]['json']
        message = payload['attachments'][0]['text']
        
        # Verify aggregated message format
        assert "Alert Summary for test_model" in message
        assert "DRIFT Alerts (2)" in message
        assert "PERFORMANCE Alerts (1)" in message
        assert "Drift alert 1" in message
        assert "Performance alert 1" in message
        assert "Drift alert 2" in message

def test_critical_alert_immediate_delivery(alert_manager):
    """Test that critical alerts are sent immediately."""
    with patch('src.ml.monitoring.alerts.requests.post') as mock_post:
        alert_manager.send_alert(
            alert_type="performance",
            message="Critical performance drop",
            severity="critical"
        )
        
        # Check immediate delivery
        mock_post.assert_called_once()
        payload = mock_post.call_args[1]['json']
        assert payload['attachments'][0]['color'] == '#ff0000'
        assert "Critical performance drop" in payload['attachments'][0]['text']

def test_email_alert_delivery(alert_manager):
    """Test email alert delivery."""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        alert_manager.send_alert(
            alert_type="drift",
            message="Test email alert",
            severity="warning"
        )
        alert_manager._send_aggregated_alerts()
        
        # Verify email was attempted
        mock_server.send_message.assert_called_once()
        
def test_slack_alert_delivery(alert_manager):
    """Test Slack alert delivery."""
    with patch('src.ml.monitoring.alerts.requests.post') as mock_post:
        alert_manager.send_alert(
            alert_type="performance",
            message="Test Slack alert",
            severity="warning"
        )
        alert_manager._send_aggregated_alerts()
        
        # Verify Slack message was sent
        mock_post.assert_called_once()
        payload = mock_post.call_args[1]['json']
        assert payload['attachments'][0]['color'] == '#ffcc00' 