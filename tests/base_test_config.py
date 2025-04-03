"""
Base test configuration and utilities for all test stages
"""

import os
import sys
import pytest
import findspark
findspark.init()

from pyspark.sql import SparkSession
from typing import Optional

class BaseSparkTest:
    """Base class for all Spark test stages"""
    
    _spark: Optional[SparkSession] = None
    
    @classmethod
    def setup_class(cls):
        """Set up test environment for the class"""
        try:
            # Set Python environment for Spark
            python_executable = sys.executable
            os.environ["PYSPARK_PYTHON"] = python_executable
            os.environ["PYSPARK_DRIVER_PYTHON"] = python_executable
            os.environ["PYTHONPATH"] = f"{os.environ.get('PYTHONPATH', '')}:{os.getcwd()}"
            
            # Create Spark session with common configurations
            if cls._spark is None or not cls._spark.sparkContext._jsc:
                if cls._spark is not None:
                    try:
                        cls._spark.stop()
                    except:
                        pass
                    cls._spark = None
                
                cls._spark = (SparkSession.builder
                    .appName("SparkTests")
                    .master("local[*]")
                    .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
                    .config("spark.sql.execution.arrow.pyspark.enabled", "true")
                    .config("spark.driver.memory", "2g")
                    .config("spark.executor.memory", "2g")
                    .config("spark.sql.shuffle.partitions", "2")
                    .config("spark.default.parallelism", "4")
                    .config("spark.sql.execution.arrow.maxRecordsPerBatch", "10000")
                    .config("spark.pyspark.python", python_executable)
                    .config("spark.pyspark.driver.python", python_executable)
                    .config("spark.driver.host", "localhost")
                    .config("spark.driver.bindAddress", "127.0.0.1")
                    .config("spark.sql.session.timeZone", "UTC")
                    .config("spark.sql.warehouse.dir", "spark-warehouse")
                    .config("spark.sql.catalogImplementation", "in-memory")
                    .config("spark.jars.packages", "org.apache.spark:spark-sql_2.12:3.5.0")
                    .config("spark.jars.repositories", "https://repos.spark-packages.org")
                    .getOrCreate())
                
                # Set log level
                cls._spark.sparkContext.setLogLevel("ERROR")
        except Exception as e:
            pytest.fail(f"Failed to initialize Spark session: {str(e)}")
    
    @classmethod
    def teardown_class(cls):
        """Clean up after all tests in the class"""
        if cls._spark is not None:
            try:
                cls._spark.stop()
            except:
                pass
            cls._spark = None
    
    def setup_method(self, method):
        """Set up test environment before each test method"""
        try:
            if self._spark is None or not self._spark.sparkContext._jsc:
                self.setup_class()
            assert self._spark is not None and self._spark.sparkContext._jsc, "Spark session not properly initialized"
        except Exception as e:
            pytest.fail(f"Failed to initialize Spark session in setup_method: {str(e)}")
    
    def teardown_method(self, method):
        """Clean up after each test method"""
        if self._spark is not None:
            try:
                self._spark.catalog.clearCache()
            except:
                pass
    
    @property
    def spark(self) -> SparkSession:
        """Get the Spark session"""
        try:
            if self._spark is None or not self._spark.sparkContext._jsc:
                self.setup_class()
            assert self._spark is not None and self._spark.sparkContext._jsc, "Spark session not properly initialized"
            return self._spark
        except Exception as e:
            pytest.fail(f"Failed to get Spark session: {str(e)}")
            raise  # This will never be reached due to pytest.fail, but it helps type checking

    @staticmethod
    def resource_path(relative_path: str) -> str:
        """Get absolute path for test resources"""
        return os.path.join(os.getcwd(), "tests", "resources", relative_path)
    
    @staticmethod
    def stage_path(stage: str, relative_path: str) -> str:
        """Get absolute path for stage-specific test resources"""
        return os.path.join(os.getcwd(), "tests", stage, "resources", relative_path) 