"""
Tests for batch scheduler module

This module contains tests for the BatchScheduler class.
"""

import os
import json
import shutil
import tempfile
from datetime import datetime, timedelta
from unittest import TestCase, mock

from src.stages.stage4_analytics.batch_scheduler import BatchScheduler
from src.stages.stage4_analytics.batch_processor import BatchProcessor


class TestBatchScheduler(TestCase):
    """Test cases for BatchScheduler class."""
    
    def setUp(self):
        """Set up test instance."""
        self.test_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.test_dir, "output")
        self.schedule_file = os.path.join(self.test_dir, "schedule.json")
        
        self.scheduler = BatchScheduler(
            output_path=self.output_path,
            schedule_file=self.schedule_file
        )
    
    def tearDown(self):
        """Clean up after each test."""
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test initialization."""
        # Check output path
        self.assertEqual(self.scheduler.output_path, self.output_path)
        
        # Check schedule file
        self.assertEqual(self.scheduler.schedule_file, self.schedule_file)
        
        # Check schedule structure
        self.assertIn("jobs", self.scheduler.schedule)
        self.assertIn("last_updated", self.scheduler.schedule)
        self.assertEqual(len(self.scheduler.schedule["jobs"]), 0)
    
    def test_add_job(self):
        """Test adding a job."""
        # Add a job
        job = self.scheduler.add_job(
            job_id="test_job",
            model_name="test_model",
            metrics_path="/path/to/metrics",
            predictions_path="/path/to/predictions",
            frequency="daily"
        )
        
        # Check job properties
        self.assertEqual(job["job_id"], "test_job")
        self.assertEqual(job["model_name"], "test_model")
        self.assertEqual(job["metrics_path"], "/path/to/metrics")
        self.assertEqual(job["predictions_path"], "/path/to/predictions")
        self.assertEqual(job["frequency"], "daily")
        self.assertEqual(job["status"], "scheduled")
        self.assertIsNone(job["last_run"])
        self.assertIsNotNone(job["next_run"])
        
        # Check schedule updated
        self.assertEqual(len(self.scheduler.schedule["jobs"]), 1)
        self.assertEqual(self.scheduler.schedule["jobs"][0]["job_id"], "test_job")
    
    def test_add_job_duplicate(self):
        """Test adding a duplicate job."""
        # Add a job
        self.scheduler.add_job(
            job_id="test_job",
            model_name="test_model",
            metrics_path="/path/to/metrics",
            predictions_path="/path/to/predictions"
        )
        
        # Try to add a duplicate job
        with self.assertRaises(ValueError):
            self.scheduler.add_job(
                job_id="test_job",
                model_name="another_model",
                metrics_path="/path/to/metrics",
                predictions_path="/path/to/predictions"
            )
    
    def test_update_job(self):
        """Test updating a job."""
        # Add a job
        self.scheduler.add_job(
            job_id="test_job",
            model_name="test_model",
            metrics_path="/path/to/metrics",
            predictions_path="/path/to/predictions",
            frequency="daily"
        )
        
        # Update the job
        updated_job = self.scheduler.update_job(
            job_id="test_job",
            model_name="updated_model",
            frequency="hourly",
            enabled=False
        )
        
        # Check updated properties
        self.assertEqual(updated_job["model_name"], "updated_model")
        self.assertEqual(updated_job["frequency"], "hourly")
        self.assertFalse(updated_job["enabled"])
        
        # Check schedule updated
        self.assertEqual(self.scheduler.schedule["jobs"][0]["model_name"], "updated_model")
        self.assertEqual(self.scheduler.schedule["jobs"][0]["frequency"], "hourly")
        self.assertFalse(self.scheduler.schedule["jobs"][0]["enabled"])
    
    def test_update_job_not_found(self):
        """Test updating a non-existent job."""
        with self.assertRaises(ValueError):
            self.scheduler.update_job(
                job_id="non_existent_job",
                model_name="updated_model"
            )
    
    def test_delete_job(self):
        """Test deleting a job."""
        # Add a job
        self.scheduler.add_job(
            job_id="test_job",
            model_name="test_model",
            metrics_path="/path/to/metrics",
            predictions_path="/path/to/predictions"
        )
        
        # Delete the job
        result = self.scheduler.delete_job("test_job")
        
        # Check result
        self.assertTrue(result)
        
        # Check job removed from schedule
        self.assertEqual(len(self.scheduler.schedule["jobs"]), 0)
    
    def test_delete_job_not_found(self):
        """Test deleting a non-existent job."""
        result = self.scheduler.delete_job("non_existent_job")
        self.assertFalse(result)
    
    def test_list_jobs(self):
        """Test listing jobs."""
        # Add jobs
        self.scheduler.add_job(
            job_id="job1",
            model_name="model1",
            metrics_path="/path/to/metrics1",
            predictions_path="/path/to/predictions1"
        )
        self.scheduler.add_job(
            job_id="job2",
            model_name="model2",
            metrics_path="/path/to/metrics2",
            predictions_path="/path/to/predictions2"
        )
        
        # List jobs
        jobs = self.scheduler.list_jobs()
        
        # Check result
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["job_id"], "job1")
        self.assertEqual(jobs[1]["job_id"], "job2")
    
    def test_calculate_next_run(self):
        """Test next run calculation."""
        # Create a job with a last_run time
        now = datetime.now()
        job = {
            "enabled": True,
            "frequency": "hourly",
            "last_run": now.isoformat()
        }
        
        # Calculate next run
        next_run = self.scheduler._calculate_next_run(job)
        
        # Check result
        expected = (now + timedelta(hours=1)).isoformat()
        self.assertEqual(next_run, expected)
        
        # Test daily frequency
        job["frequency"] = "daily"
        next_run = self.scheduler._calculate_next_run(job)
        expected = (now + timedelta(days=1)).isoformat()
        self.assertEqual(next_run, expected)
        
        # Test weekly frequency
        job["frequency"] = "weekly"
        next_run = self.scheduler._calculate_next_run(job)
        expected = (now + timedelta(weeks=1)).isoformat()
        self.assertEqual(next_run, expected)
        
        # Test unknown frequency (should default to daily)
        job["frequency"] = "unknown"
        next_run = self.scheduler._calculate_next_run(job)
        expected = (now + timedelta(days=1)).isoformat()
        self.assertEqual(next_run, expected)
        
        # Test disabled job
        job["enabled"] = False
        next_run = self.scheduler._calculate_next_run(job)
        self.assertIsNone(next_run)
    
    @mock.patch('src.stages.stage4_analytics.batch_processor.BatchProcessor.run_batch_job')
    def test_run_job(self, mock_run_batch):
        """Test running a job."""
        # Mock the batch processor
        mock_run_batch.return_value = {"metrics": {}, "predictions": {}}
        
        # Add a job
        self.scheduler.add_job(
            job_id="test_job",
            model_name="test_model",
            metrics_path="/path/to/metrics",
            predictions_path="/path/to/predictions"
        )
        
        # Run the job
        result = self.scheduler.run_job("test_job")
        
        # Check result
        self.assertIn("metrics", result)
        self.assertIn("predictions", result)
        
        # Check job status updated
        job = next(job for job in self.scheduler.schedule["jobs"] if job["job_id"] == "test_job")
        self.assertEqual(job["status"], "completed")
        self.assertIsNotNone(job["last_run"])
        self.assertIsNotNone(job["next_run"])
        
        # Check run history (expect 2 entries: running + completed)
        self.assertEqual(len(job["run_history"]), 2)
        self.assertEqual(job["run_history"][0]["status"], "running")
        self.assertEqual(job["run_history"][1]["status"], "completed")
        
        # Check batch processor called with correct arguments
        mock_run_batch.assert_called_once_with(
            metrics_path="/path/to/metrics",
            predictions_path="/path/to/predictions",
            model_name="test_model"
        )
    
    def test_run_job_not_found(self):
        """Test running a non-existent job."""
        with self.assertRaises(ValueError):
            self.scheduler.run_job("non_existent_job")
    
    @mock.patch('src.stages.stage4_analytics.batch_processor.BatchProcessor.run_batch_job')
    def test_run_job_error(self, mock_run_batch):
        """Test error handling when running a job."""
        # Mock the batch processor to raise an exception
        mock_run_batch.side_effect = Exception("Test error")
        
        # Add a job
        self.scheduler.add_job(
            job_id="test_job",
            model_name="test_model",
            metrics_path="/path/to/metrics",
            predictions_path="/path/to/predictions"
        )
        
        # Run the job (should raise exception)
        with self.assertRaises(Exception):
            self.scheduler.run_job("test_job")
        
        # Check job status updated to failed
        job = next(job for job in self.scheduler.schedule["jobs"] if job["job_id"] == "test_job")
        self.assertEqual(job["status"], "failed")
        self.assertIsNotNone(job["last_run"])
        self.assertIsNotNone(job["next_run"])
        
        # Check run history (expect 2 entries: running + failed)
        self.assertEqual(len(job["run_history"]), 2)
        self.assertEqual(job["run_history"][0]["status"], "running")
        self.assertEqual(job["run_history"][1]["status"], "failed")
    
    @mock.patch('src.stages.stage4_analytics.batch_scheduler.BatchScheduler.run_job')
    def test_run_due_jobs(self, mock_run_job):
        """Test running due jobs."""
        # Mock the run_job method
        mock_run_job.return_value = {"metrics": {}, "predictions": {}}
        
        # Add jobs with different next_run times
        now = datetime.now()
        past = (now - timedelta(hours=1)).isoformat()
        future = (now + timedelta(hours=1)).isoformat()
        
        # Job 1: Due (next_run in the past)
        job1 = self.scheduler.add_job(
            job_id="job1",
            model_name="model1",
            metrics_path="/path/to/metrics1",
            predictions_path="/path/to/predictions1"
        )
        job1["next_run"] = past
        
        # Job 2: Not due (next_run in the future)
        job2 = self.scheduler.add_job(
            job_id="job2",
            model_name="model2",
            metrics_path="/path/to/metrics2",
            predictions_path="/path/to/predictions2"
        )
        job2["next_run"] = future
        
        # Job 3: Disabled
        job3 = self.scheduler.add_job(
            job_id="job3",
            model_name="model3",
            metrics_path="/path/to/metrics3",
            predictions_path="/path/to/predictions3",
            enabled=False
        )
        job3["next_run"] = past
        
        # Update schedule
        self.scheduler._save_schedule()
        
        # Run due jobs
        results = self.scheduler.run_due_jobs()
        
        # Check results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["job_id"], "job1")
        self.assertEqual(results[0]["status"], "completed")
        
        # Check run_job called for due jobs
        mock_run_job.assert_called_once_with("job1")
    
    @mock.patch('time.sleep')
    @mock.patch('src.stages.stage4_analytics.batch_scheduler.BatchScheduler.run_due_jobs')
    def test_start_scheduler(self, mock_run_due_jobs, mock_sleep):
        """Test starting the scheduler."""
        # Configure the mock
        mock_run_due_jobs.return_value = [{"job_id": "job1", "status": "completed"}]
        
        # Start scheduler with max_runs=2
        self.scheduler.start_scheduler(interval_seconds=1, max_runs=2)
        
        # Check run_due_jobs called twice
        self.assertEqual(mock_run_due_jobs.call_count, 2)
        
        # Check sleep called once (after first run)
        mock_sleep.assert_called_once_with(1)
    
    @mock.patch('time.sleep')
    @mock.patch('src.stages.stage4_analytics.batch_scheduler.BatchScheduler.run_due_jobs')
    def test_start_scheduler_keyboard_interrupt(self, mock_run_due_jobs, mock_sleep):
        """Test keyboard interrupt handling in scheduler."""
        # Configure the mock to raise KeyboardInterrupt
        mock_sleep.side_effect = KeyboardInterrupt()
        
        # Start scheduler
        self.scheduler.start_scheduler()
        
        # Check run_due_jobs called once
        mock_run_due_jobs.assert_called_once() 