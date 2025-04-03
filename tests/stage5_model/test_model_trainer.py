"""Tests for Stage 5 model trainer."""

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.ml.evaluation import BinaryClassificationEvaluator

from src.stages.stage5_model.config import (
    ModelType,
    ModelAlgorithm,
    EvaluationMetric,
    FeatureConfig,
    TrainingConfig
)
from src.stages.stage5_model.training.model_trainer import (
    ModelTrainer
)


@pytest.fixture(scope="module")
def spark():
    """Create a Spark session for testing."""
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("test_model_trainer")
        .getOrCreate()
    )


@pytest.fixture(scope="module")
def sample_df(spark):
    """Create a sample DataFrame for testing."""
    data = [
        ("A", 1.0, 2.0, 0.0),
        ("B", 2.0, 3.0, 1.0),
        ("A", 3.0, 4.0, 0.0),
        ("B", 4.0, 5.0, 1.0),
        ("A", 5.0, 6.0, 0.0),
        ("B", 6.0, 7.0, 1.0)
    ]
    schema = StructType([
        StructField("category", StringType(), False),
        StructField("feature1", DoubleType(), False),
        StructField("feature2", DoubleType(), False),
        StructField("label", DoubleType(), False)
    ])
    return spark.createDataFrame(data, schema)


@pytest.fixture(scope="module")
def feature_config():
    """Create a sample feature configuration."""
    return FeatureConfig(
        categorical_columns=["category"],
        numerical_columns=["feature1", "feature2"],
        categorical_encoding="one_hot",
        numerical_scaling="standard"
    )


@pytest.fixture(scope="module")
def training_config(feature_config):
    """Create a sample training configuration."""
    return TrainingConfig(
        model_type=ModelType.CLASSIFICATION,
        model_algorithm=ModelAlgorithm.LOGISTIC_REGRESSION,
        feature_config=feature_config,
        label_column="label",
        evaluation_metric=EvaluationMetric.ACCURACY,
        test_size=0.2,
        validation_size=0.2,
        hyperparameters={
            "regParam": [0.0, 0.1],
            "elasticNetParam": [0.0, 0.5]
        }
    )


def test_model_trainer_initialization(training_config):
    """Test model trainer initialization."""
    # Test successful initialization
    trainer = ModelTrainer(training_config)
    assert trainer.config == training_config
    assert trainer._validate_config() == []  # No validation errors
    
    # Test invalid configuration
    invalid_config = TrainingConfig(
        model_type=ModelType.CLASSIFICATION,
        model_algorithm=ModelAlgorithm.LOGISTIC_REGRESSION,
        feature_config=FeatureConfig(
            categorical_columns=[],
            numerical_columns=[],
            categorical_encoding="invalid"
        ),
        label_column="label",
        evaluation_metric=EvaluationMetric.ACCURACY
    )
    
    with pytest.raises(ValueError) as exc_info:
        ModelTrainer(invalid_config)
    assert "Invalid configuration" in str(exc_info.value)
    assert "Invalid categorical_encoding" in str(exc_info.value)


def test_prepare_features(sample_df, training_config):
    """Test feature preparation pipeline."""
    trainer = ModelTrainer(training_config)
    pipeline = trainer.prepare_features()
    
    # Transform data
    transformed_df = pipeline.fit(sample_df).transform(sample_df)
    
    # Check transformed columns
    expected_cols = {
        "category",  # Original
        "feature1",  # Original
        "feature2",  # Original
        "label",     # Original
        "category_idx",  # Indexed
        "category_onehot",  # One-hot encoded
        "numerical_features",  # Scaled
        "features"  # Assembled
    }
    assert all(col in transformed_df.columns for col in expected_cols)


def test_prepare_features_with_nulls(spark, training_config):
    """Test feature preparation pipeline with null values."""
    # Create sample data with nulls
    data = [
        ("A", 1.0, None, 0.0),
        ("B", None, 3.0, 1.0),
        (None, 3.0, 4.0, 0.0),
        ("B", 4.0, 5.0, 1.0)
    ]
    schema = StructType([
        StructField("category", StringType(), True),
        StructField("feature1", DoubleType(), True),
        StructField("feature2", DoubleType(), True),
        StructField("label", DoubleType(), False)
    ])
    df_with_nulls = spark.createDataFrame(data, schema)
    
    trainer = ModelTrainer(training_config)
    pipeline = trainer.prepare_features()
    
    # Transform data
    transformed_df = pipeline.fit(df_with_nulls).transform(df_with_nulls)
    
    # Check that transformation completed without errors
    assert transformed_df.count() == len(data)
    
    # Check that features column exists and contains vectors
    features_col = transformed_df.select("features").collect()
    assert all(row.features is not None for row in features_col)
    
    # Verify handling of null values in numerical features
    if training_config.feature_config.numerical_scaling:
        scaled_features = transformed_df.select("numerical_features").collect()
        assert all(row.numerical_features is not None for row in scaled_features)
    
    # Verify handling of null values in categorical features
    if training_config.feature_config.categorical_encoding == "one_hot":
        onehot_cols = [c for c in transformed_df.columns if c.endswith("_onehot")]
        assert len(onehot_cols) > 0
        for col in onehot_cols:
            assert all(row[col] is not None for row in transformed_df.select(col).collect())


def test_create_model(sample_df, training_config):
    """Test model creation and parameter grid."""
    trainer = ModelTrainer(training_config)
    pipeline, param_grid = trainer.create_model()
    
    # Check pipeline stages
    stages = pipeline.getStages()
    assert len(stages) > 0
    
    # Check parameter grid
    param_maps = param_grid.build()
    assert len(param_maps) > 0
    assert any("regParam" in str(param_map) for param_map in param_maps)


def test_get_evaluator(training_config):
    """Test evaluator retrieval."""
    trainer = ModelTrainer(training_config)
    evaluator = trainer.get_evaluator()
    
    assert isinstance(evaluator, BinaryClassificationEvaluator)
    assert evaluator.getLabelCol() == "label"
    assert evaluator.getRawPredictionCol() == "rawPrediction"


def test_train_model(sample_df, training_config):
    """Test model training."""
    trainer = ModelTrainer(training_config)
    model, metrics = trainer.train_model(sample_df)
    
    # Check model
    assert model is not None
    assert hasattr(model, "transform")
    
    # Check metrics
    assert isinstance(metrics, dict)
    assert "best_params" in metrics
    assert "cv_metrics" in metrics
    assert "test_metrics" in metrics


def test_train_model_with_validation(sample_df, training_config):
    """Test model training with validation data."""
    # Create larger sample to ensure enough distinct values
    data = []
    for i in range(3):  # Triplicate the data
        for row in sample_df.collect():
            data.append(row)
    
    larger_df = sample_df.sparkSession.createDataFrame(data, sample_df.schema)
    
    # Split data into train and validation sets
    train_df, val_df = larger_df.randomSplit([0.7, 0.3], seed=42)
    
    trainer = ModelTrainer(training_config)
    model, metrics = trainer.train_model(train_df, val_data=val_df, num_folds=2)
    
    # Check model
    assert model is not None
    assert hasattr(model, "transform")
    
    # Check metrics
    assert isinstance(metrics, dict)
    assert "best_params" in metrics
    assert "cv_metrics" in metrics
    assert "validation_metric" in metrics
    assert isinstance(metrics["cv_metrics"], dict)
    # CrossValidator returns metrics for all parameter combinations
    num_param_combinations = len(trainer.config.hyperparameters["regParam"]) * len(trainer.config.hyperparameters["elasticNetParam"])
    assert len(metrics["cv_metrics"]) == num_param_combinations
    
    # Verify validation predictions
    val_predictions = model.transform(val_df)
    assert val_predictions.count() == val_df.count()
    assert "prediction" in val_predictions.columns
    
    # Test with invalid validation data
    invalid_val_df = val_df.drop(training_config.label_column)
    with pytest.raises(Exception):
        trainer.train_model(train_df, val_data=invalid_val_df)


def test_model_trainer_with_regression(sample_df, feature_config):
    """Test model trainer with regression task."""
    config = TrainingConfig(
        model_type=ModelType.REGRESSION,
        model_algorithm=ModelAlgorithm.RANDOM_FOREST_REGRESSOR,
        feature_config=feature_config,
        label_column="feature2",  # Using feature2 as target
        evaluation_metric=EvaluationMetric.RMSE,
        hyperparameters={
            "maxDepth": [5, 10],
            "numTrees": [10, 20]
        }
    )
    
    trainer = ModelTrainer(config)
    model, metrics = trainer.train_model(sample_df)
    
    assert model is not None
    assert "rmse" in metrics["test_metrics"]


def test_invalid_config():
    """Test model trainer with invalid configuration."""
    # Invalid feature config with no columns but valid encoding
    feature_config = FeatureConfig(
        categorical_columns=[],
        numerical_columns=[],
        categorical_encoding="label"  # Valid encoding
    )

    config = TrainingConfig(
        model_type=ModelType.CLASSIFICATION,
        model_algorithm=ModelAlgorithm.LOGISTIC_REGRESSION,
        feature_config=feature_config,
        label_column="label",
        evaluation_metric=EvaluationMetric.ACCURACY
    )

    with pytest.raises(ValueError) as exc_info:
        trainer = ModelTrainer(config)
    
    assert "At least one feature column must be specified" in str(exc_info.value)


def test_model_persistence(sample_df, training_config, tmp_path):
    """Test model saving and loading."""
    trainer = ModelTrainer(training_config)
    model, metrics = trainer.train_model(sample_df)
    
    # Save model
    model_path = trainer.save_model(
        model,
        str(tmp_path),
        "test_model",
        metrics
    )
    
    # Load model
    loaded_model = trainer.load_model(model_path)
    
    assert loaded_model is not None
    
    # Test predictions
    original_preds = model.transform(sample_df)
    loaded_preds = loaded_model.transform(sample_df)
    
    # Compare predictions
    assert (
        original_preds.select("prediction")
        .collect() ==
        loaded_preds.select("prediction")
        .collect()
    )


def test_different_evaluation_metrics(sample_df, feature_config):
    """Test model training with different evaluation metrics."""
    # Test classification metrics
    for metric in [EvaluationMetric.ACCURACY, EvaluationMetric.F1]:  # Removed AUC for now
        config = TrainingConfig(
            model_type=ModelType.CLASSIFICATION,
            model_algorithm=ModelAlgorithm.RANDOM_FOREST_CLASSIFIER,
            feature_config=feature_config,
            label_column="label",
            evaluation_metric=metric,
            hyperparameters={"maxDepth": [5], "numTrees": [10]}
        )
        trainer = ModelTrainer(config)
        model, metrics = trainer.train_model(sample_df)
        assert model is not None
        assert metrics["test_metrics"] is not None
        
    # Test AUC separately with binary classification
    config = TrainingConfig(
        model_type=ModelType.CLASSIFICATION,
        model_algorithm=ModelAlgorithm.LOGISTIC_REGRESSION,
        feature_config=feature_config,
        label_column="label",
        evaluation_metric=EvaluationMetric.AUC,
        hyperparameters={"regParam": [0.0], "elasticNetParam": [0.0]}
    )
    trainer = ModelTrainer(config)
    model, metrics = trainer.train_model(sample_df)
    assert model is not None
    assert metrics["test_metrics"] is not None
        
    # Test regression metrics
    regression_config = feature_config
    for metric in [EvaluationMetric.RMSE, EvaluationMetric.MAE, EvaluationMetric.R2]:
        config = TrainingConfig(
            model_type=ModelType.REGRESSION,
            model_algorithm=ModelAlgorithm.RANDOM_FOREST_REGRESSOR,
            feature_config=regression_config,
            label_column="feature1",  # Using feature1 as target for regression
            evaluation_metric=metric,
            hyperparameters={"maxDepth": [5], "numTrees": [10]}
        )
        trainer = ModelTrainer(config)
        model, metrics = trainer.train_model(sample_df)
        assert model is not None
        assert metrics["test_metrics"] is not None


def test_cross_validation(sample_df, training_config):
    """Test model training with different cross-validation settings."""
    trainer = ModelTrainer(training_config)

    # Test with different number of folds
    for num_folds in [2, 3, 5]:
        model, metrics = trainer.train_model(sample_df, num_folds=num_folds)
        assert model is not None
        assert isinstance(metrics["cv_metrics"], dict)
        # CrossValidator returns metrics for all parameter combinations
        num_param_combinations = len(trainer.config.hyperparameters["regParam"]) * len(trainer.config.hyperparameters["elasticNetParam"])
        assert len(metrics["cv_metrics"]) == num_param_combinations


def test_handle_missing_labels(spark, feature_config):
    """Test model training with missing labels."""
    # Create sample data with missing labels
    data = [
        ("A", 1.0, 2.0, None),
        ("B", 2.0, 3.0, 1.0),
        ("A", 3.0, 4.0, 0.0),
        ("B", 4.0, 5.0, None),
        ("A", 5.0, 6.0, 0.0),
        ("B", 6.0, 7.0, 1.0)
    ]
    schema = StructType([
        StructField("category", StringType(), False),
        StructField("feature1", DoubleType(), False),
        StructField("feature2", DoubleType(), False),
        StructField("label", DoubleType(), True)  # Nullable
    ])
    df_with_nulls = spark.createDataFrame(data, schema)
    
    config = TrainingConfig(
        model_type=ModelType.CLASSIFICATION,
        model_algorithm=ModelAlgorithm.RANDOM_FOREST_CLASSIFIER,
        feature_config=feature_config,
        label_column="label",
        evaluation_metric=EvaluationMetric.ACCURACY,
        hyperparameters={"maxDepth": [5], "numTrees": [10]}
    )
    
    trainer = ModelTrainer(config)
    
    # Training should succeed with rows having non-null labels
    model, metrics = trainer.train_model(df_with_nulls)
    assert model is not None
    
    # Transform should work on data with missing labels
    predictions = model.transform(df_with_nulls)
    assert predictions.count() == len(data)
    assert all(row.prediction is not None for row in predictions.select("prediction").collect()) 