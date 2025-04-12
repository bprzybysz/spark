"""Visualization utilities for model monitoring results."""

from typing import List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

class MonitoringDashboard:
    """Creates visualizations for monitoring results."""
    
    def __init__(self, figure_size: tuple = (12, 8)):
        """Initialize dashboard settings.
        
        Args:
            figure_size: Default size for figures (width, height)
        """
        self.figure_size = figure_size
        # Use default style instead of seaborn
        plt.style.use('default')
        # Apply some common styling
        plt.rcParams['figure.figsize'] = figure_size
        plt.rcParams['axes.grid'] = True
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.right'] = False
    
    def plot_metric_history(
        self,
        history: List[Dict[str, Any]],
        metrics: List[str] = None,
        title: str = "Model Performance History"
    ) -> None:
        """Plot historical metrics.
        
        Args:
            history: List of performance history records
            metrics: Specific metrics to plot (default: all)
            title: Plot title
        """
        df = pd.DataFrame([
            {
                'timestamp': record['timestamp'],
                **record['metrics']
            }
            for record in history
        ])
        
        metrics = metrics or df.columns.difference(['timestamp']).tolist()
        
        plt.figure(figsize=self.figure_size)
        for metric in metrics:
            plt.plot(df['timestamp'], df[metric], marker='o', label=metric)
            
        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Metric Value')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
    
    def plot_drift_heatmap(
        self,
        drift_results: List[Dict[str, Any]],
        feature_names: List[str] = None,
        title: str = "Feature Drift Detection Heatmap"
    ) -> None:
        """Plot feature drift detection results as a heatmap.
        
        Args:
            drift_results: List of drift detection results
            feature_names: Names of features (default: indices)
            title: Plot title
        """
        # Extract p-values and timestamps
        data = []
        for result in drift_results:
            data.append({
                'timestamp': result['timestamp'],
                **{f'feature_{i}': p for i, p in enumerate(result['p_values'])}
            })
        
        df = pd.DataFrame(data)
        feature_cols = [col for col in df.columns if col.startswith('feature_')]
        
        if feature_names:
            df.rename(columns=dict(zip(feature_cols, feature_names)), inplace=True)
            feature_cols = feature_names
        
        plt.figure(figsize=self.figure_size)
        sns.heatmap(
            df[feature_cols].T,
            cmap='RdYlGn_r',
            center=0.05,
            vmin=0,
            vmax=0.1,
            cbar_kws={'label': 'p-value'}
        )
        
        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Feature')
        plt.tight_layout()
    
    def plot_alert_summary(
        self,
        history: List[Dict[str, Any]],
        title: str = "Alert History Summary"
    ) -> None:
        """Plot alert history summary.
        
        Args:
            history: List of performance history records
            title: Plot title
        """
        alert_counts = []
        timestamps = []
        
        for record in history:
            alert_counts.append(len(record['alerts']))
            timestamps.append(record['timestamp'])
        
        plt.figure(figsize=self.figure_size)
        plt.bar(timestamps, alert_counts, color='red', alpha=0.6)
        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Number of Alerts')
        plt.grid(True, axis='y')
        plt.xticks(rotation=45)
        plt.tight_layout()
    
    def plot_performance_comparison(
        self,
        current: Dict[str, float],
        baseline: Dict[str, float],
        title: str = "Performance Comparison"
    ) -> None:
        """Plot current vs baseline performance comparison.
        
        Args:
            current: Current metric values
            baseline: Baseline metric values
            title: Plot title
        """
        metrics = list(current.keys())
        x = range(len(metrics))
        
        plt.figure(figsize=self.figure_size)
        width = 0.35
        
        plt.bar([i - width/2 for i in x], [baseline[m] for m in metrics],
                width, label='Baseline', color='blue', alpha=0.6)
        plt.bar([i + width/2 for i in x], [current[m] for m in metrics],
                width, label='Current', color='red', alpha=0.6)
        
        plt.title(title)
        plt.xlabel('Metrics')
        plt.ylabel('Value')
        plt.xticks(x, metrics)
        plt.legend()
        plt.grid(True, axis='y')
        plt.tight_layout() 