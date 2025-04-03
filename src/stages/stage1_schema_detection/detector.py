"""Schema detection implementation for various data sources.

This module provides functionality to automatically detect and infer schemas
from different data sources including CSV, JSON, Parquet, and Hive tables.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import csv
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType

from src.utility.base import BaseStage, StageResult, StageStatus
from src.utility.logging import setup_logger

class DataSourceType(Enum):
    """Supported data source types."""
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    HIVE = "hive"

@dataclass
class SchemaDetectionResult:
    """Result of schema detection process.
    
    Attributes:
        source_type: Type of the data source
        schema: Detected schema in Spark StructType format
        sample_data: Optional sample of the data
        validation_errors: List of any validation errors encountered
    """
    source_type: DataSourceType
    schema: StructType
    sample_data: Optional[pd.DataFrame] = None
    validation_errors: List[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.validation_errors is None:
            self.validation_errors = []

class SchemaDetectionStage(BaseStage):
    """Stage implementation for schema detection."""
    
    def __init__(
        self,
        spark: SparkSession,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the schema detection stage.
        
        Args:
            spark: Active SparkSession
            config: Optional stage configuration
        """
        super().__init__("schema_detection", spark, config)
        self.detector = SchemaDetector(spark)
    
    def validate_config(self) -> List[str]:
        """Validate stage configuration.
        
        Returns:
            List of validation error messages, empty if valid
        """
        errors = []
        required_fields = ['source_path', 'source_type']
        
        for field in required_fields:
            if field not in self.config:
                errors.append(f"Missing required config field: {field}")
        
        return errors
    
    def execute(self) -> StageResult[SchemaDetectionResult]:
        """Execute schema detection.
        
        Returns:
            StageResult containing the schema detection result
        """
        # Validate configuration
        if errors := self.validate_config():
            return StageResult(
                status=StageStatus.FAILED,
                stage_name=self.name,
                errors=errors
            )
        
        try:
            # Detect schema
            source_path = self.config['source_path']
            source_type = (
                DataSourceType(self.config['source_type'])
                if 'source_type' in self.config
                else None
            )
            
            result = self.detector.detect_schema(
                source_path,
                source_type,
                sample_size=self.config.get('sample_size', 1000)
            )
            
            # Check for detection errors
            if result.validation_errors:
                return StageResult(
                    status=StageStatus.FAILED,
                    stage_name=self.name,
                    output=result,
                    errors=result.validation_errors
                )
            
            # Validate result
            validation_messages = self.detector.validate_schema(result)
            
            return StageResult(
                status=StageStatus.COMPLETED,
                stage_name=self.name,
                output=result,
                warnings=validation_messages
            )
            
        except Exception as e:
            self.logger.error(f"Schema detection failed: {e}")
            return StageResult(
                status=StageStatus.FAILED,
                stage_name=self.name,
                errors=[str(e)]
            )

class SchemaDetector:
    """Schema detection for various data sources."""
    
    def __init__(self, spark: SparkSession):
        """Initialize the schema detector.
        
        Args:
            spark: Active SparkSession for processing
        """
        self.spark = spark
        self.logger = setup_logger(__name__)
    
    def detect_schema(
        self,
        source_path: Union[str, Path],
        source_type: Optional[DataSourceType] = None,
        sample_size: int = 1000,
        **options: Dict
    ) -> SchemaDetectionResult:
        """Detect schema from a data source.
        
        Args:
            source_path: Path to the data source
            source_type: Optional explicit source type, if not provided will be inferred
            sample_size: Number of records to sample for schema detection
            **options: Additional options passed to the reader
            
        Returns:
            SchemaDetectionResult containing the detected schema
            
        Raises:
            ValueError: If source type cannot be determined or is unsupported
        """
        source_path = str(source_path)
        
        # Infer source type if not provided
        if source_type is None:
            source_type = self._infer_source_type(source_path)
            
        self.logger.info(f"Detecting schema for {source_type.value} source: {source_path}")
        
        try:
            # For Hive tables, we don't need to check file existence
            if source_type != DataSourceType.HIVE:
                # Check if file exists
                if not Path(source_path).exists():
                    raise FileNotFoundError(f"File not found: {source_path}")
            
            # Validate file format
            if source_type == DataSourceType.CSV:
                self._validate_csv_format(source_path)
            
            # Read sample data
            reader = self.spark.read.options(**options)
            
            try:
                if source_type == DataSourceType.CSV:
                    df = reader.csv(source_path, inferSchema=True, header=True)
                elif source_type == DataSourceType.JSON:
                    df = reader.json(source_path)
                elif source_type == DataSourceType.PARQUET:
                    df = reader.parquet(source_path)
                elif source_type == DataSourceType.HIVE:
                    # Check if table exists
                    if not self.spark._jsparkSession.catalog().tableExists(source_path):
                        raise ValueError(f"Table or view not found: {source_path}")
                    df = self.spark.table(source_path)
                else:
                    raise ValueError(f"Unsupported source type: {source_type}")
                
                # Sample data
                sample_df = df.limit(sample_size)
                
                # Convert sample to pandas for easier inspection
                pandas_sample = sample_df.toPandas() if sample_size > 0 else None
                
                return SchemaDetectionResult(
                    source_type=source_type,
                    schema=df.schema,
                    sample_data=pandas_sample
                )
                
            except Exception as e:
                if "Table or view not found" in str(e):
                    raise ValueError(f"Table or view not found: {source_path}")
                raise
                
        except Exception as e:
            self.logger.error(f"Schema detection failed: {e}")
            return SchemaDetectionResult(
                source_type=source_type,
                schema=StructType([]),  # Empty schema
                validation_errors=[str(e)]
            )
    
    def _validate_csv_format(self, file_path: str) -> None:
        """Validate CSV file format.
        
        Args:
            file_path: Path to the CSV file
            
        Raises:
            ValueError: If CSV format is invalid
        """
        try:
            with open(file_path, 'r') as f:
                # Read first few lines to check format
                sample = list(csv.reader(f, delimiter=','))
                if not sample:
                    raise ValueError("Empty CSV file")
                
                # Check consistent number of columns
                num_cols = len(sample[0])
                for i, row in enumerate(sample[1:], 1):
                    if len(row) != num_cols:
                        raise ValueError(
                            f"Inconsistent number of columns at row {i}: "
                            f"expected {num_cols}, got {len(row)}"
                        )
        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {e}")
    
    def _infer_source_type(self, source_path: str) -> DataSourceType:
        """Infer the data source type from the path or content.
        
        Args:
            source_path: Path to the data source
            
        Returns:
            Detected DataSourceType
            
        Raises:
            ValueError: If source type cannot be determined
        """
        if source_path.endswith('.csv'):
            return DataSourceType.CSV
        elif source_path.endswith('.json'):
            return DataSourceType.JSON
        elif source_path.endswith('.parquet'):
            return DataSourceType.PARQUET
        elif '.' not in source_path:  # Assume Hive table if no extension
            return DataSourceType.HIVE
        else:
            raise ValueError(f"Could not determine source type for: {source_path}")
    
    def validate_schema(self, result: SchemaDetectionResult) -> List[str]:
        """Validate the detected schema for common issues.
        
        Args:
            result: Schema detection result to validate
            
        Returns:
            List of validation messages/warnings
        """
        messages = []
        
        # Check for empty schema
        if len(result.schema.fields) == 0:
            messages.append("Schema contains no fields")
            
        # Check for potential data type issues in sample
        if result.sample_data is not None:
            # Check for columns with mixed types
            for col in result.sample_data.columns:
                if result.sample_data[col].dtype == 'object':
                    messages.append(f"Column '{col}' has mixed or object data type")
                    
            # Check for columns with high null percentage
            null_percentages = result.sample_data.isnull().mean()
            for col, pct in null_percentages.items():
                if pct > 0:  # Any nulls
                    messages.append(
                        f"Column '{col}' has {pct*100:.1f}% null values"
                    )
        
        return messages 