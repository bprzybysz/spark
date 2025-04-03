"""
Spark session provider module.

This module provides a factory for creating and configuring Spark sessions.
"""
from typing import Dict, Any, Optional

import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.conf import SparkConf


class SparkSessionFactory:
    """Factory for creating and configuring Spark sessions."""
    
    def __init__(
        self,
        app_name: str = "SparkETLMLPipeline",
        master: str = "local[*]",
        config: Optional[Dict[str, Any]] = None,
        enable_hive: bool = True,
        enable_arrow: bool = True,
    ):
        """
        Initialize the Spark session factory.
        
        Args:
            app_name: The name of the Spark application
            master: The Spark master URL
            config: Additional Spark configuration options
            enable_hive: Whether to enable Hive support
            enable_arrow: Whether to enable Arrow optimization for Python UDFs
        """
        self.app_name = app_name
        self.master = master
        self.config = config or {}
        self.enable_hive = enable_hive
        self.enable_arrow = enable_arrow
        self._session = None
    
    def create_session(self) -> SparkSession:
        """
        Create a new Spark session.
        
        Returns:
            SparkSession: Configured Spark session
        """
        # Create Spark configuration
        conf = SparkConf().setAppName(self.app_name).setMaster(self.master)
        
        # Add additional configuration
        for key, value in self.config.items():
            conf.set(key, value)
        
        # Create session builder
        builder = SparkSession.builder.config(conf=conf)
        
        # Enable Hive support if requested
        if self.enable_hive:
            builder = builder.enableHiveSupport()
        
        # Create the session
        session = builder.getOrCreate()
        
        # Configure Arrow for better Python UDF performance
        if self.enable_arrow:
            session.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
        
        return session
    
    def get_session(self) -> SparkSession:
        """
        Get the Spark session, creating it if it doesn't exist.
        
        Returns:
            SparkSession: Configured Spark session
        """
        if self._session is None:
            self._session = self.create_session()
        
        return self._session
    
    def stop_session(self) -> None:
        """Stop the Spark session if it exists."""
        if self._session is not None:
            self._session.stop()
            self._session = None


def create_spark_session(
    app_name: str = "SparkETLMLPipeline",
    master: str = "local[*]",
    config: Optional[Dict[str, Any]] = None,
    enable_hive: bool = True,
    enable_arrow: bool = True,
) -> SparkSession:
    """
    Create a configured Spark session.
    
    This is a convenience function for creating a Spark session without
    explicitly using the SparkSessionFactory.
    
    Args:
        app_name: The name of the Spark application
        master: The Spark master URL
        config: Additional Spark configuration options
        enable_hive: Whether to enable Hive support
        enable_arrow: Whether to enable Arrow optimization for Python UDFs
        
    Returns:
        SparkSession: Configured Spark session
    """
    factory = SparkSessionFactory(
        app_name=app_name,
        master=master,
        config=config,
        enable_hive=enable_hive,
        enable_arrow=enable_arrow,
    )
    
    return factory.create_session() 