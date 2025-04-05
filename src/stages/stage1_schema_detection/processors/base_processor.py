"""
Base processor abstract class for data source processors.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType


class DataSourceProcessor(ABC):
    """Base class for all data source processors."""
    
    def __init__(self, spark: SparkSession):
        """Initialize the data source processor.
        
        Args:
            spark: Active SparkSession
        """
        self.spark = spark
    
    @abstractmethod
    def can_process(self, source_path: str) -> bool:
        """Check if this processor can handle the given source path.
        
        Args:
            source_path: Path to the data source
            
        Returns:
            True if this processor can handle the source, False otherwise
        """
        pass
    
    @abstractmethod
    def extract_schema(self, source_path: str, options: Optional[Dict] = None) -> StructType:
        """Extract schema from the data source.
        
        Args:
            source_path: Path to the data source
            options: Additional options for processing
            
        Returns:
            Extracted schema as a StructType
        """
        pass
    
    @abstractmethod
    def extract_sample_data(self, source_path: str, limit: int = 100, 
                           options: Optional[Dict] = None) -> DataFrame:
        """Extract sample data from the source.
        
        Args:
            source_path: Path to the data source
            limit: Maximum number of records to extract
            options: Additional options for processing
            
        Returns:
            DataFrame containing sample data
        """
        pass
    
    @abstractmethod
    def validate(self, source_path: str, options: Optional[Dict] = None) -> List[str]:
        """Validate the data source.
        
        Args:
            source_path: Path to the data source
            options: Additional options for processing
            
        Returns:
            List of validation messages/errors
        """
        pass 