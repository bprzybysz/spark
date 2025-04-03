"""
Utility module for Stage 4 Analytics

This module provides helper functions for data analytics operations.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pyspark.sql.functions as F
from pyspark.sql import DataFrame, Window
from pyspark.sql.types import NumericType
from pyspark.ml.stat import Correlation
from pyspark.ml.feature import VectorAssembler

def calculate_descriptive_stats(df: DataFrame, column: str) -> Dict[str, float]:
    """
    Calculate descriptive statistics for a numeric column.
    
    Args:
        df: Input DataFrame
        column: Column name to analyze
        
    Returns:
        Dictionary containing descriptive statistics
    """
    stats = df.select(
        F.mean(column).alias('mean'),
        F.stddev(column).alias('stddev'),
        F.min(column).alias('min'),
        F.max(column).alias('max'),
        F.expr(f'percentile_approx({column}, 0.25)').alias('q1'),
        F.expr(f'percentile_approx({column}, 0.5)').alias('median'),
        F.expr(f'percentile_approx({column}, 0.75)').alias('q3'),
        F.skewness(column).alias('skewness'),
        F.kurtosis(column).alias('kurtosis')
    ).collect()[0].asDict()
    
    return {k: float(v) if v is not None else None for k, v in stats.items()}

def calculate_correlation_matrix(df: DataFrame, 
                              columns: List[str], 
                              method: str = 'pearson') -> Dict[Tuple[str, str], float]:
    """
    Calculate correlation matrix for specified numeric columns.
    
    Args:
        df: Input DataFrame
        columns: List of column names to analyze
        method: Correlation method ('pearson' or 'spearman')
        
    Returns:
        Dictionary with column pairs as keys and correlation coefficients as values
    """
    if df.rdd.isEmpty():
        # Return None for all correlations if DataFrame is empty
        correlations = {}
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                correlations[(col1, col2)] = None
        return correlations
    
    assembler = VectorAssembler(
        inputCols=columns,
        outputCol='features'
    )
    
    vector_df = assembler.transform(df.select(columns))
    correlation_matrix = Correlation.corr(vector_df, 'features', method).collect()[0][0].toArray()
    
    correlations = {}
    for i, col1 in enumerate(columns):
        for j, col2 in enumerate(columns):
            correlations[(col1, col2)] = float(correlation_matrix[i][j])
    
    return correlations

def calculate_group_metrics(df: DataFrame,
                          group_cols: List[str],
                          agg_cols: List[str],
                          agg_funcs: List[str]) -> DataFrame:
    """
    Calculate aggregated metrics for specified groups.
    
    Args:
        df: Input DataFrame
        group_cols: Columns to group by
        agg_cols: Columns to aggregate
        agg_funcs: Aggregation functions to apply
        
    Returns:
        DataFrame with aggregated metrics
    """
    agg_exprs = []
    for col in agg_cols:
        for func in agg_funcs:
            if func == 'count':
                agg_exprs.append(F.count(col).alias(f'{col}_{func}'))
            elif func == 'sum':
                agg_exprs.append(F.sum(col).alias(f'{col}_{func}'))
            elif func == 'avg':
                agg_exprs.append(F.avg(col).alias(f'{col}_{func}'))
            elif func == 'min':
                agg_exprs.append(F.min(col).alias(f'{col}_{func}'))
            elif func == 'max':
                agg_exprs.append(F.max(col).alias(f'{col}_{func}'))
            elif func == 'stddev':
                agg_exprs.append(F.stddev(col).alias(f'{col}_{func}'))
    
    return df.groupBy(group_cols).agg(*agg_exprs)

def calculate_time_series_metrics(df: DataFrame,
                                time_col: str,
                                metric_cols: List[str],
                                window_size: int) -> DataFrame:
    """
    Calculate time series metrics using sliding windows.
    
    Args:
        df: Input DataFrame
        time_col: Column containing timestamps
        metric_cols: Columns to analyze
        window_size: Size of the sliding window
        
    Returns:
        DataFrame with time series metrics
    """
    window_spec = Window.orderBy(time_col).rowsBetween(-window_size + 1, 0)
    
    metric_exprs = []
    for col in metric_cols:
        metric_exprs.extend([
            F.avg(col).over(window_spec).alias(f'{col}_rolling_avg'),
            F.stddev(col).over(window_spec).alias(f'{col}_rolling_stddev'),
            F.min(col).over(window_spec).alias(f'{col}_rolling_min'),
            F.max(col).over(window_spec).alias(f'{col}_rolling_max')
        ])
    
    return df.select(time_col, *metric_cols, *metric_exprs)

def detect_outliers(df: DataFrame,
                   column: str,
                   method: str = 'iqr',
                   threshold: float = 1.5) -> DataFrame:
    """
    Detect outliers in a numeric column.
    
    Args:
        df: Input DataFrame
        column: Column to analyze
        method: Detection method ('iqr' or 'zscore')
        threshold: Threshold for outlier detection
        
    Returns:
        DataFrame with outlier flags
    """
    if method == 'iqr':
        stats = df.select(
            F.expr(f'percentile_approx({column}, 0.25)').alias('q1'),
            F.expr(f'percentile_approx({column}, 0.75)').alias('q3')
        ).collect()[0]
        
        q1, q3 = stats['q1'], stats['q3']
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        
        return df.withColumn(
            f'{column}_is_outlier',
            (F.col(column) < lower_bound) | (F.col(column) > upper_bound)
        )
    
    elif method == 'zscore':
        stats = df.select(
            F.mean(column).alias('mean'),
            F.stddev(column).alias('stddev')
        ).collect()[0]
        
        mean, stddev = stats['mean'], stats['stddev']
        
        return df.withColumn(
            f'{column}_is_outlier',
            F.abs((F.col(column) - mean) / stddev) > threshold
        )
    
    else:
        raise ValueError(f"Invalid outlier detection method: {method}")

def validate_numeric_columns(df: DataFrame, columns: List[str]) -> bool:
    """
    Validate that specified columns are numeric.
    
    Args:
        df: Input DataFrame
        columns: List of column names to validate
        
    Returns:
        True if all columns are numeric, False otherwise
    """
    for column in columns:
        if column not in df.columns:
            return False
        if not isinstance(df.schema[column].dataType, NumericType):
            return False
    return True 