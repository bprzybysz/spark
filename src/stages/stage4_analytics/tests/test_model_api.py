"""
Tests for model API endpoints

This module contains tests for the model API endpoints.
"""

import json
from unittest import TestCase, mock
from fastapi.testclient import TestClient

from src.api.fastapi.main import app
from src.ml.models.registry import Model, PredictionResult


class MockModel(Model):
    """Mock model implementation for testing."""
    
    def __init__(self, name, version):
        """Initialize mock model."""
        super().__init__(name, version, {})
    
    def predict(self, features):
        """Mock prediction method."""
        return PredictionResult(
            prediction=1,
            probability=0.9,
            details={"features": features}
        )


class TestModelAPI(TestCase):
    """Test cases for model API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    @mock.patch('src.core.di.container.get_container')
    def test_list_models(self, mock_get_container):
        """Test listing models endpoint."""
        # Mock model registry
        mock_registry = mock.MagicMock()
        mock_registry.list_models.return_value = [
            {"name": "model1", "version": "1.0"},
            {"name": "model2", "version": "2.0"}
        ]
        
        # Mock container
        mock_container = mock.MagicMock()
        mock_container.model_registry.return_value = mock_registry
        mock_get_container.return_value = mock_container
        
        # Call the endpoint
        response = self.client.get("/models")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("models", data)
        self.assertEqual(len(data["models"]), 2)
        self.assertEqual(data["models"][0]["name"], "model1")
        self.assertEqual(data["models"][1]["name"], "model2")
    
    @mock.patch('src.core.di.container.get_container')
    def test_predict(self, mock_get_container):
        """Test prediction endpoint."""
        # Mock model
        mock_model = MockModel("test_model", "1.0")
        
        # Mock model registry
        mock_registry = mock.MagicMock()
        mock_registry.get_model.return_value = mock_model
        
        # Mock container
        mock_container = mock.MagicMock()
        mock_container.model_registry.return_value = mock_registry
        mock_get_container.return_value = mock_container
        
        # Request data
        request_data = {
            "model_name": "test_model",
            "model_version": "1.0",
            "features": {"feature1": 1, "feature2": 2}
        }
        
        # Call the endpoint
        response = self.client.post(
            "/predict",
            json=request_data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["model_name"], "test_model")
        self.assertEqual(data["model_version"], "1.0")
        self.assertEqual(data["prediction"], 1)
        self.assertEqual(data["probability"], 0.9)
        self.assertIn("details", data)
        self.assertIn("features", data["details"])
        
        # Check model registry called correctly
        mock_registry.get_model.assert_called_once_with("test_model", "1.0")
    
    @mock.patch('src.core.di.container.get_container')
    def test_predict_model_not_found(self, mock_get_container):
        """Test prediction endpoint with non-existent model."""
        # Mock model registry
        from src.ml.models.registry import ModelNotFoundError
        mock_registry = mock.MagicMock()
        mock_registry.get_model.side_effect = ModelNotFoundError("Model not found")
        
        # Mock container
        mock_container = mock.MagicMock()
        mock_container.model_registry.return_value = mock_registry
        mock_get_container.return_value = mock_container
        
        # Request data
        request_data = {
            "model_name": "non_existent_model",
            "model_version": "1.0",
            "features": {"feature1": 1, "feature2": 2}
        }
        
        # Call the endpoint
        response = self.client.post(
            "/predict",
            json=request_data
        )
        
        # Check response (should be 404)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("Model not found", data["detail"])
    
    @mock.patch('src.core.di.container.get_container')
    def test_predict_invalid_request(self, mock_get_container):
        """Test prediction endpoint with invalid request."""
        # Request missing required fields
        request_data = {
            "model_name": "test_model"
            # Missing features
        }
        
        # Call the endpoint
        response = self.client.post(
            "/predict",
            json=request_data
        )
        
        # Check response (should be 422 Unprocessable Entity)
        self.assertEqual(response.status_code, 422)
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy") 