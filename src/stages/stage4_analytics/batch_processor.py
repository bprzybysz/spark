"""
Batch processor for model analytics data

This module provides the BatchProcessor class for processing model analytics data in batches.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from src.stages.stage4_analytics.analytics import DataAnalyzer
from src.stages.stage4_analytics.config import AnalyticsConfig
from src.core.logging.logger import Logger


class BatchProcessor:
    """Class for batch processing of model analytics data."""
    
    def __init__(
        self,
        spark: Optional[SparkSession] = None,
        output_path: str = "data/analytics",
        logger: Optional[Logger] = None
    ):
        """
        Initialize the BatchProcessor.
        
        Args:
            spark: Optional SparkSession instance
            output_path: Path to save batch results
            logger: Optional logger instance
        """
        self.spark = spark or SparkSession.builder \
            .appName("AnalyticsBatchProcessor") \
            .master("local[*]") \
            .getOrCreate()
        
        self.output_path = output_path
        self.logger = logger
        self.analyzer = DataAnalyzer(spark=self.spark)
        self.config = AnalyticsConfig()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
    
    def _log(self, message: str, level: str = "info"):
        """Log a message if logger is available."""
        if self.logger:
            if level == "info":
                self.logger.info(message)
            elif level == "error":
                self.logger.error(message)
            elif level == "warning":
                self.logger.warning(message)
        else:
            print(f"[{level.upper()}] {message}")
    
    def process_model_metrics(
        self,
        metrics_df: DataFrame,
        model_name: str,
        batch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process model metrics data.
        
        Args:
            metrics_df: DataFrame containing model metrics
            model_name: Name of the model
            batch_id: Optional batch identifier
            
        Returns:
            Dictionary of processed metrics
        """
        batch_id = batch_id or datetime.now().strftime("%Y%m%d%H%M%S")
        self._log(f"Processing batch {batch_id} for model {model_name}")
        
        # Create analytics config for model metrics
        analytics_config = self.config.create_config(
            numeric_columns=metrics_df.columns,
            correlation_columns=metrics_df.columns,
            time_column="timestamp" if "timestamp" in metrics_df.columns else None,
            metric_columns=[c for c in metrics_df.columns if c != "timestamp"],
            window_size=7,
            outlier_columns=[c for c in metrics_df.columns if c not in ["timestamp", "model_name", "model_version"]]
        )
        
        # Generate analytics report
        try:
            report = self.analyzer.generate_analytics_report(metrics_df, analytics_config)
            
            # Save the report
            output_file = os.path.join(
                self.output_path,
                f"{model_name}_metrics_{batch_id}.json"
            )
            
            # Convert DataFrame results to dictionary for JSON serialization
            processed_report = {}
            for key, value in report.items():
                if isinstance(value, DataFrame):
                    processed_report[key] = value.limit(1000).toPandas().to_dict()
                else:
                    processed_report[key] = value
            
            with open(output_file, "w") as f:
                json.dump(processed_report, f, indent=2)
                
            self._log(f"Saved metrics report to {output_file}")
            return processed_report
            
        except Exception as e:
            self._log(f"Error processing batch {batch_id}: {str(e)}", "error")
            raise
    
    def process_prediction_data(
        self,
        predictions_df: DataFrame,
        model_name: str,
        batch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process model prediction data.
        
        Args:
            predictions_df: DataFrame containing predictions
            model_name: Name of the model
            batch_id: Optional batch identifier
            
        Returns:
            Dictionary of processed prediction insights
        """
        batch_id = batch_id or datetime.now().strftime("%Y%m%d%H%M%S")
        self._log(f"Processing prediction data batch {batch_id} for model {model_name}")
        
        # Basic validation
        required_columns = ["prediction", "label"]
        missing_columns = [col for col in required_columns if col not in predictions_df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Calculate prediction metrics
        try:
            # Add error column
            predictions_with_error = predictions_df.withColumn(
                "error",
                F.abs(F.col("prediction") - F.col("label"))
            )
            
            # Calculate summary metrics
            summary = predictions_with_error.select(
                F.mean("error").alias("mean_absolute_error"),
                F.stddev("error").alias("std_error"),
                F.min("error").alias("min_error"),
                F.max("error").alias("max_error"),
                F.expr("percentile_approx(error, 0.95)").alias("p95_error")
            ).collect()[0]
            
            # Calculate error distribution
            error_distribution = predictions_with_error.select(
                F.when(F.col("error") < 0.1, "0-0.1")
                .when(F.col("error") < 0.5, "0.1-0.5")
                .when(F.col("error") < 1.0, "0.5-1.0")
                .when(F.col("error") < 5.0, "1.0-5.0")
                .otherwise(">5.0").alias("error_range")
            ).groupBy("error_range").count()
            
            # Save results
            output_file = os.path.join(
                self.output_path,
                f"{model_name}_predictions_{batch_id}.json"
            )
            
            results = {
                "summary_metrics": {
                    "mean_absolute_error": float(summary["mean_absolute_error"]),
                    "std_error": float(summary["std_error"]),
                    "min_error": float(summary["min_error"]),
                    "max_error": float(summary["max_error"]),
                    "p95_error": float(summary["p95_error"])
                },
                "error_distribution": error_distribution.toPandas().to_dict()
            }
            
            # Add confusion matrix for classification models if probability column exists
            if "probability" in predictions_df.columns:
                confusion = predictions_df.groupBy("label", "prediction").count()
                results["confusion_matrix"] = confusion.toPandas().to_dict()
            
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)
                
            self._log(f"Saved prediction analysis to {output_file}")
            return results
            
        except Exception as e:
            self._log(f"Error processing prediction batch {batch_id}: {str(e)}", "error")
            raise
    
    def run_batch_job(
        self,
        metrics_path: str,
        predictions_path: str,
        model_name: str
    ) -> Dict[str, Any]:
        """
        Run a complete batch job processing both metrics and predictions.
        
        Args:
            metrics_path: Path to metrics data
            predictions_path: Path to predictions data
            model_name: Name of the model
            
        Returns:
            Dictionary with batch processing results
        """
        batch_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self._log(f"Starting batch job {batch_id} for model {model_name}")
        
        results = {}
        
        # Process metrics
        try:
            metrics_df = self.spark.read.parquet(metrics_path)
            results["metrics"] = self.process_model_metrics(
                metrics_df=metrics_df,
                model_name=model_name,
                batch_id=batch_id
            )
        except Exception as e:
            self._log(f"Error processing metrics: {str(e)}", "error")
            results["metrics_error"] = str(e)
        
        # Process predictions
        try:
            predictions_df = self.spark.read.parquet(predictions_path)
            results["predictions"] = self.process_prediction_data(
                predictions_df=predictions_df,
                model_name=model_name,
                batch_id=batch_id
            )
        except Exception as e:
            self._log(f"Error processing predictions: {str(e)}", "error")
            results["predictions_error"] = str(e)
        
        # Save job summary
        summary_file = os.path.join(
            self.output_path,
            f"batch_summary_{batch_id}.json"
        )
        
        with open(summary_file, "w") as f:
            summary = {
                "batch_id": batch_id,
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "metrics_processed": "metrics" in results,
                "predictions_processed": "predictions" in results
            }
            json.dump(summary, f, indent=2)
        
        self._log(f"Batch job {batch_id} completed")
        return results 