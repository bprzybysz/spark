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
    # Validate columns exist
    all_cols = set(df.columns)
    missing_cols = set(group_cols + agg_cols) - all_cols
    if missing_cols:
        raise ValueError(f"Columns not found in DataFrame: {missing_cols}")
    
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
    
    return df.groupBy(group_cols).agg(*agg_exprs) if not df.rdd.isEmpty() else df.select()

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

def calculate_moving_average(df: DataFrame,
                           column: str,
                           window_size: int) -> DataFrame:
    """
    Calculate moving average for a numeric column.
    
    Args:
        df: Input DataFrame
        column: Column to analyze
        window_size: Size of the moving average window
        
    Returns:
        DataFrame with moving average column
    """
    if window_size <= 0:
        raise ValueError("Window size must be positive")
        
    window_spec = Window.orderBy(F.monotonically_increasing_id()).rowsBetween(-window_size + 1, 0)
    return df.withColumn(f'{column}_ma', F.avg(column).over(window_spec))

def detect_seasonality(df: DataFrame,
                      time_col: str,
                      value_col: str,
                      period: int) -> Dict[str, float]:
    """
    Detect seasonality in time series data.
    
    Args:
        df: Input DataFrame
        time_col: Column containing timestamps
        value_col: Column containing values to analyze
        period: Expected seasonality period
        
    Returns:
        Dictionary containing seasonality metrics
    """
    if df.rdd.isEmpty():
        return {
            'period': period,
            'seasonality_score': 0.0,
            'is_seasonal': False
        }
    
    # Calculate autocorrelation at the specified period
    lagged_df = df.withColumn(
        'lagged_value',
        F.lag(F.col(value_col), period).over(Window.orderBy(time_col))
    )
    
    corr = lagged_df.select(
        F.corr(value_col, 'lagged_value').alias('autocorrelation')
    ).collect()[0]['autocorrelation']
    
    seasonality_score = abs(corr) if corr is not None else 0.0
    
    return {
        'period': period,
        'seasonality_score': seasonality_score,
        'is_seasonal': seasonality_score > 0.7
    }

def identify_trends(df: DataFrame,
                   value_col: str,
                   time_col: str,
                   window_size: int = 7) -> DataFrame:
    """
    Identify trends in time series data.
    
    Args:
        df: Input DataFrame
        value_col: Column containing values to analyze
        time_col: Column containing timestamps
        window_size: Window size for trend calculation
        
    Returns:
        DataFrame with trend indicators
    """
    window_spec = Window.orderBy(time_col).rowsBetween(-window_size + 1, 0)
    
    return df.withColumn(
        'trend_direction',
        F.when(
            F.col(value_col) > F.lag(value_col, 1).over(Window.orderBy(time_col)),
            'increasing'
        ).when(
            F.col(value_col) < F.lag(value_col, 1).over(Window.orderBy(time_col)),
            'decreasing'
        ).otherwise('stable')
    ).withColumn(
        'slope',
        (F.col(value_col) - F.lag(value_col, window_size).over(Window.orderBy(time_col))) / window_size
    )

def analyze_distribution(df: DataFrame,
                        column: str,
                        bins: int = 10) -> Dict[str, float]:
    """
    Analyze the distribution of a numeric column.
    
    Args:
        df: Input DataFrame
        column: Column to analyze
        bins: Number of bins for histogram
        
    Returns:
        Dictionary containing distribution metrics
    """
    if df.rdd.isEmpty():
        return {
            'mean': None,
            'median': None,
            'stddev': None,
            'skewness': None,
            'kurtosis': None
        }
    
    stats = df.select(
        F.mean(column).alias('mean'),
        F.expr(f'percentile_approx({column}, 0.5)').alias('median'),
        F.stddev(column).alias('stddev'),
        F.skewness(column).alias('skewness'),
        F.kurtosis(column).alias('kurtosis')
    ).collect()[0]
    
    return {
        'mean': float(stats['mean']) if stats['mean'] is not None else None,
        'median': float(stats['median']) if stats['median'] is not None else None,
        'stddev': float(stats['stddev']) if stats['stddev'] is not None else None,
        'skewness': float(stats['skewness']) if stats['skewness'] is not None else None,
        'kurtosis': float(stats['kurtosis']) if stats['kurtosis'] is not None else None
    }

def calculate_percentiles(df: DataFrame,
                         column: str,
                         percentiles: List[float]) -> Dict[float, float]:
    """
    Calculate percentiles for a numeric column.
    
    Args:
        df: Input DataFrame
        column: Column to analyze
        percentiles: List of percentiles to calculate (between 0 and 100)
        
    Returns:
        Dictionary mapping percentiles to their values
    """
    if not all(0 <= p <= 100 for p in percentiles):
        raise ValueError("Percentiles must be between 0 and 100")
    
    # Convert percentiles to fractions
    fractions = [p/100.0 for p in percentiles]
    expr = [F.expr(f'percentile_approx({column}, {f})').alias(f'p{int(f*100)}') 
            for f in fractions]
    
    result = df.select(*expr).collect()[0]
    return {p: float(result[f'p{int((p/100)*100)}']) for p in percentiles} 