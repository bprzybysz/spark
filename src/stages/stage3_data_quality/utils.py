"""
Utility functions for data quality checks in Stage 3.

This module provides helper functions for common data quality operations.
"""

from typing import Dict, List, Optional, Tuple, Union
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *

def calculate_column_statistics(df: DataFrame, column: str) -> Dict[str, float]:
    """
    Calculate basic statistics for a column.
    
    Args:
        df: Input DataFrame
        column: Column name to analyze
        
    Returns:
        Dictionary containing basic statistics
    """
    stats = df.select(
        F.count(column).alias('count'),
        F.countDistinct(column).alias('distinct'),
        F.mean(column).alias('mean'),
        F.stddev(column).alias('stddev'),
        F.min(column).alias('min'),
        F.max(column).alias('max')
    ).collect()[0]
    
    return {
        'count': stats['count'],
        'distinct_count': stats['distinct'],
        'mean': stats['mean'],
        'stddev': stats['stddev'],
        'min': stats['min'],
        'max': stats['max']
    }

def detect_data_patterns(df: DataFrame, column: str) -> Dict[str, Union[str, float]]:
    """
    Detect common patterns in column data.
    
    Args:
        df: Input DataFrame
        column: Column name to analyze
        
    Returns:
        Dictionary containing pattern information
    """
    patterns = {}
    
    # Get column type
    col_type = df.schema[column].dataType
    
    if isinstance(col_type, StringType):
        # String pattern analysis
        patterns['avg_length'] = df.select(F.avg(F.length(F.col(column)))).collect()[0][0]
        patterns['max_length'] = df.select(F.max(F.length(F.col(column)))).collect()[0][0]
        patterns['contains_numbers'] = df.filter(F.col(column).rlike('\\d')).count() > 0
        patterns['contains_special'] = df.filter(F.col(column).rlike('[^a-zA-Z0-9\\s]')).count() > 0
    elif isinstance(col_type, (IntegerType, LongType, FloatType, DoubleType)):
        # Numeric pattern analysis
        patterns['is_continuous'] = df.select(F.countDistinct(column)).collect()[0][0] > 10
        patterns['has_negatives'] = df.filter(F.col(column) < 0).count() > 0
        patterns['has_decimals'] = isinstance(col_type, (FloatType, DoubleType))
    
    return patterns

def check_value_distribution(df: DataFrame, column: str, num_bins: int = 10) -> Dict[str, float]:
    """
    Analyze value distribution in a column.
    
    Args:
        df: Input DataFrame
        column: Column name to analyze
        num_bins: Number of bins for histogram (for numeric data)
        
    Returns:
        Dictionary containing distribution metrics
    """
    distribution = {}
    
    # Calculate frequency distribution
    value_counts = df.filter(F.col(column).isNotNull()).groupBy(column).count().orderBy('count', ascending=False)
    
    # Get top values
    top_values = value_counts.limit(5).collect()
    distribution['top_values'] = [(row[column], row['count']) for row in top_values]
    
    # Calculate distribution metrics
    total_count = df.count()
    non_null_count = df.filter(F.col(column).isNotNull()).count()
    
    distribution['null_ratio'] = (total_count - non_null_count) / total_count if total_count > 0 else 0
    distribution['unique_ratio'] = df.select(F.countDistinct(column)).collect()[0][0] / total_count if total_count > 0 else 0
    
    # If all values are null, clear top_values
    if non_null_count == 0:
        distribution['top_values'] = []
    
    return distribution

def validate_value_ranges(df: DataFrame, column: str, 
                        min_value: Optional[float] = None,
                        max_value: Optional[float] = None) -> Dict[str, Union[bool, int]]:
    """
    Validate if values in a column fall within specified ranges.
    
    Args:
        df: Input DataFrame
        column: Column name to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Dictionary containing validation results
    """
    validation = {'is_valid': True, 'violations': 0}
    
    if min_value is not None:
        violations = df.filter(F.col(column) < min_value).count()
        validation['violations'] += violations
        validation['is_valid'] &= violations == 0
        
    if max_value is not None:
        violations = df.filter(F.col(column) > max_value).count()
        validation['violations'] += violations
        validation['is_valid'] &= violations == 0
        
    return validation

def check_referential_integrity(df1: DataFrame, df2: DataFrame,
                              key1: str, key2: str) -> Dict[str, Union[bool, int]]:
    """
    Check referential integrity between two DataFrames.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        key1: Key column in first DataFrame
        key2: Key column in second DataFrame
        
    Returns:
        Dictionary containing integrity check results
    """
    integrity = {}
    
    # Get distinct keys from both DataFrames
    keys1 = set(row[0] for row in df1.select(key1).distinct().collect())
    keys2 = set(row[0] for row in df2.select(key2).distinct().collect())
    
    # Check for orphaned records
    orphaned_keys = keys1 - keys2
    integrity['orphaned_records'] = len(orphaned_keys)
    
    # Check for missing references
    missing_keys = keys2 - keys1
    integrity['missing_references'] = len(missing_keys)
    
    # Overall integrity status
    integrity['is_valid'] = len(orphaned_keys) == 0 and len(missing_keys) == 0
    
    return integrity 