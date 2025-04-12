"""Model performance monitoring system.

This module provides functionality for monitoring ML model performance,
including drift detection, metric tracking, and alerting.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import numpy as np
from scipy import stats
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import logging

logger = logging.getLogger(__name__)

class ModelMonitor:
    """Monitors model performance and detects drift."""
    
    def __init__(
        self,
        model_name: str,
        metrics: List[str] = None,
        drift_threshold: float = 0.05,
        alert_threshold: float = 0.1
    ):
        """Initialize the model monitor.
        
        Args:
            model_name: Name of the model being monitored
            metrics: List of metrics to track (default: accuracy, precision, recall, f1)
            drift_threshold: P-value threshold for drift detection
            alert_threshold: Performance drop threshold for alerts
        """
        self.model_name = model_name
        self.metrics = metrics or ["accuracy", "precision", "recall", "f1"]
        self.drift_threshold = drift_threshold
        self.alert_threshold = alert_threshold
        
        # Initialize storage
        self.baseline_distribution = None
        self.baseline_metrics = None
        self.performance_history = []
        
    def set_baseline(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        features: np.ndarray
    ) -> Dict[str, float]:
        """Set baseline performance and distribution.
        
        Args:
            y_true: Ground truth labels
            y_pred: Model predictions
            features: Input features used for distribution baseline
            
        Returns:
            Dict of baseline metric values
        """
        # Store feature distribution
        self.baseline_distribution = {
            'mean': np.mean(features, axis=0),
            'std': np.std(features, axis=0),
            'timestamp': datetime.now()
        }
        
        # Calculate baseline metrics
        self.baseline_metrics = self._calculate_metrics(y_true, y_pred)
        
        logger.info(f"Set baseline metrics for {self.model_name}: {self.baseline_metrics}")
        return self.baseline_metrics
    
    def check_performance(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        raise_alert: bool = True
    ) -> Dict[str, Any]:
        """Check current model performance against baseline.
        
        Args:
            y_true: Ground truth labels
            y_pred: Model predictions
            raise_alert: Whether to raise alerts for performance drops
            
        Returns:
            Dict containing metrics and alert status
        """
        if self.baseline_metrics is None:
            raise ValueError("Baseline metrics not set. Call set_baseline() first.")
            
        # Calculate current metrics
        current_metrics = self._calculate_metrics(y_true, y_pred)
        
        # Check for significant drops
        alerts = []
        for metric in self.metrics:
            baseline = self.baseline_metrics[metric]
            current = current_metrics[metric]
            drop = baseline - current
            
            if drop > self.alert_threshold and raise_alert:
                alert = f"{metric} dropped by {drop:.3f} (baseline: {baseline:.3f}, current: {current:.3f})"
                alerts.append(alert)
                logger.warning(f"Performance alert for {self.model_name}: {alert}")
        
        # Store in history
        self.performance_history.append({
            'timestamp': datetime.now(),
            'metrics': current_metrics,
            'alerts': alerts
        })
        
        return {
            'metrics': current_metrics,
            'baseline': self.baseline_metrics,
            'alerts': alerts
        }
    
    def detect_drift(
        self,
        features: np.ndarray,
        raise_alert: bool = True
    ) -> Dict[str, Any]:
        """Detect feature drift using statistical tests.
        
        Args:
            features: Current feature values to check for drift
            raise_alert: Whether to raise alerts for detected drift
            
        Returns:
            Dict containing drift detection results
        """
        if self.baseline_distribution is None:
            raise ValueError("Baseline distribution not set. Call set_baseline() first.")
            
        # Perform Kolmogorov-Smirnov test for distribution drift
        drift_detected = []
        p_values = []
        
        for i in range(features.shape[1]):
            baseline = stats.norm(
                self.baseline_distribution['mean'][i],
                self.baseline_distribution['std'][i]
            ).rvs(features.shape[0])
            
            _, p_value = stats.ks_2samp(baseline, features[:, i])
            p_values.append(p_value)
            
            if p_value < self.drift_threshold:
                drift_detected.append(i)
                if raise_alert:
                    logger.warning(
                        f"Drift detected in feature {i} for {self.model_name} "
                        f"(p-value: {p_value:.3f})"
                    )
        
        return {
            'drift_detected': len(drift_detected) > 0,
            'drifted_features': drift_detected,
            'p_values': p_values,
            'timestamp': datetime.now()
        }
    
    def _calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """Calculate performance metrics.
        
        Args:
            y_true: Ground truth labels
            y_pred: Model predictions
            
        Returns:
            Dict of metric values
        """
        metrics = {}
        
        if "accuracy" in self.metrics:
            metrics['accuracy'] = accuracy_score(y_true, y_pred)
        if "precision" in self.metrics:
            metrics['precision'] = precision_score(y_true, y_pred, average='weighted')
        if "recall" in self.metrics:
            metrics['recall'] = recall_score(y_true, y_pred, average='weighted')
        if "f1" in self.metrics:
            metrics['f1'] = f1_score(y_true, y_pred, average='weighted')
            
        return metrics 