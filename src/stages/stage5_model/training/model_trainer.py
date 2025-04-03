"""Model training functionality for Stage 5.

This module provides functionality for training ML models using PySpark ML,
including feature engineering, model selection, and hyperparameter tuning.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import os
import json

from pyspark.sql import DataFrame, SparkSession
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import (
    VectorAssembler,
    StandardScaler,
    StringIndexer,
    OneHotEncoder
)
from pyspark.ml.classification import (
    RandomForestClassifier,
    LogisticRegression,
    GBTClassifier
)
from pyspark.ml.regression import (
    RandomForestRegressor,
    LinearRegression,
    GBTRegressor
)
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator,
    RegressionEvaluator
)

from src.stages.stage5_model.config import (
    ModelType,
    ModelAlgorithm,
    TrainingConfig,
    EvaluationMetric
)


@dataclass
class ModelConfig:
    """Configuration for model training.

    Attributes:
        model_type: Type of model ('classification' or 'regression')
        feature_columns: List of feature column names
        label_column: Name of the label column
        categorical_columns: List of categorical column names
        numerical_columns: List of numerical column names
        model_algorithm: Algorithm to use (e.g., 'random_forest', 'gbt')
        hyperparameters: Dictionary of hyperparameter ranges for tuning
        evaluation_metric: Metric to use for model evaluation
        test_size: Fraction of data to use for testing
        random_seed: Random seed for reproducibility
    """
    model_type: str
    feature_columns: List[str]
    label_column: str
    categorical_columns: List[str]
    numerical_columns: List[str]
    model_algorithm: str
    hyperparameters: Dict[str, List[Union[int, float, bool]]]
    evaluation_metric: str
    test_size: float = 0.2
    random_seed: int = 42


class ModelTrainer:
    """Handles model training and hyperparameter tuning.

    Attributes:
        spark: SparkSession instance
        config: TrainingConfig instance with training configuration
    """

    def __init__(self, config: TrainingConfig):
        """Initialize ModelTrainer.

        Args:
            config: Training configuration

        Raises:
            ValueError: If configuration is invalid
        """
        self.spark = SparkSession.getActiveSession()
        if not self.spark:
            self.spark = SparkSession.builder.getOrCreate()
        self.config = config
        
        validation_errors = self._validate_config()
        if validation_errors:
            raise ValueError(f"Invalid configuration: {'; '.join(validation_errors)}")

    def _validate_config(self) -> List[str]:
        """Validate the model configuration.

        Returns:
            List of validation error messages. Empty list if configuration is valid.
        """
        errors = []
        
        if not isinstance(self.config.model_type, ModelType):
            errors.append(f"Invalid model_type. Must be a ModelType enum value")

        if not isinstance(self.config.model_algorithm, ModelAlgorithm):
            errors.append(f"Invalid model_algorithm. Must be a ModelAlgorithm enum value")

        # Validate feature configuration
        if not self.config.feature_config.categorical_columns and not self.config.feature_config.numerical_columns:
            errors.append("At least one feature column must be specified")

        valid_encodings = {"one_hot", "label"}
        if self.config.feature_config.categorical_encoding not in valid_encodings:
            errors.append(f"Invalid categorical_encoding. Must be one of {valid_encodings}")

        valid_scaling = {"standard", "minmax", None}
        if self.config.feature_config.numerical_scaling not in valid_scaling:
            errors.append(f"Invalid numerical_scaling. Must be one of {valid_scaling}")
            
        return errors

    def prepare_features(self) -> Pipeline:
        """Create a feature preparation pipeline.

        Returns:
            Pipeline for feature preparation
        """
        stages = []

        # Handle categorical features
        if self.config.feature_config.categorical_columns:
            for col in self.config.feature_config.categorical_columns:
                indexer = StringIndexer(
                    inputCol=col,
                    outputCol=f"{col}_idx",
                    handleInvalid="keep"
                )
                if self.config.feature_config.categorical_encoding == "one_hot":
                    encoder = OneHotEncoder(
                        inputCol=f"{col}_idx",
                        outputCol=f"{col}_onehot"
                    )
                    stages.extend([indexer, encoder])
                else:
                    stages.append(indexer)

        # Combine numerical features
        if self.config.feature_config.numerical_columns:
            numerical_assembler = VectorAssembler(
                inputCols=self.config.feature_config.numerical_columns,
                outputCol="numerical_features",
                handleInvalid="keep"
            )
            stages.append(numerical_assembler)

            if self.config.feature_config.numerical_scaling == "standard":
                scaler = StandardScaler(
                    inputCol="numerical_features",
                    outputCol="scaled_numerical_features",
                    withStd=True,
                    withMean=True
                )
                stages.append(scaler)

        # Combine all features
        feature_cols = []
        if self.config.feature_config.categorical_columns:
            if self.config.feature_config.categorical_encoding == "one_hot":
                feature_cols.extend([f"{col}_onehot" for col in self.config.feature_config.categorical_columns])
            else:
                feature_cols.extend([f"{col}_idx" for col in self.config.feature_config.categorical_columns])
        
        if self.config.feature_config.numerical_columns:
            if self.config.feature_config.numerical_scaling:
                feature_cols.append("scaled_numerical_features")
            else:
                feature_cols.append("numerical_features")

        final_assembler = VectorAssembler(
            inputCols=feature_cols,
            outputCol="features",
            handleInvalid="keep"
        )
        stages.append(final_assembler)

        return Pipeline(stages=stages)

    def create_model(self) -> Tuple[Pipeline, ParamGridBuilder]:
        """Create model pipeline and parameter grid.

        Returns:
            Tuple of (Pipeline, ParamGridBuilder)
        """
        feature_pipeline = self.prepare_features()
        model = self._get_model_instance()
        pipeline = Pipeline(stages=feature_pipeline.getStages() + [model])
        param_grid = self._create_param_grid(model)

        return pipeline, param_grid

    def _get_model_instance(self) -> Union[
        RandomForestClassifier,
        LogisticRegression,
        GBTClassifier,
        RandomForestRegressor,
        LinearRegression,
        GBTRegressor
    ]:
        """Get the appropriate model instance.

        Returns:
            Model instance based on configuration
        """
        model_map = {
            ModelType.CLASSIFICATION: {
                ModelAlgorithm.RANDOM_FOREST_CLASSIFIER: RandomForestClassifier(
                    labelCol=self.config.label_column,
                    featuresCol="features"
                ),
                ModelAlgorithm.LOGISTIC_REGRESSION: LogisticRegression(
                    labelCol=self.config.label_column,
                    featuresCol="features"
                ),
                ModelAlgorithm.GRADIENT_BOOSTED_CLASSIFIER: GBTClassifier(
                    labelCol=self.config.label_column,
                    featuresCol="features"
                )
            },
            ModelType.REGRESSION: {
                ModelAlgorithm.RANDOM_FOREST_REGRESSOR: RandomForestRegressor(
                    labelCol=self.config.label_column,
                    featuresCol="features"
                ),
                ModelAlgorithm.LINEAR_REGRESSION: LinearRegression(
                    labelCol=self.config.label_column,
                    featuresCol="features"
                ),
                ModelAlgorithm.GRADIENT_BOOSTED_REGRESSOR: GBTRegressor(
                    labelCol=self.config.label_column,
                    featuresCol="features"
                )
            }
        }

        return model_map[self.config.model_type][self.config.model_algorithm]

    def _create_param_grid(self, model: Any) -> ParamGridBuilder:
        """Create parameter grid for hyperparameter tuning.

        Args:
            model: Model instance to create parameter grid for

        Returns:
            ParamGridBuilder with hyperparameter grid
        """
        # Default hyperparameters for each model type
        default_params = {
            LogisticRegression: {
                "regParam": [0.0, 0.1],
                "elasticNetParam": [0.0, 0.5]
            },
            LinearRegression: {
                "regParam": [0.0, 0.1],
                "elasticNetParam": [0.0, 0.5]
            },
            RandomForestClassifier: {
                "maxDepth": [5, 10],
                "numTrees": [10, 20]
            },
            RandomForestRegressor: {
                "maxDepth": [5, 10],
                "numTrees": [10, 20]
            },
            GBTClassifier: {
                "maxDepth": [5, 10],
                "maxIter": [10, 20]
            },
            GBTRegressor: {
                "maxDepth": [5, 10],
                "maxIter": [10, 20]
            }
        }

        param_grid = ParamGridBuilder()
        
        # Use provided hyperparameters if any, otherwise use defaults
        hyperparameters = (
            self.config.hyperparameters if self.config.hyperparameters
            else default_params.get(type(model), {})
        )
        
        for param_name, param_values in hyperparameters.items():
            if hasattr(model, param_name):
                param = getattr(model, param_name)
                param_grid.addGrid(param, param_values)
        
        return param_grid

    def get_evaluator(self) -> Union[
        BinaryClassificationEvaluator,
        MulticlassClassificationEvaluator,
        RegressionEvaluator
    ]:
        """Get the appropriate model evaluator.

        Returns:
            Model evaluator based on configuration
        """
        if self.config.model_type == ModelType.CLASSIFICATION:
            if self.config.evaluation_metric == EvaluationMetric.AUC:
                return BinaryClassificationEvaluator(
                    labelCol=self.config.label_column,
                    metricName="areaUnderROC"
                )
            else:
                return MulticlassClassificationEvaluator(
                    labelCol=self.config.label_column,
                    metricName=self.config.evaluation_metric.value
                )
        else:
            return RegressionEvaluator(
                labelCol=self.config.label_column,
                metricName=self.config.evaluation_metric.value
            )

    def train_model(
        self,
        train_data: DataFrame,
        val_data: Optional[DataFrame] = None,
        num_folds: int = 3
    ) -> Tuple[PipelineModel, Dict[str, float]]:
        """Train model with cross-validation and hyperparameter tuning.

        Args:
            train_data: Training data
            val_data: Optional validation data
            num_folds: Number of cross-validation folds

        Returns:
            Tuple of (trained model, metrics dictionary)
        """
        # Drop rows with null labels
        train_data = train_data.dropna(subset=[self.config.label_column])
        if val_data is not None:
            val_data = val_data.dropna(subset=[self.config.label_column])

        # Ensure categorical columns have at least two distinct values
        for col in self.config.feature_config.categorical_columns:
            distinct_count = train_data.select(col).distinct().count()
            if distinct_count < 2:
                raise ValueError(f"Column {col} must have at least two distinct values")

        # Create pipeline and parameter grid
        pipeline, param_grid = self.create_model()
        evaluator = self.get_evaluator()

        # Create cross validator
        cv = CrossValidator(
            estimator=pipeline,
            estimatorParamMaps=param_grid.build(),
            evaluator=evaluator,
            numFolds=num_folds,
            parallelism=1,
            seed=self.config.random_seed
        )

        # Train model
        cv_model = cv.fit(train_data)

        # Get best model and metrics
        best_model = cv_model.bestModel
        cv_metrics = cv_model.avgMetrics
        best_params = cv_model.getEstimatorParamMaps()[cv_model.avgMetrics.index(max(cv_model.avgMetrics))]

        metrics = {
            "best_params": best_params,
            "cv_metrics": {
                f"fold_{i+1}": metric for i, metric in enumerate(cv_metrics)
            },
            "test_metrics": evaluator.evaluate(best_model.transform(train_data))
        }

        # Add validation metrics if validation data is provided
        if val_data is not None:
            metrics["validation_metric"] = evaluator.evaluate(best_model.transform(val_data))

        return best_model, metrics

    def save_model(self, model: PipelineModel, path: str, model_name: str, metrics: Optional[Dict] = None) -> str:
        """Save trained model to disk.

        Args:
            model: Trained model to save
            path: Path to save model to
            model_name: Name of the model
            metrics: Optional metrics to save with the model

        Returns:
            Path where model was saved
        """
        model_path = os.path.join(path, model_name)
        model.write().overwrite().save(model_path)

        if metrics:
            metrics_path = os.path.join(path, f"{model_name}_metrics.json")
            with open(metrics_path, "w") as f:
                json.dump(metrics, f)

        return model_path

    def load_model(self, path: str) -> PipelineModel:
        """Load trained model from disk.

        Args:
            path: Path to load model from

        Returns:
            Loaded model
        """
        return PipelineModel.load(path) 