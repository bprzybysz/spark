"""Model evaluation functionality for Stage 5.

This module provides functionality for evaluating ML models, including
performance metrics calculation, model validation, and results visualization.
"""

from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

import numpy as np
from pyspark.sql import DataFrame
from pyspark.ml import PipelineModel
from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator,
    RegressionEvaluator
)
from pyspark.mllib.evaluation import (
    BinaryClassificationMetrics,
    MulticlassMetrics,
    RegressionMetrics
)
from pyspark.sql import functions as F


@dataclass
class EvaluationConfig:
    """Configuration for model evaluation.

    Attributes:
        model_type: Type of model ('classification' or 'regression')
        label_column: Name of the label column
        prediction_column: Name of the prediction column
        metrics: List of metrics to compute
        threshold: Classification threshold for binary problems
    """
    model_type: str
    label_column: str
    prediction_column: str = "prediction"
    metrics: Optional[List[str]] = None
    threshold: float = 0.5


class ModelEvaluator:
    """Handles model evaluation and validation.

    Attributes:
        config: EvaluationConfig instance
    """

    def __init__(self, config: EvaluationConfig):
        """Initialize ModelEvaluator.

        Args:
            config: Evaluation configuration
        """
        self.config = config
        self._validate_config()
        self._set_default_metrics()

    def _validate_config(self) -> None:
        """Validate the evaluation configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        valid_model_types = {"classification", "regression"}
        if self.config.model_type not in valid_model_types:
            raise ValueError(f"Invalid model_type. Must be one of {valid_model_types}")

        if self.config.threshold <= 0 or self.config.threshold >= 1:
            raise ValueError("Threshold must be between 0 and 1")

    def _set_default_metrics(self) -> None:
        """Set default metrics based on model type."""
        if not self.config.metrics:
            if self.config.model_type == "classification":
                self.config.metrics = [
                    "accuracy",
                    "precision",
                    "recall",
                    "f1",
                    "areaUnderROC",
                    "areaUnderPR"
                ]
            else:
                self.config.metrics = [
                    "rmse",
                    "mse",
                    "mae",
                    "r2",
                    "explained_variance"
                ]

    def evaluate_model(
        self,
        model: PipelineModel,
        test_data: DataFrame
    ) -> Dict[str, float]:
        """Evaluate model performance on test data.

        Args:
            model: Trained model
            test_data: Test DataFrame

        Returns:
            Dictionary of evaluation metrics
        """
        predictions = model.transform(test_data)
        
        if self.config.model_type == "classification":
            return self._evaluate_classification(predictions)
        return self._evaluate_regression(predictions)

    def _evaluate_classification(self, predictions: DataFrame) -> Dict[str, float]:
        """Evaluate classification model.

        Args:
            predictions: DataFrame with predictions

        Returns:
            Dictionary of classification metrics
        """
        metrics = {}
        
        # Binary metrics
        if len(predictions.select(self.config.label_column).distinct().collect()) == 2:
            binary_evaluator = BinaryClassificationEvaluator(
                labelCol=self.config.label_column,
                rawPredictionCol="rawPrediction"
            )
            
            for metric in ["areaUnderROC", "areaUnderPR"]:
                if metric in self.config.metrics:
                    binary_evaluator.setMetricName(metric)
                    metrics[metric] = binary_evaluator.evaluate(predictions)

            # Calculate confusion matrix based metrics
            predictions_and_labels = predictions.select(
                F.col(self.config.prediction_column).cast("double"),
                F.col(self.config.label_column).cast("double")
            )
            binary_metrics = BinaryClassificationMetrics(
                predictions_and_labels.rdd.map(tuple)
            )
            
            if "precision" in self.config.metrics:
                metrics["precision"] = binary_metrics.precisionByThreshold().filter(
                    lambda x: abs(x[0] - self.config.threshold) < 1e-6
                ).first()[1]
            
            if "recall" in self.config.metrics:
                metrics["recall"] = binary_metrics.recallByThreshold().filter(
                    lambda x: abs(x[0] - self.config.threshold) < 1e-6
                ).first()[1]
            
            if "f1" in self.config.metrics:
                metrics["f1"] = binary_metrics.fMeasureByThreshold().filter(
                    lambda x: abs(x[0] - self.config.threshold) < 1e-6
                ).first()[1]

        # Multiclass metrics
        multiclass_evaluator = MulticlassClassificationEvaluator(
            labelCol=self.config.label_column,
            predictionCol=self.config.prediction_column
        )
        
        for metric in ["accuracy", "weightedPrecision", "weightedRecall", "f1"]:
            if metric in self.config.metrics:
                multiclass_evaluator.setMetricName(metric)
                metrics[metric] = multiclass_evaluator.evaluate(predictions)

        return metrics

    def _evaluate_regression(self, predictions: DataFrame) -> Dict[str, float]:
        """Evaluate regression model.

        Args:
            predictions: DataFrame with predictions

        Returns:
            Dictionary of regression metrics
        """
        metrics = {}
        evaluator = RegressionEvaluator(
            labelCol=self.config.label_column,
            predictionCol=self.config.prediction_column
        )

        metric_mapping = {
            "rmse": "rmse",
            "mse": "mse",
            "mae": "mae",
            "r2": "r2",
            "explained_variance": "var"
        }

        for metric, spark_metric in metric_mapping.items():
            if metric in self.config.metrics:
                evaluator.setMetricName(spark_metric)
                metrics[metric] = evaluator.evaluate(predictions)

        return metrics

    def get_feature_importance(
        self,
        model: PipelineModel,
        feature_names: List[str]
    ) -> Dict[str, float]:
        """Get feature importance scores.

        Args:
            model: Trained model
            feature_names: List of feature names

        Returns:
            Dictionary mapping feature names to importance scores
        """
        # Get the last stage (actual model)
        final_stage = model.stages[-1]
        
        if hasattr(final_stage, "featureImportances"):
            importances = final_stage.featureImportances.toArray()
            return dict(zip(feature_names, importances))
        
        return {}

    def generate_predictions_summary(
        self,
        predictions: DataFrame
    ) -> Dict[str, Union[float, Dict[str, int]]]:
        """Generate summary statistics for predictions.

        Args:
            predictions: DataFrame with predictions

        Returns:
            Dictionary containing prediction summary statistics
        """
        summary = {}

        # Basic statistics
        pred_stats = predictions.select(
            F.mean(self.config.prediction_column).alias("mean"),
            F.stddev(self.config.prediction_column).alias("std"),
            F.min(self.config.prediction_column).alias("min"),
            F.max(self.config.prediction_column).alias("max")
        ).collect()[0]

        summary.update({
            "prediction_mean": float(pred_stats["mean"]),
            "prediction_std": float(pred_stats["std"]),
            "prediction_min": float(pred_stats["min"]),
            "prediction_max": float(pred_stats["max"])
        })

        # Distribution of predictions
        if self.config.model_type == "classification":
            class_counts = (
                predictions.groupBy(self.config.prediction_column)
                .count()
                .collect()
            )
            summary["class_distribution"] = {
                int(row[self.config.prediction_column]): int(row["count"])
                for row in class_counts
            }

        return summary

    def cross_validate(
        self,
        model: PipelineModel,
        data: DataFrame,
        num_folds: int = 5
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Perform cross-validation.

        Args:
            model: Model to validate
            data: Input DataFrame
            num_folds: Number of folds

        Returns:
            Tuple of (mean metrics, std metrics)
        """
        # Split data into folds
        splits = data.randomSplit([1.0/num_folds] * num_folds)
        fold_metrics = []

        for i in range(num_folds):
            # Create train and validation sets
            validation = splits[i]
            train = data.subtract(validation)

            # Train and evaluate
            trained_model = model.fit(train)
            metrics = self.evaluate_model(trained_model, validation)
            fold_metrics.append(metrics)

        # Calculate mean and std of metrics
        mean_metrics = {}
        std_metrics = {}

        for metric in fold_metrics[0].keys():
            values = [m[metric] for m in fold_metrics]
            mean_metrics[metric] = float(np.mean(values))
            std_metrics[metric] = float(np.std(values))

        return mean_metrics, std_metrics 