"""
Tests for model analytics API endpoints

This module contains tests for the model analytics API endpoints.
"""

import os
import json
import tempfile
from unittest import TestCase, mock
from fastapi.testclient import TestClient

from src.api.fastapi.main import app
from src.stages.stage4_analytics.batch_scheduler import BatchScheduler


class TestModelAnalyticsAPI(TestCase):
    """Test cases for model analytics API endpoints."""
    
    def setUp(self):
        """Set up test client and mocks."""
        # Initialize FastAPI test client
        self.client = TestClient(app)
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

    def tearDown(self):
        """Clean up after tests."""
        # Stop all patches
        self.scheduler_patcher.stop()
        
        # Clean up temporary directory
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_create_analytics_job(self):
        """Test creating a new analytics job."""
        job_request = {
            "job_id": "test-job-1",
            "model_name": "test-model",
            "metrics_path": "/path/to/metrics",
            "predictions_path": "/path/to/predictions",
            "frequency": "daily"
        }
        
        # Mock scheduler's add_job method
        self.mock_scheduler.add_job.return_value = job_request
        
        # Make request
        response = self.client.post("/analytics/jobs", json=job_request)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), job_request)
        self.mock_scheduler.add_job.assert_called_once_with(**job_request)

    def test_list_analytics_jobs(self):
        """Test listing analytics jobs."""
        # Mock scheduler's list_jobs method
        mock_jobs = [
            {"job_id": "job-1", "status": "running"},
            {"job_id": "job-2", "status": "completed"}
        ]
        self.mock_scheduler.list_jobs.return_value = mock_jobs
        
        # Make request
        response = self.client.get("/analytics/jobs")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["jobs"], mock_jobs)
        self.mock_scheduler.list_jobs.assert_called_once()

    def test_get_job_status(self):
        """Test getting status of a specific job."""
        job_id = "test-job-1"
        mock_status = {"job_id": job_id, "status": "completed", "result": "success"}
        self.mock_scheduler.get_job_status.return_value = mock_status
        
        # Make request
        response = self.client.get(f"/analytics/jobs/{job_id}/status")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_status)
        self.mock_scheduler.get_job_status.assert_called_once_with(job_id)

    def test_update_analytics_job(self):
        """Test updating an analytics job."""
        job_id = "test-job-1"
        job_update = {
            "frequency": "weekly",
            "enabled": False
        }
        
        # Mock scheduler's update_job method
        updated_job = {"job_id": job_id, **job_update}
        self.mock_scheduler.update_job.return_value = updated_job
        
        # Make request
        response = self.client.put(f"/analytics/jobs/{job_id}", json=job_update)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), updated_job)
        self.mock_scheduler.update_job.assert_called_once_with(job_id, **job_update)

    def test_delete_analytics_job(self):
        """Test deleting an analytics job."""
        job_id = "test-job-1"
        
        # Make request
        response = self.client.delete(f"/analytics/jobs/{job_id}")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.mock_scheduler.delete_job.assert_called_once_with(job_id)

    def test_job_not_found(self):
        """Test handling of non-existent job."""
        job_id = "non-existent-job"
        self.mock_scheduler.get_job_status.side_effect = KeyError("Job not found")
        
        # Make request
        response = self.client.get(f"/analytics/jobs/{job_id}/status")
        
        # Check response
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())
        self.mock_scheduler.get_job_status.assert_called_once_with(job_id)

    def test_invalid_job_request(self):
        """Test handling of invalid job request."""
        invalid_request = {
            "job_id": "test-job-1"
            # Missing required fields
        }
        
        # Make request
        response = self.client.post("/analytics/jobs", json=invalid_request)
        
        # Check response
        self.assertEqual(response.status_code, 422)  # Validation error
        self.assertIn("detail", response.json())

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
"""
Tests for model analytics API endpoints

This module contains tests for the model analytics API endpoints.
"""

import os
import json
import tempfile
from unittest import TestCase, mock
from fastapi.testclient import TestClient

from src.api.fastapi.main import app
from src.stages.stage4_analytics.batch_scheduler import BatchScheduler


class TestModelAnalyticsAPI(TestCase):
    """Test cases for model analytics API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app, root_path="/")
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
        self.mock_scheduler = mock.MagicMock(spec=BatchScheduler)
        self.mock_scheduler.output_path = self.test_dir
        self.mock_get_scheduler.return_value = self.mock_scheduler

        # Set up mock for the get_scheduler dependency
        self.scheduler_patcher = mock.patch('src.api.fastapi.model_analytics.get_scheduler')
        self.mock_get_scheduler = self.scheduler_patcher.start()
        
        # Create mock scheduler
       