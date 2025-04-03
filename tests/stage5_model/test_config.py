"""Tests for Stage 5 configuration module."""

import pytest
from src.stages.stage5_model.config import (
    ModelType,
    ModelAlgorithm,
    EvaluationMetric,
    FeatureConfig,
    TrainingConfig,
    EvaluationConfig
)


def test_feature_config_validation():
    """Test feature configuration validation."""
    # Valid configuration
    config = FeatureConfig(
        categorical_columns=["cat1", "cat2"],
        numerical_columns=["num1", "num2"],
        text_columns=["text1"],
        date_columns=["date1"],
        categorical_encoding="one_hot",
        numerical_scaling="standard",
        text_vectorization="tfidf",
        date_encoding="cyclic"
    )
    assert not config.validate()
    
    # Invalid - no features
    config = FeatureConfig(
        categorical_columns=[],
        numerical_columns=[],
        categorical_encoding="one_hot",
        numerical_scaling="standard"
    )
    errors = config.validate()
    assert len(errors) == 1
    assert "At least one feature column must be specified" in errors[0]
    
    # Invalid encodings
    config = FeatureConfig(
        categorical_columns=["cat1"],
        numerical_columns=["num1"],
        text_columns=["text1"],
        date_columns=["date1"],
        categorical_encoding="invalid",
        numerical_scaling="invalid",
        text_vectorization="invalid",
        date_encoding="invalid"
    )
    errors = config.validate()
    assert len(errors) == 4
    assert any("Invalid categorical encoding" in e for e in errors)
    assert any("Invalid numerical scaling" in e for e in errors)
    assert any("Invalid text vectorization" in e for e in errors)
    assert any("Invalid date encoding" in e for e in errors)


def test_training_config_validation():
    """Test training configuration validation."""
    # Valid configuration
    feature_config = FeatureConfig(
        categorical_columns=["cat1"],
        numerical_columns=["num1"]
    )
    
    config = TrainingConfig(
        model_type=ModelType.CLASSIFICATION,
        model_algorithm=ModelAlgorithm.LOGISTIC_REGRESSION,
        feature_config=feature_config,
        label_column="label",
        evaluation_metric=EvaluationMetric.ACCURACY,
        test_size=0.2,
        validation_size=0.2,
        cv_folds=5
    )
    assert not config.validate()
    
    # Invalid model type and algorithm combination
    config = TrainingConfig(
        model_type=ModelType.CLASSIFICATION,
        model_algorithm=ModelAlgorithm.LINEAR_REGRESSION,
        feature_config=feature_config,
        label_column="label",
        evaluation_metric=EvaluationMetric.ACCURACY
    )
    errors = config.validate()
    assert len(errors) == 1
    assert "Invalid algorithm" in errors[0]
    
    # Invalid metric for model type
    config = TrainingConfig(
        model_type=ModelType.CLASSIFICATION,
        model_algorithm=ModelAlgorithm.LOGISTIC_REGRESSION,
        feature_config=feature_config,
        label_column="label",
        evaluation_metric=EvaluationMetric.RMSE
    )
    errors = config.validate()
    assert len(errors) == 1
    assert "Invalid metric" in errors[0]
    
    # Invalid training parameters
    config = TrainingConfig(
        model_type=ModelType.CLASSIFICATION,
        model_algorithm=ModelAlgorithm.LOGISTIC_REGRESSION,
        feature_config=feature_config,
        label_column="label",
        evaluation_metric=EvaluationMetric.ACCURACY,
        test_size=0.5,
        validation_size=0.5,
        cv_folds=1
    )
    errors = config.validate()
    assert len(errors) == 2
    assert any("Combined test and validation size" in e for e in errors)
    assert any("Invalid number of CV folds" in e for e in errors)


def test_evaluation_config_validation():
    """Test evaluation configuration validation."""
    # Valid configuration
    config = EvaluationConfig(
        model_type=ModelType.CLASSIFICATION,
        metrics=[
            EvaluationMetric.ACCURACY,
            EvaluationMetric.F1_SCORE
        ],
        label_column="label",
        threshold=0.5
    )
    assert not config.validate()
    
    # Invalid metrics for model type
    config = EvaluationConfig(
        model_type=ModelType.CLASSIFICATION,
        metrics=[
            EvaluationMetric.RMSE,
            EvaluationMetric.MAE
        ],
        label_column="label"
    )
    errors = config.validate()
    assert len(errors) == 2
    assert all("Invalid metric" in e for e in errors)
    
    # Invalid threshold
    config = EvaluationConfig(
        model_type=ModelType.CLASSIFICATION,
        metrics=[EvaluationMetric.ACCURACY],
        label_column="label",
        threshold=1.5
    )
    errors = config.validate()
    assert len(errors) == 1
    assert "Invalid threshold" in errors[0]


def test_model_type_compatibility():
    """Test model type compatibility with algorithms and metrics."""
    # Classification models
    assert ModelAlgorithm.LOGISTIC_REGRESSION in [
        ModelAlgorithm.LOGISTIC_REGRESSION,
        ModelAlgorithm.RANDOM_FOREST_CLASSIFIER,
        ModelAlgorithm.GRADIENT_BOOSTED_CLASSIFIER
    ]
    
    # Regression models
    assert ModelAlgorithm.LINEAR_REGRESSION in [
        ModelAlgorithm.LINEAR_REGRESSION,
        ModelAlgorithm.RANDOM_FOREST_REGRESSOR,
        ModelAlgorithm.GRADIENT_BOOSTED_REGRESSOR
    ]
    
    # Classification metrics
    assert EvaluationMetric.ACCURACY in [
        EvaluationMetric.ACCURACY,
        EvaluationMetric.PRECISION,
        EvaluationMetric.RECALL,
        EvaluationMetric.F1_SCORE,
        EvaluationMetric.ROC_AUC
    ]
    
    # Regression metrics
    assert EvaluationMetric.RMSE in [
        EvaluationMetric.MSE,
        EvaluationMetric.RMSE,
        EvaluationMetric.MAE,
        EvaluationMetric.R2,
        EvaluationMetric.EXPLAINED_VARIANCE
    ] 