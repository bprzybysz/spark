"""
Unit tests for Spark UI monitoring utilities.
"""

import unittest
import socket
from unittest.mock import patch, MagicMock
import os
from urllib.error import URLError

from pyspark.sql import SparkSession
from pyspark.errors.exceptions.captured import AnalysisException

from src.utility.monitoring import (
    enable_spark_ui,
    get_spark_ui_config,
    find_available_port
)


class TestSparkUIMonitoring(unittest.TestCase):
    """Test cases for Spark UI monitoring utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a minimal SparkSession for tests with UI already enabled
        ui_config = get_spark_ui_config(port=4040)
        self.spark = SparkSession.builder \
            .appName("TestSparkMonitoring") \
            .master("local[1]") \
            .config("spark.ui.enabled", "true") \
            .config("spark.ui.port", "4040") \
            .getOrCreate()
    
    def tearDown(self):
        """Tear down test fixtures."""
        if self.spark:
            self.spark.stop()
    
    def test_get_spark_ui_config(self):
        """Test the get_spark_ui_config function."""
        # Test with default port
        config = get_spark_ui_config()
        self.assertEqual(config["spark.ui.enabled"], "true")
        self.assertEqual(config["spark.ui.port"], "4040")
        self.assertEqual(config["spark.ui.showConsoleProgress"], "true")
        self.assertTrue("spark.eventLog.enabled" in config)
        self.assertTrue("spark.eventLog.dir" in config)
        
        # Test with custom port
        config = get_spark_ui_config(port=4050)
        self.assertEqual(config["spark.ui.port"], "4050")
    
    @patch('src.utility.monitoring.urlopen')
    @patch('src.utility.monitoring.webbrowser.open')
    @patch('src.utility.monitoring.os.makedirs')
    def test_enable_spark_ui_success(self, mock_makedirs, mock_webbrowser_open, mock_urlopen):
        """Test enable_spark_ui with successful connection."""
        # Configure mocks
        mock_urlopen.return_value = MagicMock()
        mock_makedirs.return_value = None
        
        # Call function
        result = enable_spark_ui(
            self.spark,
            port=4040,
            interval_s=0.1,
            retry_attempts=1,
            auto_open=True
        )
        
        # Check results
        self.assertTrue(result)
        mock_urlopen.assert_called_once()
        mock_webbrowser_open.assert_called_once_with("http://localhost:4040")
        mock_makedirs.assert_called_once()
    
    @patch('src.utility.monitoring.urlopen')
    @patch('src.utility.monitoring.webbrowser.open')
    @patch('src.utility.monitoring.os.makedirs')
    def test_enable_spark_ui_failure(self, mock_makedirs, mock_webbrowser_open, mock_urlopen):
        """Test enable_spark_ui with connection failure."""
        # Configure mocks to simulate connection failure
        mock_urlopen.side_effect = URLError("Connection failed")
        mock_makedirs.return_value = None
        
        # Call function
        result = enable_spark_ui(
            self.spark,
            port=4040,
            interval_s=0.1,
            retry_attempts=2,
            auto_open=True
        )
        
        # Check results
        self.assertFalse(result)
        self.assertEqual(mock_urlopen.call_count, 2)  # Should retry twice
        mock_webbrowser_open.assert_not_called()  # Should not open browser
        mock_makedirs.assert_called_once()
    
    @patch('socket.socket')
    def test_find_available_port_success(self, mock_socket):
        """Test find_available_port with available port."""
        # Configure mock to succeed for the first port
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        
        # Call function
        port = find_available_port(start_port=4040, max_attempts=3)
        
        # Check results
        self.assertEqual(port, 4040)
        mock_socket_instance.bind.assert_called_once_with(("localhost", 4040))
    
    @patch('socket.socket')
    def test_find_available_port_first_busy(self, mock_socket):
        """Test find_available_port with first port busy."""
        # Configure mock to fail for first port, succeed for second
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        
        # First call raises OSError, second succeeds
        mock_socket_instance.bind.side_effect = [OSError(), None]
        
        # Call function
        port = find_available_port(start_port=4040, max_attempts=3)
        
        # Check results
        self.assertEqual(port, 4041)
        self.assertEqual(mock_socket_instance.bind.call_count, 2)
    
    @patch('socket.socket')
    def test_find_available_port_all_busy(self, mock_socket):
        """Test find_available_port with all ports busy."""
        # Configure mock to fail for all ports
        mock_socket_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance
        mock_socket_instance.bind.side_effect = OSError()
        
        # Call function
        port = find_available_port(start_port=4040, max_attempts=3)
        
        # Check results
        self.assertIsNone(port)
        self.assertEqual(mock_socket_instance.bind.call_count, 3)


if __name__ == '__main__':
    unittest.main() 