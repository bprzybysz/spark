"""Tests for monitoring visualization functionality."""

import pytest
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from src.ml.monitoring.visualization import MonitoringDashboard

@pytest.fixture
def sample_history():
    """Create sample monitoring history data."""
    base_time = datetime.now()
    history = []
    
    for i in range(5):
        history.append({
            'timestamp': base_time + timedelta(hours=i),
            'metrics': {
                'accuracy': 0.9 - i * 0.05,
                'precision': 0.85 - i * 0.03,
                'recall': 0.88 - i * 0.04
            },
            'alerts': ['Alert 1'] if i > 2 else []
        })
    
    return history

@pytest.fixture
def sample_drift_results():
    """Create sample drift detection results."""
    base_time = datetime.now()
    results = []
    
    for i in range(3):
        results.append({
            'timestamp': base_time + timedelta(hours=i),
            'drift_detected': i > 1,
            'p_values': [0.1 - i * 0.03, 0.2 - i * 0.05, 0.15 - i * 0.04],
            'drifted_features': [0, 2] if i > 1 else []
        })
    
    return results

def test_dashboard_initialization():
    """Test MonitoringDashboard initialization."""
    dashboard = MonitoringDashboard()
    assert dashboard.figure_size == (12, 8)
    
    custom_size = (10, 6)
    dashboard = MonitoringDashboard(figure_size=custom_size)
    assert dashboard.figure_size == custom_size

def test_plot_metric_history(sample_history):
    """Test metric history plotting."""
    dashboard = MonitoringDashboard()
    
    # Clear any existing plots
    plt.close('all')
    
    # Test with default metrics
    dashboard.plot_metric_history(sample_history)
    fig = plt.gcf()
    assert len(fig.axes) == 1
    assert len(fig.axes[0].lines) == 3  # Three metrics
    
    # Test with specific metrics
    plt.close('all')
    dashboard.plot_metric_history(sample_history, metrics=['accuracy'])
    fig = plt.gcf()
    assert len(fig.axes[0].lines) == 1  # One metric
    
    plt.close('all')

def test_plot_drift_heatmap(sample_drift_results):
    """Test drift heatmap plotting."""
    dashboard = MonitoringDashboard()
    
    # Clear any existing plots
    plt.close('all')
    
    # Test with default feature names
    dashboard.plot_drift_heatmap(sample_drift_results)
    fig = plt.gcf()
    assert len(fig.axes) == 2  # Main plot and colorbar
    
    # Test with custom feature names
    plt.close('all')
    feature_names = ['Feature A', 'Feature B', 'Feature C']
    dashboard.plot_drift_heatmap(sample_drift_results, feature_names=feature_names)
    fig = plt.gcf()
    assert len(fig.axes) == 2
    
    plt.close('all')

def test_plot_alert_summary(sample_history):
    """Test alert summary plotting."""
    dashboard = MonitoringDashboard()
    
    # Clear any existing plots
    plt.close('all')
    
    dashboard.plot_alert_summary(sample_history)
    fig = plt.gcf()
    assert len(fig.axes) == 1
    
    # Verify alert counts
    alert_counts = [len(h['alerts']) for h in sample_history]
    assert sum(alert_counts) == 2  # Based on sample_history fixture
    
    plt.close('all')

def test_plot_performance_comparison():
    """Test performance comparison plotting."""
    dashboard = MonitoringDashboard()
    
    # Clear any existing plots
    plt.close('all')
    
    current = {'accuracy': 0.85, 'precision': 0.82, 'recall': 0.84}
    baseline = {'accuracy': 0.90, 'precision': 0.88, 'recall': 0.89}
    
    dashboard.plot_performance_comparison(current, baseline)
    fig = plt.gcf()
    assert len(fig.axes) == 1
    assert len(fig.axes[0].patches) == 6  # Two bars for each metric
    
    plt.close('all') 