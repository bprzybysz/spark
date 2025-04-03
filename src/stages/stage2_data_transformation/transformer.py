"""Data transformation and validation implementation.

This module provides functionality for transforming and validating data
according to the detected schema from Stage 1.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType
from pyspark.sql import functions as F

from src.utility.base import BaseStage, StageResult, StageStatus
from src.utility.logging import setup_logger
from src.stages.stage1_schema_detection.detector import SchemaDetectionResult

class TransformationType(Enum):
    """Supported data transformation types."""
    CLEAN = "clean"  # Basic data cleaning
    CONVERT = "convert"  # Type conversion
    FORMAT = "format"  # Data formatting
    VALIDATE = "validate"  # Data validation
    CUSTOM = "custom"  # Custom transformation

@dataclass
class DataQualityMetrics:
    """Metrics for data quality assessment.
    
    Attributes:
        total_rows: Total number of rows processed
        null_counts: Dictionary of null counts per column
        unique_counts: Dictionary of unique value counts per column
        invalid_values: Dictionary of invalid value counts per column
        validation_errors: List of validation error messages
    """
    total_rows: int
    null_counts: Dict[str, int]
    unique_counts: Dict[str, int]
    invalid_values: Dict[str, int]
    validation_errors: List[str]

@dataclass
class TransformationResult:
    """Result of data transformation process.
    
    Attributes:
        transformed_data: Transformed DataFrame
        original_schema: Original schema from Stage 1
        transformed_schema: Schema after transformations
        quality_metrics: Data quality metrics
        validation_errors: List of validation errors
    """
    transformed_data: Optional[DataFrame]
    original_schema: StructType
    transformed_schema: StructType
    quality_metrics: DataQualityMetrics
    validation_errors: List[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.validation_errors is None:
            self.validation_errors = []

class DataTransformer:
    """Data transformation and validation implementation."""
    
    def __init__(self, spark: SparkSession):
        """Initialize the data transformer.
        
        Args:
            spark: Active SparkSession for processing
        """
        self.spark = spark
        self.logger = setup_logger(__name__)
    
    def transform_data(
        self,
        data: DataFrame,
        schema: StructType,
        transformations: List[Dict[str, Any]],
        **options: Dict
    ) -> TransformationResult:
        """Apply transformations to the data.
        
        Args:
            data: Input DataFrame to transform
            schema: Expected schema (from Stage 1)
            transformations: List of transformation configurations
            **options: Additional transformation options
            
        Returns:
            TransformationResult containing transformed data and metrics
            
        Raises:
            ValueError: If transformation configuration is invalid
        """
        try:
            # Initialize metrics
            metrics = self._initialize_metrics(data)
            
            # Track the evolving schema
            current_schema = schema
            transformed_df = data
            
            # Apply each transformation in sequence
            for transform_config in transformations:
                transform_type = TransformationType(transform_config['type'])
                
                if transform_type == TransformationType.CLEAN:
                    transformed_df = self._clean_data(
                        transformed_df,
                        transform_config.get('columns', []),
                        transform_config.get('options', {})
                    )
                elif transform_type == TransformationType.CONVERT:
                    transformed_df = self._convert_types(
                        transformed_df,
                        transform_config.get('type_mappings', {}),
                        transform_config.get('options', {})
                    )
                elif transform_type == TransformationType.FORMAT:
                    transformed_df = self._format_data(
                        transformed_df,
                        transform_config.get('format_specs', {}),
                        transform_config.get('options', {})
                    )
                elif transform_type == TransformationType.VALIDATE:
                    self._validate_data(
                        transformed_df,
                        transform_config.get('rules', []),
                        metrics
                    )
                elif transform_type == TransformationType.CUSTOM:
                    if 'function' not in transform_config:
                        raise ValueError("Custom transformation requires 'function' specification")
                    transformed_df = transform_config['function'](
                        transformed_df,
                        **transform_config.get('args', {})
                    )
                
                # Update schema after transformation
                current_schema = transformed_df.schema
            
            # Final validation
            self._validate_schema_compliance(transformed_df, schema, metrics)
            
            return TransformationResult(
                transformed_data=transformed_df,
                original_schema=schema,
                transformed_schema=current_schema,
                quality_metrics=metrics
            )
            
        except Exception as e:
            self.logger.error(f"Data transformation failed: {e}")
            return TransformationResult(
                transformed_data=None,
                original_schema=schema,
                transformed_schema=schema,
                quality_metrics=metrics,
                validation_errors=[str(e)]
            )
    
    def _initialize_metrics(self, df: DataFrame) -> DataQualityMetrics:
        """Initialize data quality metrics.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Initial DataQualityMetrics
        """
        total_rows = df.count()
        
        # Calculate initial metrics
        null_counts = {
            col: df.filter(F.col(col).isNull()).count()
            for col in df.columns
        }
        
        unique_counts = {
            col: df.select(col).distinct().count()
            for col in df.columns
        }
        
        return DataQualityMetrics(
            total_rows=total_rows,
            null_counts=null_counts,
            unique_counts=unique_counts,
            invalid_values={},
            validation_errors=[]
        )
    
    def _clean_data(
        self,
        df: DataFrame,
        columns: List[str],
        options: Dict[str, Any]
    ) -> DataFrame:
        """Clean data in specified columns.
        
        Args:
            df: Input DataFrame
            columns: Columns to clean
            options: Cleaning options
            
        Returns:
            Cleaned DataFrame
        """
        cleaned_df = df
        
        for col in columns:
            if col not in df.columns:
                continue
                
            # Apply cleaning operations based on options
            if options.get('remove_whitespace', True):
                cleaned_df = cleaned_df.withColumn(
                    col,
                    F.trim(F.col(col))
                )
            
            if options.get('replace_nulls') is not None:
                cleaned_df = cleaned_df.withColumn(
                    col,
                    F.coalesce(F.col(col), F.lit(options['replace_nulls']))
                )
        
        return cleaned_df
    
    def _convert_types(
        self,
        df: DataFrame,
        type_mappings: Dict[str, str],
        options: Dict[str, Any]
    ) -> DataFrame:
        """Convert column data types.
        
        Args:
            df: Input DataFrame
            type_mappings: Column to type mappings
            options: Conversion options
            
        Returns:
            DataFrame with converted types
        """
        converted_df = df
        
        for col, target_type in type_mappings.items():
            if col not in df.columns:
                continue
                
            try:
                # Handle different type conversions
                if target_type == "timestamp":
                    converted_df = converted_df.withColumn(
                        col,
                        F.to_timestamp(F.col(col), options.get('timestamp_format'))
                    )
                elif target_type == "date":
                    converted_df = converted_df.withColumn(
                        col,
                        F.to_date(F.col(col), options.get('date_format'))
                    )
                elif target_type in ["int", "long", "float", "double"]:
                    converted_df = converted_df.withColumn(
                        col,
                        F.col(col).cast(target_type)
                    )
                elif target_type == "boolean":
                    converted_df = converted_df.withColumn(
                        col,
                        F.col(col).cast("boolean")
                    )
            except Exception as e:
                self.logger.warning(f"Type conversion failed for column {col}: {e}")
        
        return converted_df
    
    def _format_data(
        self,
        df: DataFrame,
        format_specs: Dict[str, Dict[str, Any]],
        options: Dict[str, Any]
    ) -> DataFrame:
        """Format data according to specifications.
        
        Args:
            df: Input DataFrame
            format_specs: Column formatting specifications
            options: Formatting options
            
        Returns:
            Formatted DataFrame
        """
        formatted_df = df
        
        for col, specs in format_specs.items():
            if col not in df.columns:
                continue
                
            # Apply formatting based on specifications
            if 'case' in specs:
                if specs['case'] == 'upper':
                    formatted_df = formatted_df.withColumn(
                        col,
                        F.upper(F.col(col))
                    )
                elif specs['case'] == 'lower':
                    formatted_df = formatted_df.withColumn(
                        col,
                        F.lower(F.col(col))
                    )
            
            if 'decimal_places' in specs:
                formatted_df = formatted_df.withColumn(
                    col,
                    F.round(F.col(col), specs['decimal_places'])
                )
        
        return formatted_df
    
    def _validate_data(
        self,
        df: DataFrame,
        rules: List[Dict[str, Any]],
        metrics: DataQualityMetrics
    ) -> None:
        """Validate data against rules.
        
        Args:
            df: Input DataFrame
            rules: Validation rules
            metrics: Metrics to update
        """
        for rule in rules:
            column = rule.get('column')
            rule_type = rule.get('type')
            
            if not column or not rule_type or column not in df.columns:
                continue
            
            if rule_type == 'not_null':
                null_count = df.filter(F.col(column).isNull()).count()
                if null_count > 0:
                    metrics.validation_errors.append(
                        f"Column {column} contains {null_count} null values"
                    )
                    metrics.invalid_values[column] = null_count
            
            elif rule_type == 'unique':
                duplicate_count = (
                    df.groupBy(column)
                    .count()
                    .filter(F.col('count') > 1)
                    .count()
                )
                if duplicate_count > 0:
                    metrics.validation_errors.append(
                        f"Column {column} contains {duplicate_count} duplicate values"
                    )
                    metrics.invalid_values[column] = duplicate_count
            
            elif rule_type == 'range':
                min_val = rule.get('min')
                max_val = rule.get('max')
                if min_val is not None or max_val is not None:
                    condition = None
                    if min_val is not None and max_val is not None:
                        condition = ~F.col(column).between(min_val, max_val)
                    elif min_val is not None:
                        condition = F.col(column) < min_val
                    else:
                        condition = F.col(column) > max_val
                    
                    invalid_count = df.filter(condition).count()
                    if invalid_count > 0:
                        metrics.validation_errors.append(
                            f"Column {column} has {invalid_count} values outside range"
                        )
                        metrics.invalid_values[column] = invalid_count
    
    def _validate_schema_compliance(
        self,
        df: DataFrame,
        expected_schema: StructType,
        metrics: DataQualityMetrics
    ) -> None:
        """Validate data compliance with expected schema.
        
        Args:
            df: Input DataFrame
            expected_schema: Expected schema
            metrics: Metrics to update
        """
        actual_schema = df.schema
        
        # Check for missing columns
        expected_cols = {f.name: f.dataType for f in expected_schema.fields}
        actual_cols = {f.name: f.dataType for f in actual_schema.fields}
        
        for col, dtype in expected_cols.items():
            if col not in actual_cols:
                metrics.validation_errors.append(f"Missing column: {col}")
            elif actual_cols[col] != dtype:
                metrics.validation_errors.append(
                    f"Column {col} has incorrect type: "
                    f"expected {dtype}, got {actual_cols[col]}"
                )

class DataTransformationStage(BaseStage):
    """Stage implementation for data transformation."""
    
    def __init__(
        self,
        spark: SparkSession,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the data transformation stage.
        
        Args:
            spark: Active SparkSession
            config: Optional stage configuration
        """
        super().__init__("data_transformation", spark, config)
        self.transformer = DataTransformer(spark)
    
    def validate_config(self) -> List[str]:
        """Validate stage configuration.
        
        Returns:
            List of validation error messages, empty if valid
        """
        errors = []
        required_fields = [
            'input_path',
            'output_path',
            'transformations'
        ]
        
        for field in required_fields:
            if field not in self.config:
                errors.append(f"Missing required config field: {field}")
        
        if 'transformations' in self.config:
            if not isinstance(self.config['transformations'], list):
                errors.append("'transformations' must be a list")
            else:
                for i, transform in enumerate(self.config['transformations']):
                    if 'type' not in transform:
                        errors.append(
                            f"Transformation at index {i} missing 'type' field"
                        )
                    elif transform['type'] not in [t.value for t in TransformationType]:
                        errors.append(
                            f"Invalid transformation type at index {i}: {transform['type']}"
                        )
        
        return errors
    
    def execute(self) -> StageResult[TransformationResult]:
        """Execute data transformation.
        
        Returns:
            StageResult containing the transformation result
        """
        # Validate configuration
        if errors := self.validate_config():
            return StageResult(
                status=StageStatus.FAILED,
                stage_name=self.name,
                errors=errors
            )
        
        try:
            # Load input data
            input_path = self.config['input_path']
            reader = self.spark.read
            
            if input_path.endswith('.csv'):
                df = reader.csv(input_path, header=True, inferSchema=True)
            elif input_path.endswith('.json'):
                df = reader.json(input_path)
            elif input_path.endswith('.parquet'):
                df = reader.parquet(input_path)
            else:
                raise ValueError(f"Unsupported input format: {input_path}")
            
            # Apply transformations
            result = self.transformer.transform_data(
                df,
                df.schema,  # Use inferred schema as original
                self.config['transformations']
            )
            
            # Save transformed data if successful
            if (
                result.transformed_data is not None
                and not result.validation_errors
                and 'output_path' in self.config
            ):
                output_path = self.config['output_path']
                writer = result.transformed_data.write.mode('overwrite')
                
                if output_path.endswith('.csv'):
                    writer.csv(output_path)
                elif output_path.endswith('.json'):
                    writer.json(output_path)
                elif output_path.endswith('.parquet'):
                    writer.parquet(output_path)
            
            # Determine stage status
            status = (
                StageStatus.COMPLETED
                if not result.validation_errors
                else StageStatus.FAILED
            )
            
            return StageResult(
                status=status,
                stage_name=self.name,
                output=result,
                errors=result.validation_errors
            )
            
        except Exception as e:
            self.logger.error(f"Data transformation failed: {e}")
            return StageResult(
                status=StageStatus.FAILED,
                stage_name=self.name,
                errors=[str(e)]
            ) 