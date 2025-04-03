"""
Data Quality Module for Stage 3

This module implements data quality checks, metrics calculation, and anomaly detection
for the data processing pipeline.
"""

from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

class DataQualityChecker:
    """
    Main class for performing data quality checks and generating quality metrics.
    """
    
    def __init__(self, spark: SparkSession):
        """
        Initialize the DataQualityChecker.
        
        Args:
            spark: Active SparkSession for processing
        """
        self.spark = spark
        self.quality_metrics = {}
        self.validation_results = {}
        
    def validate_completeness(self, df: DataFrame, required_columns: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Check completeness of required columns.
        
        Args:
            df: Input DataFrame
            required_columns: List of columns that should be complete
            
        Returns:
            Dictionary with completeness metrics for each column
        """
        completeness = {}
        total_rows = df.count()
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Column {col} not found in DataFrame")
                
            non_null_count = df.filter(F.col(col).isNotNull()).count()
            completeness[col] = {
                "completeness": non_null_count / total_rows if total_rows > 0 else 1.0,
                "total_rows": total_rows,
                "non_null_rows": non_null_count
            }
            
        return completeness
    
    def validate_data_types(self, df: DataFrame, expected_types: Dict[str, str]) -> Dict[str, Dict[str, bool]]:
        """
        Validate that columns match their expected data types.
        
        Args:
            df: Input DataFrame
            expected_types: Dictionary mapping column names to expected types
            
        Returns:
            Dictionary indicating type validation results for each column
        """
        type_validation = {}
        actual_types = {field.name: field.dataType.typeName() for field in df.schema.fields}
        
        for col, expected_type in expected_types.items():
            if col not in actual_types:
                raise ValueError(f"Column {col} not found in DataFrame")
                
            actual_type = actual_types[col].lower()
            is_valid = actual_type == expected_type.lower()
            type_validation[col] = {
                "is_valid": is_valid,
                "expected_type": expected_type.lower(),
                "actual_type": actual_type
            }
                
        return type_validation
    
    def detect_anomalies(self, df: DataFrame, numeric_columns: List[str], 
                        method: str = "zscore", threshold: float = 3.0) -> DataFrame:
        """
        Detect numerical anomalies using specified method.
        
        Args:
            df: Input DataFrame
            numeric_columns: List of numerical columns to check
            method: Detection method ("zscore" or "iqr")
            threshold: Threshold for anomaly detection (z-score or IQR multiplier)
            
        Returns:
            DataFrame with additional anomaly flag columns
        """
        result_df = df
        
        for col in numeric_columns:
            if col not in df.columns:
                raise ValueError(f"Column {col} not found in DataFrame")
                
            if method.lower() == "zscore":
                # Z-score method
                stats = df.select(
                    F.mean(col).alias('mean'),
                    F.stddev(col).alias('stddev')
                ).collect()[0]
                
                mean, stddev = stats['mean'], stats['stddev']
                
                if stddev is not None and stddev > 0:
                    result_df = result_df.withColumn(
                        f"{col}_anomaly",
                        F.abs((F.col(col) - mean) / stddev) > threshold
                    )
                else:
                    result_df = result_df.withColumn(
                        f"{col}_anomaly",
                        F.lit(False)
                    )
            elif method.lower() == "iqr":
                # IQR method
                quantiles = df.select(
                    F.expr(f"percentile_approx({col}, array(0.25, 0.75))").alias("quantiles")
                ).collect()[0]["quantiles"]
                
                q1, q3 = quantiles[0], quantiles[1]
                iqr = q3 - q1
                
                if iqr > 0:
                    lower_bound = q1 - threshold * iqr
                    upper_bound = q3 + threshold * iqr
                    result_df = result_df.withColumn(
                        f"{col}_anomaly",
                        (F.col(col) < lower_bound) | (F.col(col) > upper_bound)
                    )
                else:
                    result_df = result_df.withColumn(
                        f"{col}_anomaly",
                        F.lit(False)
                    )
            else:
                raise ValueError(f"Unsupported anomaly detection method: {method}")
                
        return result_df
    
    def calculate_quality_metrics(self, df: DataFrame, columns: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Calculate various quality metrics for specified columns.
        
        Args:
            df: Input DataFrame
            columns: List of columns to analyze
            
        Returns:
            Dictionary containing quality metrics for each column
        """
        metrics = {}
        
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Column {col} not found in DataFrame")
                
            col_metrics = {}
            
            # Basic statistics
            stats = df.select(
                F.count(col).alias('count'),
                F.countDistinct(col).alias('distinct_count'),
                F.mean(col).alias('mean'),
                F.stddev(col).alias('stddev')
            ).collect()[0]
            
            col_metrics.update({
                'count': stats['count'],
                'distinct_count': stats['distinct_count'],
                'uniqueness_ratio': stats['distinct_count'] / stats['count'] if stats['count'] > 0 else 0.0
            })
            
            # Add numerical statistics if applicable
            if isinstance(df.schema[col].dataType, (IntegerType, LongType, FloatType, DoubleType)):
                col_metrics.update({
                    'mean': stats['mean'],
                    'stddev': stats['stddev']
                })
            
            metrics[col] = col_metrics
            
        return metrics
    
    def generate_quality_report(self, df: DataFrame, config: Dict) -> Dict:
        """
        Generate a comprehensive quality report for the DataFrame.
        
        Args:
            df: Input DataFrame
            config: Configuration dictionary with validation rules
            
        Returns:
            Dictionary containing the complete quality report
        """
        report = {
            'completeness': self.validate_completeness(df, config.get('required_columns', [])),
            'data_types': self.validate_data_types(df, config.get('expected_types', {})),
            'metrics': self.calculate_quality_metrics(df, config.get('columns', []))
        }
        
        if config.get('numeric_columns'):
            report['anomalies'] = self.detect_anomalies(
                df, 
                config['numeric_columns'],
                config.get('anomaly_method', "zscore"),
                config.get('anomaly_threshold', 3.0)
            )
            
        return report 