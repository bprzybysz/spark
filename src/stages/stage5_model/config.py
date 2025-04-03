"""Configuration module for Stage 5 model training and evaluation.

This module defines configuration classes and validation for model training
and evaluation settings.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from enum import Enum, auto


class ModelType(Enum):
    """Supported model types."""
    CLASSIFICATION = auto()
    REGRESSION = auto()


class ModelAlgorithm(Enum):
    """Supported model algorithms."""
    # Classification
    LOGISTIC_REGRESSION = auto()
    RANDOM_FOREST_CLASSIFIER = auto()
    GBT_CLASSIFIER = auto()
    
    # Regression
    LINEAR_REGRESSION = auto()
    RANDOM_FOREST_REGRESSOR = auto()
    GBT_REGRESSOR = auto()


class EvaluationMetric(Enum):
    """Supported evaluation metrics."""
    # Classification
    ACCURACY = "accuracy"
    AUC = "areaUnderROC"
    F1 = "f1"
    PRECISION = "precision"
    RECALL = "recall"
    
    # Regression
    RMSE = "rmse"
    MAE = "mae"
    R2 = "r2"


@dataclass
class FeatureConfig:
    """Configuration for feature engineering."""
    categorical_columns: List[str]
    numerical_columns: List[str]
    text_columns: Optional[List[str]] = None
    date_columns: Optional[List[str]] = None
    id_columns: Optional[List[str]] = None
    
    # Feature engineering settings
    categorical_encoding: str = "one_hot"  # one_hot, label
    numerical_scaling: str = "standard"  # standard, minmax, robust
    text_vectorization: Optional[str] = None  # tfidf, count, word2vec
    date_encoding: Optional[str] = None  # cyclic, timestamp
    
    def validate(self) -> List[str]:
        """Validate feature configuration.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for empty column lists
        if not self.categorical_columns and not self.numerical_columns:
            errors.append("At least one feature column must be specified")
        
        # Validate encoding settings
        if self.categorical_encoding not in ["one_hot", "label"]:
            errors.append(
                f"Invalid categorical encoding: {self.categorical_encoding}"
            )
        
        if self.numerical_scaling not in ["standard", "minmax", "robust"]:
            errors.append(
                f"Invalid numerical scaling: {self.numerical_scaling}"
            )
        
        if self.text_columns and self.text_vectorization not in [
            None, "tfidf", "count", "word2vec"
        ]:
            errors.append(
                f"Invalid text vectorization: {self.text_vectorization}"
            )
        
        if self.date_columns and self.date_encoding not in [
            None, "cyclic", "timestamp"
        ]:
            errors.append(
                f"Invalid date encoding: {self.date_encoding}"
            )
        
        return errors


@dataclass
class TrainingConfig:
    """Configuration for model training."""
    model_type: ModelType
    model_algorithm: ModelAlgorithm
    feature_config: FeatureConfig
    label_column: str
    evaluation_metric: EvaluationMetric
    
    # Training settings
    test_size: float = 0.2
    validation_size: float = 0.2
    random_seed: int = 42
    stratify: bool = True
    
    # Hyperparameter tuning
    hyperparameters: Dict[str, List[Union[str, float, int]]] = field(
        default_factory=dict
    )
    cv_folds: int = 5
    
    def validate(self) -> List[str]:
        """Validate training configuration.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate feature config
        errors.extend(self.feature_config.validate())
        
        # Check model type and algorithm compatibility
        classification_algorithms = [
            ModelAlgorithm.LOGISTIC_REGRESSION,
            ModelAlgorithm.RANDOM_FOREST_CLASSIFIER,
            ModelAlgorithm.GBT_CLASSIFIER
        ]
        
        regression_algorithms = [
            ModelAlgorithm.LINEAR_REGRESSION,
            ModelAlgorithm.RANDOM_FOREST_REGRESSOR,
            ModelAlgorithm.GBT_REGRESSOR
        ]
        
        if (
            self.model_type == ModelType.CLASSIFICATION and
            self.model_algorithm not in classification_algorithms
        ):
            errors.append(
                f"Invalid algorithm {self.model_algorithm} "
                "for classification task"
            )
        
        if (
            self.model_type == ModelType.REGRESSION and
            self.model_algorithm not in regression_algorithms
        ):
            errors.append(
                f"Invalid algorithm {self.model_algorithm} "
                "for regression task"
            )
        
        # Check metric compatibility
        classification_metrics = [
            EvaluationMetric.ACCURACY,
            EvaluationMetric.AUC,
            EvaluationMetric.F1,
            EvaluationMetric.PRECISION,
            EvaluationMetric.RECALL
        ]
        
        regression_metrics = [
            EvaluationMetric.RMSE,
            EvaluationMetric.MAE,
            EvaluationMetric.R2
        ]
        
        if (
            self.model_type == ModelType.CLASSIFICATION and
            self.evaluation_metric not in classification_metrics
        ):
            errors.append(
                f"Invalid metric {self.evaluation_metric} "
                "for classification task"
            )
        
        if (
            self.model_type == ModelType.REGRESSION and
            self.evaluation_metric not in regression_metrics
        ):
            errors.append(
                f"Invalid metric {self.evaluation_metric} "
                "for regression task"
            )
        
        # Validate training parameters
        if not 0 < self.test_size < 1:
            errors.append(
                f"Invalid test size: {self.test_size}"
            )
        
        if not 0 < self.validation_size < 1:
            errors.append(
                f"Invalid validation size: {self.validation_size}"
            )
        
        if self.test_size + self.validation_size >= 1:
            errors.append(
                "Combined test and validation size must be less than 1"
            )
        
        if self.cv_folds < 2:
            errors.append(
                f"Invalid number of CV folds: {self.cv_folds}"
            )
        
        return errors


@dataclass
class EvaluationConfig:
    """Configuration for model evaluation."""
    model_type: ModelType
    metrics: List[EvaluationMetric]
    label_column: str
    prediction_column: str = "prediction"
    probability_column: Optional[str] = None
    threshold: float = 0.5  # For binary classification
    
    def validate(self) -> List[str]:
        """Validate evaluation configuration.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check metric compatibility
        classification_metrics = [
            EvaluationMetric.ACCURACY,
            EvaluationMetric.AUC,
            EvaluationMetric.F1,
            EvaluationMetric.PRECISION,
            EvaluationMetric.RECALL
        ]
        
        regression_metrics = [
            EvaluationMetric.RMSE,
            EvaluationMetric.MAE,
            EvaluationMetric.R2
        ]
        
        for metric in self.metrics:
            if (
                self.model_type == ModelType.CLASSIFICATION and
                metric not in classification_metrics
            ):
                errors.append(
                    f"Invalid metric {metric} for classification task"
                )
            
            if (
                self.model_type == ModelType.REGRESSION and
                metric not in regression_metrics
            ):
                errors.append(
                    f"Invalid metric {metric} for regression task"
                )
        
        # Validate threshold for classification
        if (
            self.model_type == ModelType.CLASSIFICATION and
            not 0 <= self.threshold <= 1
        ):
            errors.append(f"Invalid threshold: {self.threshold}")
        
        return errors 