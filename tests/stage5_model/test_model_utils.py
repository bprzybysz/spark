"""Tests for Stage 5 model utilities."""

import os
import tempfile
from datetime import datetime

import pytest
import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.ml.pipeline import Pipeline, PipelineModel
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import LogisticRegression

from src.stages.stage5_model.utils.model_utils import (
    prepare_train_test_split,
    validate_schema_compatibility,
    save_model,
    load_model,
    analyze_predictions,
    get_feature_correlations,
    check_data_leakage
)


@pytest.fixture(scope="module")
def spark():
    """Create a Spark session for testing."""
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("test_model_utils")
        .getOrCreate()
    )


@pytest.fixture(scope="module")
def sample_df(spark):
    """Create a sample DataFrame for testing."""
    data = [
        ("A", 1.0, 2.0, 0),
        ("B", 2.0, 3.0, 1),
        ("A", 3.0, 4.0, 0),
        ("B", 4.0, 5.0, 1),
        ("A", 5.0, 6.0, 0),
        ("B", 6.0, 7.0, 1)
    ]
    schema = StructType([
        StructField("category", StringType(), False),
        StructField("feature1", DoubleType(), False),
        StructField("feature2", DoubleType(), False),
        StructField("label", DoubleType(), False)
    ])
    return spark.createDataFrame(data, schema)


@pytest.fixture(scope="module")
def sample_pipeline():
    """Create a sample pipeline for testing."""
    indexer = StringIndexer(
        inputCol="category",
        outputCol="category_idx"
    )
    assembler = VectorAssembler(
        inputCols=["category_idx", "feature1", "feature2"],
        outputCol="features"
    )
    lr = LogisticRegression(
        featuresCol="features",
        labelCol="label"
    )
    return Pipeline(stages=[indexer, assembler, lr])


def test_prepare_train_test_split(sample_df):
    """Test train-test split preparation."""
    # Basic split
    train_df, test_df = prepare_train_test_split(
        sample_df,
        test_size=0.3,
        random_seed=42
    )
    
    assert train_df.count() + test_df.count() == sample_df.count()
    assert abs(test_df.count() / sample_df.count() - 0.3) < 0.2
    
    # Stratified split
    train_df, test_df = prepare_train_test_split(
        sample_df,
        test_size=0.3,
        stratify_column="category",
        random_seed=42
    )
    
    train_props = (
        train_df.groupBy("category")
        .count()
        .toPandas()
        .set_index("category")["count"]
        .to_dict()
    )
    
    test_props = (
        test_df.groupBy("category")
        .count()
        .toPandas()
        .set_index("category")["count"]
        .to_dict()
    )
    
    # Check proportions are roughly maintained
    for category in train_props:
        train_prop = train_props[category] / train_df.count()
        test_prop = test_props[category] / test_df.count()
        assert abs(train_prop - test_prop) < 0.2


def test_validate_schema_compatibility(sample_df):
    """Test schema validation."""
    # Valid schema
    required_schema = StructType([
        StructField("category", StringType(), False),
        StructField("feature1", DoubleType(), False)
    ])
    
    is_valid, errors = validate_schema_compatibility(
        sample_df,
        required_schema
    )
    assert is_valid
    assert not errors
    
    # Invalid schema
    required_schema = StructType([
        StructField("category", StringType(), True),
        StructField("missing_col", DoubleType(), False)
    ])
    
    is_valid, errors = validate_schema_compatibility(
        sample_df,
        required_schema
    )
    assert not is_valid
    assert len(errors) == 1
    assert "Missing required column" in errors[0]


def test_save_load_model(sample_df, sample_pipeline, tmp_path):
    """Test model saving and loading."""
    # Train and save model
    model = sample_pipeline.fit(sample_df)
    metadata = {
        "training_date": datetime.now().isoformat(),
        "metrics": {"accuracy": 0.95}
    }
    
    model_path = save_model(
        model,
        str(tmp_path),
        "test_model",
        metadata
    )
    
    assert os.path.exists(model_path)
    assert os.path.exists(f"{model_path}_metadata.json")
    
    # Load model and verify
    loaded_model, loaded_metadata = load_model(model_path)
    assert isinstance(loaded_model, PipelineModel)
    assert loaded_metadata == metadata


def test_analyze_predictions(sample_df, sample_pipeline):
    """Test prediction analysis."""
    # Generate predictions
    model = sample_pipeline.fit(sample_df)
    predictions = model.transform(sample_df)
    
    # Basic analysis
    analysis = analyze_predictions(
        predictions,
        label_col="label",
        prediction_col="prediction",
        probability_col="probability"
    )
    
    assert "prediction_stats" in analysis
    assert "error_metrics" in analysis
    assert "probability_stats" in analysis
    assert "confusion_matrix" in analysis
    
    stats = analysis["prediction_stats"]
    assert all(k in stats for k in ["mean", "std", "min", "max"])
    assert all(isinstance(v, float) for v in stats.values())


def test_get_feature_correlations(sample_df):
    """Test feature correlation calculation."""
    corr_matrix = get_feature_correlations(
        sample_df,
        feature_columns=["feature1", "feature2"]
    )
    
    assert isinstance(corr_matrix, pd.DataFrame)
    assert corr_matrix.shape == (2, 2)
    assert abs(corr_matrix.loc["feature1", "feature2"]) <= 1.0


def test_check_data_leakage(sample_df):
    """Test data leakage detection."""
    # Split data
    train_df, test_df = prepare_train_test_split(
        sample_df,
        test_size=0.3,
        random_seed=42
    )
    
    # Check for leakage
    has_leakage, overlapping = check_data_leakage(
        train_df,
        test_df,
        id_columns=["category", "feature1"]
    )
    
    assert isinstance(has_leakage, bool)
    assert isinstance(overlapping, list)
    assert all(isinstance(r, dict) for r in overlapping) 