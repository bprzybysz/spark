"""
Parquet file processor for schema detection.

This module provides a processor for detecting and extracting schemas from Parquet files.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType

from src.stages.stage1_schema_detection.processors.base_processor import DataSourceProcessor
from src.utility.logging import setup_logger


class ParquetProcessor(DataSourceProcessor):
    """Processor for Parquet files."""

    def __init__(self, spark: SparkSession):
        """Initialize the Parquet processor.
        
        Args:
            spark: Active SparkSession for processing
        """
        self.spark = spark
        self.logger = setup_logger(__name__)
    
    def can_process(self, source_path: str) -> bool:
        """Check if the processor can handle the given source.
        
        Args:
            source_path: Path to the data source
            
        Returns:
            True if this processor can handle the source, False otherwise
        """
        if isinstance(source_path, str):
            return source_path.endswith('.parquet')
        return False
    
    def extract_schema(self, source_path: Union[str, Path], options: Optional[Dict[str, Any]] = None) -> StructType:
        """Extract schema from a Parquet file.
        
        Args:
            source_path: Path to the Parquet file
            options: Optional parameters for schema extraction
                - mergeSchema: "true" to merge schemas from different files
                
        Returns:
            Detected schema as a PySpark StructType
            
        Raises:
            FileNotFoundError: If file not found
        """
        source_path = str(source_path)
        options = options or {}
        
        self.logger.info(f"Extracting schema from Parquet file: {source_path}")
        
        # Validation
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Parquet file not found: {source_path}")
        
        try:
            # Configure reader
            reader = self.spark.read
            
            # Apply options
            for key, value in options.items():
                reader = reader.option(key, value)
            
            # Read schema without loading all data
            df = reader.parquet(source_path)
            
            return df.schema
            
        except Exception as e:
            self.logger.error(f"Error extracting schema from Parquet file: {e}")
            raise
    
    def extract_sample_data(
        self, 
        source_path: Union[str, Path], 
        limit: int = 100,
        options: Optional[Dict[str, Any]] = None
    ) -> DataFrame:
        """Extract sample data from a Parquet file.
        
        Args:
            source_path: Path to the Parquet file
            limit: Maximum number of records to extract
            options: Optional parameters for data extraction
                - mergeSchema: "true" to merge schemas from different files
                
        Returns:
            Spark DataFrame containing the sample data
            
        Raises:
            FileNotFoundError: If file not found
        """
        source_path = str(source_path)
        options = options or {}
        
        self.logger.info(f"Extracting sample data from Parquet file: {source_path}")
        
        # Validation
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Parquet file not found: {source_path}")
        
        try:
            # Configure reader
            reader = self.spark.read
            
            # Apply options
            for key, value in options.items():
                reader = reader.option(key, value)
            
            # Read data
            df = reader.parquet(source_path)
            
            # Limit records if specified
            if limit is not None:
                df = df.limit(limit)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error extracting sample data from Parquet file: {e}")
            raise
    
    def validate(self, source_path: Union[str, Path], options: Optional[Dict[str, Any]] = None) -> List[str]:
        """Validate a Parquet file.
        
        Args:
            source_path: Path to the Parquet file
            options: Optional parameters for validation
                
        Returns:
            List of validation messages/warnings
        """
        source_path = str(source_path)
        options = options or {}
        
        messages = []
        
        # Check if file exists
        if not os.path.exists(source_path):
            messages.append(f"Parquet file not found: {source_path}")
            return messages
        
        try:
            # Extract schema to check for issues
            schema = self.extract_schema(source_path, options)
            
            # Check for empty schema
            if len(schema.fields) == 0:
                messages.append("Schema contains no fields")
            
            # Try to extract a small sample to check for data issues
            try:
                sample = self.extract_sample_data(source_path, limit=10, options=options)
                
                # Check for empty dataset
                if sample.count() == 0:
                    messages.append("Parquet file contains no data")
                
            except Exception as e:
                messages.append(f"Error reading Parquet data: {str(e)}")
                
        except Exception as e:
            messages.append(f"Error validating Parquet file: {str(e)}")
        
        return messages 