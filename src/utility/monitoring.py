"""Utility module for monitoring Spark applications.

This module provides functions for enabling and configuring Spark UI
for application monitoring and performance analysis.
"""

from typing import Dict, Any, Optional
import os
import socket
import webbrowser
from urllib.request import urlopen
from urllib.error import URLError
from time import sleep

from pyspark.sql import SparkSession
from pyspark.errors.exceptions.captured import AnalysisException


def enable_spark_ui(
    spark: SparkSession,
    port: int = 4040,
    interval_s: int = 5,
    retry_attempts: int = 5,
    auto_open: bool = True,
) -> bool:
    """
    Configure and check Spark UI for the given SparkSession.
    
    Note: This function checks if the Spark UI is available. If you want to
    enable the UI, you must configure it during SparkSession creation using
    get_spark_ui_config().
    
    Args:
        spark: The SparkSession to configure
        port: Port to use for the Spark UI (default: 4040)
        interval_s: Time to wait between retry attempts in seconds
        retry_attempts: Number of times to retry connecting to UI
        auto_open: Whether to automatically open the UI in a browser
        
    Returns:
        bool: True if UI is accessible
    """
    # Try to configure event log if not set
    try:
        # Configure history server if needed
        event_log_dir = os.path.join(os.getcwd(), "spark-events")
        os.makedirs(event_log_dir, exist_ok=True)
        
        spark.conf.set("spark.eventLog.enabled", "true")
        spark.conf.set("spark.eventLog.dir", event_log_dir)
    except AnalysisException as e:
        # Some configurations can't be changed after session creation, but we can proceed
        print(f"Note: Could not update event log settings: {e}")
    
    # Wait for UI to be available
    ui_url = f"http://localhost:{port}"
    for _ in range(retry_attempts):
        try:
            # Try to connect to the UI
            urlopen(ui_url, timeout=1)
            print(f"✅ Spark UI is available at: {ui_url}")
            
            # Open browser if requested
            if auto_open:
                webbrowser.open(ui_url)
                
            return True
        except URLError:
            print(f"Waiting for Spark UI to be available at {ui_url}...")
            sleep(interval_s)
    
    print(f"❌ Failed to connect to Spark UI at {ui_url} after {retry_attempts} attempts")
    return False


def get_spark_ui_config(port: int = 4040) -> Dict[str, str]:
    """
    Get Spark configuration settings for enabling the UI.
    
    Args:
        port: Port to use for the Spark UI
        
    Returns:
        Dict[str, str]: Dictionary of Spark configuration settings
    """
    event_log_dir = os.path.join(os.getcwd(), "spark-events")
    
    return {
        "spark.ui.enabled": "true",
        "spark.ui.port": str(port),
        "spark.ui.showConsoleProgress": "true",
        "spark.eventLog.enabled": "true",
        "spark.eventLog.dir": event_log_dir,
    }


def find_available_port(start_port: int = 4040, max_attempts: int = 10) -> Optional[int]:
    """
    Find an available port starting from the given port.
    
    Args:
        start_port: The port to start checking from
        max_attempts: Maximum number of ports to check
        
    Returns:
        Optional[int]: An available port, or None if no port was found
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return port
        except OSError:
            continue
    
    return None 