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
        
    def validate_completeness(self, df: DataFrame, required_columns: List[str]) -> Dict[str, float]:
        """
        Check completeness of required columns.
        
        Args:
            df: Input DataFrame
            required_columns: List of columns that should be complete
            
        Returns:
            Dictionary with completeness ratios for each column
        """
        completeness = {}
        total_rows = df.count()
        
        for col in required_columns:
            non_null_count = df.filter(F.col(col).isNotNull()).count()
            completeness[col] = non_null_count / total_rows if total_rows > 0 else 0.0
            
        return completeness
    
    def validate_data_types(self, df: DataFrame, expected_types: Dict[str, str]) -> Dict[str, bool]:
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
            if col in actual_types:
                type_validation[col] = actual_types[col].lower() == expected_type.lower()
            else:
                type_validation[col] = False
                
        return type_validation
    
    def detect_anomalies(self, df: DataFrame, numeric_columns: List[str], 
                        threshold: float = 3.0) -> Dict[str, List[float]]:
        """
        Detect numerical anomalies using z-score method.
        
        Args:
            df: Input DataFrame
            numeric_columns: List of numerical columns to check
            threshold: Z-score threshold for anomaly detection
            
        Returns:
            Dictionary with anomaly counts and boundaries for each column
        """
        anomalies = {}
        
        for col in numeric_columns:
            stats = df.select(
                F.mean(col).alias('mean'),
                F.stddev(col).alias('stddev')
            ).collect()[0]
            
            mean, stddev = stats['mean'], stats['stddev']
            
            if stddev is not None and stddev > 0:
                lower_bound = mean - threshold * stddev
                upper_bound = mean + threshold * stddev
                
                anomaly_count = df.filter(
                    (F.col(col) < lower_bound) | (F.col(col) > upper_bound)
                ).count()
                
                anomalies[col] = {
                    'anomaly_count': anomaly_count,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound
                }
                
        return anomalies
    
    def calculate_quality_metrics(self, df: DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Calculate various quality metrics for the DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary containing quality metrics for each column
        """
        metrics = {}
        
        for col in df.columns:
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
            'type_validation': self.validate_data_types(df, config.get('expected_types', {})),
            'metrics': self.calculate_quality_metrics(df)
        }
        
        if config.get('numeric_columns'):
            report['anomalies'] = self.detect_anomalies(
                df, 
                config['numeric_columns'],
                config.get('anomaly_threshold', 3.0)
            )
            
        return report 