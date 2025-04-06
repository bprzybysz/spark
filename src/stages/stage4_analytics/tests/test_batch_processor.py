"""
Tests for batch processor module

This module contains tests for the BatchProcessor class.
"""

import os
import json
import shutil
import tempfile
from datetime import datetime
from unittest import TestCase, mock

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from src.stages.stage4_analytics.batch_processor import BatchProcessor


class TestBatchProcessor(TestCase):
    """Test cases for BatchProcessor class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up Spark session and test fixtures."""
        cls.spark = SparkSession.builder \
            .appName("BatchProcessorTest") \
            .master("local[*]") \
            .getOrCreate()
        
        # Create test directory
        cls.test_dir = tempfile.mkdtemp()
        
        # Create test data
        # Metrics DataFrame - Use only numeric columns for metrics
        metrics_data = [
            {"accuracy": 0.85, "precision": 0.82, "recall": 0.81},
            {"accuracy": 0.86, "precision": 0.84, "recall": 0.82},
            {"accuracy": 0.87, "precision": 0.85, "recall": 0.84},
            {"accuracy": 0.84, "precision": 0.81, "recall": 0.80},
            {"accuracy": 0.88, "precision": 0.86, "recall": 0.85},
        ]
        cls.metrics_df = cls.spark.createDataFrame(metrics_data)
        
        # Predictions DataFrame
        predictions_data = [
            {"label": 1, "prediction": 1, "probability": 0.9, "features": [0.1, 0.2, 0.3]},
            {"label": 0, "prediction": 0, "probability": 0.8, "features": [0.2, 0.3, 0.4]},
            {"label": 1, "prediction": 1, "probability": 0.7, "features": [0.3, 0.4, 0.5]},
            {"label": 1, "prediction": 0, "probability": 0.4, "features": [0.4, 0.5, 0.6]},
            {"label": 0, "prediction": 1, "probability": 0.3, "features": [0.5, 0.6, 0.7]},
        ]
        cls.predictions_df = cls.spark.createDataFrame(predictions_data)
        
        # Save test data as parquet files
        cls.metrics_path = os.path.join(cls.test_dir, "metrics.parquet")
        cls.predictions_path = os.path.join(cls.test_dir, "predictions.parquet")
        
        cls.metrics_df.write.parquet(cls.metrics_path)
        cls.predictions_df.write.parquet(cls.predictions_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up resources."""
        # Stop Spark session
        cls.spark.stop()
        
        # Remove test directory
        shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up test instance."""
        self.output_path = os.path.join(self.test_dir, "output")
        self.processor = BatchProcessor(
            spark=self.spark,
            output_path=self.output_path
        )
    
    def tearDown(self):
        """Clean up after each test."""
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.processor.output_path, self.output_path)
        self.assertTrue(os.path.exists(self.output_path))
    
    @mock.patch('src.stages.stage4_analytics.batch_processor.BatchProcessor._log')
    @mock.patch('src.stages.stage4_analytics.analytics.DataAnalyzer.generate_analytics_report')
    def test_process_model_metrics(self, mock_generate_report, mock_log):
        """Test processing model metrics."""
        # Mock the generate_analytics_report to return a valid report
        mock_report = {
            "summary_statistics": {
                "accuracy": {"mean": 0.86, "std": 0.016},
                "precision": {"mean": 0.836, "std": 0.02},
                "recall": {"mean": 0.824, "std": 0.018}
            }
        }
        mock_generate_report.return_value = mock_report
        
        # Run the processor
        result = self.processor.process_model_metrics(
            metrics_df=self.metrics_df,
            model_name="test_model"
        )
        
        # Check that result is a dictionary
        self.assertIsInstance(result, dict)
        self.assertEqual(result, mock_report)
        
        # Check that the log method was called
        mock_log.assert_called()
        
        # Verify there was a call with a message about saving metrics
        for args, _ in mock_log.call_args_list:
            # Check if any call argument starts with "Saved metrics report"
            for arg in args:
                if isinstance(arg, str) and arg.startswith("Saved metrics report"):
                    break
            else:
                continue
            break
        else:
            self.fail("No log message containing 'Saved metrics report' was found")
        
        # Verify generate_analytics_report was called with correct arguments
        mock_generate_report.assert_called_once()
        config_arg = mock_generate_report.call_args[0][1]
        self.assertIn('numeric_columns', config_arg)
        self.assertListEqual(sorted(config_arg['numeric_columns']), ['accuracy', 'precision', 'recall'])
    
    def test_process_prediction_data(self):
        """Test processing prediction data."""
        # Run the processor
        result = self.processor.process_prediction_data(
            predictions_df=self.predictions_df,
            model_name="test_model"
        )
        
        # Check that result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check that output file was created
        files = os.listdir(self.output_path)
        self.assertTrue(any(f.startswith("test_model_predictions_") for f in files))
        
        # Check that the file contains valid JSON
        prediction_file = next(f for f in files if f.startswith("test_model_predictions_"))
        with open(os.path.join(self.output_path, prediction_file), 'r') as f:
            data = json.load(f)
            
        # Verify content
        self.assertIn("summary_metrics", data)
        self.assertIn("mean_absolute_error", data["summary_metrics"])
        self.assertIn("error_distribution", data)
        self.assertIn("confusion_matrix", data)
    
    @mock.patch('src.stages.stage4_analytics.batch_processor.BatchProcessor.process_model_metrics')
    def test_run_batch_job(self, mock_process_metrics):
        """Test running a complete batch job."""
        # Mock process_model_metrics to return a valid result
        mock_metrics_result = {"summary_statistics": {"accuracy": {"mean": 0.86}}}
        mock_process_metrics.return_value = mock_metrics_result
        
        # Run the processor
        result = self.processor.run_batch_job(
            metrics_path=self.metrics_path,
            predictions_path=self.predictions_path,
            model_name="test_model"
        )
        
        # Check that result contains both metrics and predictions
        self.assertIn("metrics", result)
        self.assertIn("predictions", result)
        self.assertEqual(result["metrics"], mock_metrics_result)
        
        # Check that summary file was created
        files = os.listdir(self.output_path)
        self.assertTrue(any(f.startswith("batch_summary_") for f in files))
        
        # Check that the file contains valid JSON
        summary_file = next(f for f in files if f.startswith("batch_summary_"))
        with open(os.path.join(self.output_path, summary_file), 'r') as f:
            data = json.load(f)
            
        # Verify content
        self.assertEqual(data["model_name"], "test_model")
        self.assertTrue(data["metrics_processed"])
        self.assertTrue(data["predictions_processed"])
    
    def test_error_handling(self):
        """Test error handling for invalid data."""
        # Create DataFrame missing required columns
        invalid_df = self.spark.createDataFrame([
            {"feature1": 1, "feature2": 2},
            {"feature1": 3, "feature2": 4}
        ])
        
        # Processing should raise ValueError due to missing columns
        with self.assertRaises(ValueError):
            self.processor.process_prediction_data(
                predictions_df=invalid_df,
                model_name="test_model"
            )
    
    @mock.patch('src.stages.stage4_analytics.analytics.DataAnalyzer.generate_analytics_report')
    def test_exception_handling(self, mock_generate):
        """Test handling of exceptions during processing."""
        # Mock generate_analytics_report to raise an exception
        mock_generate.side_effect = Exception("Test exception")
        
        # Processing should propagate the exception
        with self.assertRaises(Exception):
            self.processor.process_model_metrics(
                metrics_df=self.metrics_df,
                model_name="test_model"
            )
        
        # Run batch job should catch and report the error
        result = self.processor.run_batch_job(
            metrics_path=self.metrics_path,
            predictions_path=self.predictions_path,
            model_name="test_model"
        )
        
        # Check that metrics_error is reported
        self.assertIn("metrics_error", result)
        self.assertIn("predictions", result) 