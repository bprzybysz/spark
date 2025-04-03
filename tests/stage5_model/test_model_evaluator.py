"""Tests for Stage 5 model evaluator."""

import pytest
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.ml.pipeline import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.regression import LinearRegression

from src.stages.stage5_model.config import (
    ModelType,
    EvaluationMetric,
    EvaluationConfig
)
from src.stages.stage5_model.evaluation.model_evaluator import (
    ModelEvaluator
)


@pytest.fixture(scope="module")
def spark():
    """Create a Spark session for testing."""
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("test_model_evaluator")
        .getOrCreate()
    )


@pytest.fixture(scope="module")
def sample_classification_df(spark):
    """Create a sample classification DataFrame for testing."""
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
def sample_regression_df(spark):
    """Create a sample regression DataFrame for testing."""
    data = [
        ("A", 1.0, 2.1),
        ("B", 2.0, 4.2),
        ("A", 3.0, 6.3),
        ("B", 4.0, 8.4),
        ("A", 5.0, 10.5),
        ("B", 6.0, 12.6)
    ]
    schema = StructType([
        StructField("category", StringType(), False),
        StructField("feature", DoubleType(), False),
        StructField("label", DoubleType(), False)
    ])
    return spark.createDataFrame(data, schema)


@pytest.fixture(scope="module")
def classification_predictions(sample_classification_df):
    """Create classification predictions for testing."""
    # Prepare features
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
    pipeline = Pipeline(stages=[indexer, assembler, lr])
    
    # Generate predictions
    model = pipeline.fit(sample_classification_df)
    return model.transform(sample_classification_df)


@pytest.fixture(scope="module")
def regression_predictions(sample_regression_df):
    """Create regression predictions for testing."""
    # Prepare features
    indexer = StringIndexer(
        inputCol="category",
        outputCol="category_idx"
    )
    assembler = VectorAssembler(
        inputCols=["category_idx", "feature"],
        outputCol="features"
    )
    lr = LinearRegression(
        featuresCol="features",
        labelCol="label"
    )
    pipeline = Pipeline(stages=[indexer, assembler, lr])
    
    # Generate predictions
    model = pipeline.fit(sample_regression_df)
    return model.transform(sample_regression_df)


def test_classification_evaluation():
    """Test classification model evaluation."""
    config = EvaluationConfig(
        model_type=ModelType.CLASSIFICATION,
        metrics=[
            EvaluationMetric.ACCURACY,
            EvaluationMetric.PRECISION,
            EvaluationMetric.RECALL,
            EvaluationMetric.F1_SCORE
        ],
        label_column="label",
        prediction_column="prediction",
        probability_column="probability",
        threshold=0.5
    )
    
    evaluator = ModelEvaluator(config)
    assert not evaluator._validate_config()


def test_regression_evaluation():
    """Test regression model evaluation."""
    config = EvaluationConfig(
        model_type=ModelType.REGRESSION,
        metrics=[
            EvaluationMetric.MSE,
            EvaluationMetric.RMSE,
            EvaluationMetric.MAE,
            EvaluationMetric.R2
        ],
        label_column="label",
        prediction_column="prediction"
    )
    
    evaluator = ModelEvaluator(config)
    assert not evaluator._validate_config()


def test_evaluate_classification_model(classification_predictions):
    """Test classification model evaluation metrics."""
    config = EvaluationConfig(
        model_type=ModelType.CLASSIFICATION,
        metrics=[
            EvaluationMetric.ACCURACY,
            EvaluationMetric.PRECISION,
            EvaluationMetric.RECALL,
            EvaluationMetric.F1_SCORE
        ],
        label_column="label",
        prediction_column="prediction",
        probability_column="probability"
    )
    
    evaluator = ModelEvaluator(config)
    metrics = evaluator.evaluate_model(classification_predictions)
    
    assert isinstance(metrics, dict)
    assert all(
        metric.name.lower() in metrics
        for metric in config.metrics
    )
    assert all(
        isinstance(value, float)
        for value in metrics.values()
    )
    assert all(
        0 <= value <= 1
        for value in metrics.values()
    )


def test_evaluate_regression_model(regression_predictions):
    """Test regression model evaluation metrics."""
    config = EvaluationConfig(
        model_type=ModelType.REGRESSION,
        metrics=[
            EvaluationMetric.MSE,
            EvaluationMetric.RMSE,
            EvaluationMetric.MAE,
            EvaluationMetric.R2
        ],
        label_column="label",
        prediction_column="prediction"
    )
    
    evaluator = ModelEvaluator(config)
    metrics = evaluator.evaluate_model(regression_predictions)
    
    assert isinstance(metrics, dict)
    assert all(
        metric.name.lower() in metrics
        for metric in config.metrics
    )
    assert all(
        isinstance(value, float)
        for value in metrics.values()
    )
    assert metrics["r2"] <= 1.0


def test_get_feature_importance(classification_predictions):
    """Test feature importance extraction."""
    config = EvaluationConfig(
        model_type=ModelType.CLASSIFICATION,
        metrics=[EvaluationMetric.ACCURACY],
        label_column="label"
    )
    
    evaluator = ModelEvaluator(config)
    importance = evaluator.get_feature_importance(
        classification_predictions,
        ["category", "feature1", "feature2"]
    )
    
    assert isinstance(importance, dict)
    assert all(
        feature in importance
        for feature in ["category", "feature1", "feature2"]
    )
    assert all(
        isinstance(value, float)
        for value in importance.values()
    )


def test_generate_predictions_summary(classification_predictions):
    """Test predictions summary generation."""
    config = EvaluationConfig(
        model_type=ModelType.CLASSIFICATION,
        metrics=[EvaluationMetric.ACCURACY],
        label_column="label"
    )
    
    evaluator = ModelEvaluator(config)
    summary = evaluator.generate_predictions_summary(
        classification_predictions
    )
    
    assert isinstance(summary, dict)
    assert "prediction_stats" in summary
    assert "class_distribution" in summary
    assert "confusion_matrix" in summary


def test_cross_validate(sample_classification_df, classification_predictions):
    """Test cross-validation metrics."""
    config = EvaluationConfig(
        model_type=ModelType.CLASSIFICATION,
        metrics=[
            EvaluationMetric.ACCURACY,
            EvaluationMetric.F1_SCORE
        ],
        label_column="label"
    )
    
    evaluator = ModelEvaluator(config)
    cv_metrics = evaluator.cross_validate(
        sample_classification_df,
        classification_predictions,
        n_folds=3
    )
    
    assert isinstance(cv_metrics, dict)
    assert all(
        f"{metric.name.lower()}_mean" in cv_metrics
        for metric in config.metrics
    )
    assert all(
        f"{metric.name.lower()}_std" in cv_metrics
        for metric in config.metrics
    )


def test_invalid_config():
    """Test evaluator with invalid configuration."""
    # Invalid metrics for model type
    config = EvaluationConfig(
        model_type=ModelType.CLASSIFICATION,
        metrics=[
            EvaluationMetric.RMSE,
            EvaluationMetric.MAE
        ],
        label_column="label"
    )
    
    evaluator = ModelEvaluator(config)
    errors = evaluator._validate_config()
    assert len(errors) > 0
    
    # Invalid threshold
    config = EvaluationConfig(
        model_type=ModelType.CLASSIFICATION,
        metrics=[EvaluationMetric.ACCURACY],
        label_column="label",
        threshold=1.5
    )
    
    evaluator = ModelEvaluator(config)
    errors = evaluator._validate_config()
    assert len(errors) > 0 