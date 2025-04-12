"""Tests for model monitoring functionality."""

import numpy as np
import pytest
from src.ml.monitoring.model_monitor import ModelMonitor

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    np.random.seed(42)
    
    # Generate baseline data
    n_samples = 1000
    n_features = 5
    
    X_baseline = np.random.normal(0, 1, (n_samples, n_features))
    y_true_baseline = (X_baseline.sum(axis=1) > 0).astype(int)
    y_pred_baseline = y_true_baseline.copy()
    # Add some noise to predictions
    noise_idx = np.random.choice(n_samples, size=int(n_samples * 0.1))
    y_pred_baseline[noise_idx] = 1 - y_pred_baseline[noise_idx]
    
    # Generate drift data (shift mean and variance)
    X_drift = np.random.normal(0.5, 1.5, (n_samples, n_features))
    y_true_drift = (X_drift.sum(axis=1) > 0).astype(int)
    y_pred_drift = y_true_drift.copy()
    # Add more noise to predictions
    noise_idx = np.random.choice(n_samples, size=int(n_samples * 0.3))
    y_pred_drift[noise_idx] = 1 - y_pred_drift[noise_idx]
    
    return {
        'baseline': (X_baseline, y_true_baseline, y_pred_baseline),
        'drift': (X_drift, y_true_drift, y_pred_drift)
    }

def test_model_monitor_initialization():
    """Test ModelMonitor initialization."""
    monitor = ModelMonitor("test_model")
    
    assert monitor.model_name == "test_model"
    assert set(monitor.metrics) == {"accuracy", "precision", "recall", "f1"}
    assert monitor.drift_threshold == 0.05
    assert monitor.alert_threshold == 0.1
    assert monitor.baseline_distribution is None
    assert monitor.baseline_metrics is None
    assert len(monitor.performance_history) == 0

def test_set_baseline(sample_data):
    """Test setting baseline metrics and distribution."""
    X, y_true, y_pred = sample_data['baseline']
    
    monitor = ModelMonitor("test_model")
    baseline_metrics = monitor.set_baseline(y_true, y_pred, X)
    
    assert monitor.baseline_distribution is not None
    assert monitor.baseline_metrics is not None
    assert isinstance(baseline_metrics, dict)
    assert all(metric in baseline_metrics for metric in monitor.metrics)
    assert all(0 <= val <= 1 for val in baseline_metrics.values())
    
    # Check baseline distribution stats
    assert monitor.baseline_distribution['mean'].shape == (X.shape[1],)
    assert monitor.baseline_distribution['std'].shape == (X.shape[1],)

def test_check_performance(sample_data):
    """Test performance checking against baseline."""
    X_base, y_true_base, y_pred_base = sample_data['baseline']
    X_drift, y_true_drift, y_pred_drift = sample_data['drift']
    
    monitor = ModelMonitor("test_model", alert_threshold=0.1)
    monitor.set_baseline(y_true_base, y_pred_base, X_base)
    
    # Check baseline performance (should have no alerts)
    result_base = monitor.check_performance(y_true_base, y_pred_base)
    assert len(result_base['alerts']) == 0
    
    # Check degraded performance (should have alerts)
    result_drift = monitor.check_performance(y_true_drift, y_pred_drift)
    assert len(result_drift['alerts']) > 0
    
    # Verify metrics are being tracked
    assert len(monitor.performance_history) == 2

def test_detect_drift(sample_data):
    """Test drift detection."""
    X_base, y_true_base, y_pred_base = sample_data['baseline']
    X_drift, y_true_drift, y_pred_drift = sample_data['drift']
    
    monitor = ModelMonitor("test_model", drift_threshold=0.05)
    monitor.set_baseline(y_true_base, y_pred_base, X_base)
    
    # Check baseline data (should not detect drift)
    result_base = monitor.detect_drift(X_base)
    assert not result_base['drift_detected']
    assert len(result_base['drifted_features']) == 0
    
    # Check drift data (should detect drift)
    result_drift = monitor.detect_drift(X_drift)
    assert result_drift['drift_detected']
    assert len(result_drift['drifted_features']) > 0

def test_error_handling():
    """Test error handling for uninitialized monitor."""
    monitor = ModelMonitor("test_model")
    
    # Should raise error when checking performance without baseline
    with pytest.raises(ValueError):
        monitor.check_performance(np.array([0, 1]), np.array([0, 1]))
    
    # Should raise error when detecting drift without baseline
    with pytest.raises(ValueError):
        monitor.detect_drift(np.array([[0, 1], [1, 0]])) 