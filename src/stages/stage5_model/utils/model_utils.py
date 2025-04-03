"""Utility functions for model training and evaluation.

This module provides helper functions for data preparation, model persistence,
and result visualization.
"""

from typing import Dict, List, Optional, Tuple, Union
import os
import json
from datetime import datetime

import numpy as np
import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from pyspark.ml import PipelineModel
from pyspark.sql import functions as F
from pyspark.sql.types import StructType


def prepare_train_test_split(
    df: DataFrame,
    test_size: float = 0.2,
    stratify_column: Optional[str] = None,
    random_seed: int = 42
) -> Tuple[DataFrame, DataFrame]:
    """Split data into training and test sets.

    Args:
        df: Input DataFrame
        test_size: Fraction of data to use for testing
        stratify_column: Column to use for stratified splitting
        random_seed: Random seed for reproducibility

    Returns:
        Tuple of (train_df, test_df)
    """
    if stratify_column:
        # Get class proportions
        class_counts = (
            df.groupBy(stratify_column)
            .count()
            .collect()
        )
        
        # Split each class separately
        train_dfs = []
        test_dfs = []
        
        for row in class_counts:
            class_value = row[stratify_column]
            class_df = df.filter(F.col(stratify_column) == class_value)
            class_train, class_test = class_df.randomSplit(
                [1 - test_size, test_size],
                seed=random_seed
            )
            train_dfs.append(class_train)
            test_dfs.append(class_test)
        
        # Combine splits
        train_df = train_dfs[0]
        test_df = test_dfs[0]
        
        for i in range(1, len(train_dfs)):
            train_df = train_df.union(train_dfs[i])
            test_df = test_df.union(test_dfs[i])
    else:
        train_df, test_df = df.randomSplit(
            [1 - test_size, test_size],
            seed=random_seed
        )
    
    return train_df, test_df


def validate_schema_compatibility(
    df: DataFrame,
    required_schema: StructType
) -> Tuple[bool, List[str]]:
    """Validate DataFrame schema against required schema.

    Args:
        df: DataFrame to validate
        required_schema: Required schema

    Returns:
        Tuple of (is_valid, list of incompatibilities)
    """
    current_schema = df.schema
    incompatibilities = []

    # Check each required field
    for required_field in required_schema.fields:
        field_name = required_field.name
        
        # Check if field exists
        if field_name not in df.columns:
            incompatibilities.append(
                f"Missing required column: {field_name}"
            )
            continue
        
        # Check field type
        current_field = current_schema[field_name]
        if current_field.dataType != required_field.dataType:
            incompatibilities.append(
                f"Type mismatch for {field_name}: "
                f"expected {required_field.dataType}, "
                f"got {current_field.dataType}"
            )
        
        # Check nullability
        if not required_field.nullable and current_field.nullable:
            incompatibilities.append(
                f"Column {field_name} must not be nullable"
            )

    return len(incompatibilities) == 0, incompatibilities


def save_model(
    model: PipelineModel,
    base_path: str,
    model_name: str,
    metadata: Optional[Dict] = None
) -> str:
    """Save trained model and metadata.

    Args:
        model: Trained model to save
        base_path: Base directory for model storage
        model_name: Name of the model
        metadata: Optional metadata dictionary

    Returns:
        Path to saved model
    """
    # Create timestamp-based version
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = os.path.join(base_path, f"{model_name}_{timestamp}")
    
    # Save model
    model.write().overwrite().save(model_path)
    
    # Save metadata if provided
    if metadata:
        metadata_path = f"{model_path}_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
    
    return model_path


def load_model(model_path: str) -> Tuple[PipelineModel, Optional[Dict]]:
    """Load saved model and metadata.

    Args:
        model_path: Path to saved model

    Returns:
        Tuple of (loaded model, metadata dictionary)
    """
    # Load model
    model = PipelineModel.load(model_path)
    
    # Try to load metadata
    metadata = None
    metadata_path = f"{model_path}_metadata.json"
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    
    return model, metadata


def analyze_predictions(
    predictions: DataFrame,
    label_col: str,
    prediction_col: str = "prediction",
    probability_col: Optional[str] = None
) -> Dict[str, Union[float, Dict]]:
    """Analyze model predictions.

    Args:
        predictions: DataFrame with predictions
        label_col: Name of label column
        prediction_col: Name of prediction column
        probability_col: Optional name of probability column

    Returns:
        Dictionary of prediction analysis results
    """
    analysis = {}
    
    # Basic statistics
    stats = predictions.select(
        F.mean(prediction_col).alias("mean"),
        F.stddev(prediction_col).alias("std"),
        F.min(prediction_col).alias("min"),
        F.max(prediction_col).alias("max")
    ).collect()[0]
    
    analysis["prediction_stats"] = {
        "mean": float(stats["mean"]),
        "std": float(stats["std"]),
        "min": float(stats["min"]),
        "max": float(stats["max"])
    }
    
    # Error analysis
    if predictions.schema[label_col].dataType.typeName() in ["double", "float"]:
        error_metrics = predictions.select(
            F.avg(F.abs(F.col(prediction_col) - F.col(label_col))).alias("mae"),
            F.avg(F.pow(F.col(prediction_col) - F.col(label_col), 2)).alias("mse")
        ).collect()[0]
        
        analysis["error_metrics"] = {
            "mae": float(error_metrics["mae"]),
            "mse": float(error_metrics["mse"]),
            "rmse": float(np.sqrt(error_metrics["mse"]))
        }
    
    # Classification specific analysis
    if probability_col:
        prob_stats = predictions.select(
            F.mean(probability_col).alias("mean_prob"),
            F.stddev(probability_col).alias("std_prob")
        ).collect()[0]
        
        analysis["probability_stats"] = {
            "mean": float(prob_stats["mean_prob"]),
            "std": float(prob_stats["std_prob"])
        }
        
        # Confusion matrix
        confusion_matrix = (
            predictions.groupBy(label_col, prediction_col)
            .count()
            .toPandas()
            .pivot(label_col, prediction_col, "count")
            .fillna(0)
        )
        
        analysis["confusion_matrix"] = confusion_matrix.to_dict()
    
    return analysis


def get_feature_correlations(
    df: DataFrame,
    feature_columns: List[str],
    method: str = "pearson"
) -> pd.DataFrame:
    """Calculate correlations between features.

    Args:
        df: Input DataFrame
        feature_columns: List of feature column names
        method: Correlation method ('pearson' or 'spearman')

    Returns:
        Pandas DataFrame with correlation matrix
    """
    # Convert to pandas for correlation calculation
    pdf = df.select(feature_columns).toPandas()
    
    # Calculate correlations
    if method == "spearman":
        corr_matrix = pdf.corr(method="spearman")
    else:
        corr_matrix = pdf.corr(method="pearson")
    
    return corr_matrix


def check_data_leakage(
    train_df: DataFrame,
    test_df: DataFrame,
    id_columns: List[str]
) -> Tuple[bool, List[Dict]]:
    """Check for potential data leakage between train and test sets.

    Args:
        train_df: Training DataFrame
        test_df: Test DataFrame
        id_columns: List of columns that should be unique

    Returns:
        Tuple of (has_leakage, list of overlapping records)
    """
    # Find overlapping records
    overlapping = (
        train_df.select(id_columns)
        .intersect(test_df.select(id_columns))
        .collect()
    )
    
    # Convert to list of dictionaries
    overlapping_records = [
        {col: row[col] for col in id_columns}
        for row in overlapping
    ]
    
    return len(overlapping_records) > 0, overlapping_records 