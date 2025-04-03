"""
Utility functions for data quality checks in Stage 3.

This module provides helper functions for common data quality operations.
"""

from typing import Dict, List, Optional, Tuple, Union
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *

def calculate_column_statistics(df: DataFrame, column_name: str) -> Dict[str, Optional[float]]:
    """Calculate basic statistics for a numeric column."""
    df.createOrReplaceTempView("data_table")
    stats = df.sparkSession.sql(f"""
        SELECT 
            COUNT(*) as count,
            COUNT(CASE WHEN {column_name} IS NULL THEN 1 END) as null_count,
            AVG({column_name}) as mean,
            STDDEV({column_name}) as stddev,
            MIN({column_name}) as min,
            MAX({column_name}) as max
        FROM data_table
    """).collect()[0]

    return {
        "count": stats["count"],
        "null_count": stats["null_count"],
        "mean": float(stats["mean"]) if stats["mean"] is not None else None,
        "stddev": float(stats["stddev"]) if stats["stddev"] is not None else None,
        "min": float(stats["min"]) if stats["min"] is not None else None,
        "max": float(stats["max"]) if stats["max"] is not None else None
    }

def detect_data_patterns(df: DataFrame, column_name: str) -> Dict[str, Union[float, int]]:
    """Detect patterns in the data for a given column."""
    total_count = df.count()
    null_count = df.filter(F.col(column_name).isNull()).count()
    null_percentage = (null_count / total_count) * 100 if total_count > 0 else 0

    # Count unique non-null values
    unique_count = df.filter(F.col(column_name).isNotNull()).select(column_name).distinct().count()

    patterns = {
        "null_percentage": null_percentage,
        "unique_values": unique_count
    }

    # Get column type
    col_type = df.schema[column_name].dataType

    if isinstance(col_type, StringType):
        # String pattern analysis
        avg_length = df.select(
            F.avg(F.length(F.col(column_name)))
        ).collect()[0][0]
        patterns["avg_length"] = float(avg_length) if avg_length is not None else 0.0
    elif isinstance(col_type, (IntegerType, LongType, FloatType, DoubleType)):
        # Numeric pattern analysis
        negative_count = df.filter(
            (F.col(column_name).isNotNull()) & (F.col(column_name) < 0)
        ).count()
        patterns["negative_values"] = negative_count

    return patterns

def check_value_distribution(df: DataFrame, column_name: str) -> Dict[str, List]:
    """Analyze the distribution of values in a numeric column."""
    non_null_df = df.filter(F.col(column_name).isNotNull())
    
    if non_null_df.count() == 0:
        return {
            "percentiles": [],
            "histogram": []
        }

    # Calculate min and max for bin calculation
    stats = non_null_df.agg(
        F.min(column_name).alias("min"),
        F.max(column_name).alias("max")
    ).collect()[0]

    min_val = float(stats["min"])
    max_val = float(stats["max"])
    bin_width = (max_val - min_val) / 10 if max_val > min_val else 1.0

    # Calculate histogram using window function
    histogram = non_null_df.groupBy(
        F.floor((F.col(column_name).cast("double") - min_val) / bin_width).alias("bin")
    ).agg(
        F.count("*").alias("count")
    ).collect()

    histogram_data = [(float(row["bin"] * bin_width + min_val), int(row["count"])) for row in histogram]

    # Calculate percentiles
    percentiles = non_null_df.select(
        F.percentile_approx(column_name, [0.25, 0.5, 0.75]).alias("percentiles")
    ).collect()[0]["percentiles"]

    return {
        "percentiles": percentiles,
        "histogram": histogram_data
    }

def validate_value_ranges(df: DataFrame, column: str, 
                        min_value: Optional[float] = None,
                        max_value: Optional[float] = None) -> Dict[str, int]:
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
    null_count = df.filter(F.col(column).isNull()).count()
    below_min = df.filter(F.col(column) < min_value).count() if min_value is not None else 0
    above_max = df.filter(F.col(column) > max_value).count() if max_value is not None else 0
    within_range = df.filter(
        (F.col(column).isNotNull()) &
        (F.col(column) >= min_value if min_value is not None else F.lit(True)) &
        (F.col(column) <= max_value if max_value is not None else F.lit(True))
    ).count()
    
    return {
        'below_min': below_min,
        'above_max': above_max,
        'within_range': within_range,
        'null_values': null_count
    }

def check_referential_integrity(df1: DataFrame, df2: DataFrame,
                              key: str) -> Dict[str, int]:
    """
    Check referential integrity between two DataFrames.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        key: Key column in both DataFrames
        
    Returns:
        Dictionary containing integrity check results
    """
    # Get distinct keys from both DataFrames
    keys1 = set(row[0] for row in df1.select(key).distinct().collect())
    keys2 = set(row[0] for row in df2.select(key).distinct().collect())
    
    # Calculate metrics
    matching_keys = len(keys1.intersection(keys2))
    missing_in_first = len(keys2 - keys1)
    missing_in_second = len(keys1 - keys2)
    
    return {
        'matching_keys': matching_keys,
        'missing_in_first': missing_in_first,
        'missing_in_second': missing_in_second
    } 