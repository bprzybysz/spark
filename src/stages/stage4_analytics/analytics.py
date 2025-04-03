"""
Main analytics module for Stage 4

This module provides the DataAnalyzer class for data aggregation and analysis.
"""

from typing import Dict, List, Optional, Union
from pyspark.sql import DataFrame, SparkSession
from .utils import (
    calculate_descriptive_stats,
    calculate_correlation_matrix,
    calculate_group_metrics,
    calculate_time_series_metrics,
    detect_outliers,
    validate_numeric_columns
)

class DataAnalyzer:
    """Class for data analysis and aggregation."""
    
    def __init__(self, spark: Optional[SparkSession] = None):
        """
        Initialize the DataAnalyzer.
        
        Args:
            spark: Optional SparkSession instance
        """
        self.spark = spark or SparkSession.builder \
            .appName("DataAnalyzer") \
            .master("local[*]") \
            .getOrCreate()
    
    def calculate_summary_statistics(self, df: DataFrame, columns: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Calculate summary statistics for specified columns.
        
        Args:
            df: Input DataFrame
            columns: List of columns to analyze
            
        Returns:
            Dictionary containing summary statistics for each column
        """
        if not validate_numeric_columns(df, columns):
            raise ValueError("All columns must be numeric")
            
        return {col: calculate_descriptive_stats(df, col) for col in columns}
    
    def calculate_correlations(self,
                             df: DataFrame,
                             columns: List[str],
                             method: str = 'pearson') -> Dict[str, Dict[str, float]]:
        """
        Calculate correlations between specified columns.
        
        Args:
            df: Input DataFrame
            columns: List of columns to analyze
            method: Correlation method ('pearson' or 'spearman')
            
        Returns:
            Dictionary containing correlation coefficients
        """
        if not validate_numeric_columns(df, columns):
            raise ValueError("All columns must be numeric")
            
        return calculate_correlation_matrix(df, columns, method)
    
    def calculate_group_statistics(self,
                                 df: DataFrame,
                                 group_columns: List[str],
                                 agg_columns: List[str],
                                 agg_functions: List[str]) -> DataFrame:
        """
        Calculate statistics for specified groups.
        
        Args:
            df: Input DataFrame
            group_columns: Columns to group by
            agg_columns: Columns to aggregate
            agg_functions: Aggregation functions to apply
            
        Returns:
            DataFrame with group statistics
        """
        if not validate_numeric_columns(df, agg_columns):
            raise ValueError("All aggregation columns must be numeric")
            
        return calculate_group_metrics(df, group_columns, agg_columns, agg_functions)
    
    def calculate_time_series_metrics(self,
                                    df: DataFrame,
                                    time_column: str,
                                    metric_columns: List[str],
                                    window_size: int) -> DataFrame:
        """
        Calculate time series metrics.
        
        Args:
            df: Input DataFrame
            time_column: Column containing timestamps
            metric_columns: Columns to analyze
            window_size: Size of the sliding window
            
        Returns:
            DataFrame with time series metrics
        """
        if not validate_numeric_columns(df, metric_columns):
            raise ValueError("All metric columns must be numeric")
            
        return calculate_time_series_metrics(df, time_column, metric_columns, window_size)
    
    def detect_outliers(self,
                       df: DataFrame,
                       columns: List[str],
                       method: str = 'iqr',
                       threshold: float = 1.5) -> DataFrame:
        """
        Detect outliers in specified columns.
        
        Args:
            df: Input DataFrame
            columns: Columns to analyze
            method: Detection method ('iqr' or 'zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            DataFrame with outlier flags
        """
        if not validate_numeric_columns(df, columns):
            raise ValueError("All columns must be numeric")
            
        result = df
        for column in columns:
            result = detect_outliers(result, column, method, threshold)
        return result
    
    def generate_analytics_report(self, df: DataFrame, config: Dict) -> Dict:
        """
        Generate a comprehensive analytics report.
        
        Args:
            df: Input DataFrame
            config: Configuration dictionary
            
        Returns:
            Dictionary containing analytics results
        """
        report = {}
        
        # Summary statistics
        if config['numeric_columns']:
            report['summary_statistics'] = self.calculate_summary_statistics(
                df,
                config['numeric_columns']
            )
        
        # Correlations
        if config['correlation_columns']:
            report['correlations'] = self.calculate_correlations(
                df,
                config['correlation_columns'],
                config['correlation_method']
            )
        
        # Group statistics
        if config['group_columns'] and config['agg_columns']:
            report['group_statistics'] = self.calculate_group_statistics(
                df,
                config['group_columns'],
                config['agg_columns'],
                config['agg_functions']
            )
        
        # Time series metrics
        if config['time_column'] and config['metric_columns']:
            report['time_series_metrics'] = self.calculate_time_series_metrics(
                df,
                config['time_column'],
                config['metric_columns'],
                config['window_size']
            )
        
        # Outliers
        if config['outlier_columns']:
            report['outliers'] = self.detect_outliers(
                df,
                config['outlier_columns'],
                config['outlier_method'],
                config['outlier_threshold']
            )
        
        return report 