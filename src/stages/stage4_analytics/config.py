"""
Configuration module for Stage 4 Analytics

This module defines the configuration settings and validation rules for the analytics operations.
"""

from typing import Dict, List, Optional, Union

class AnalyticsConfig:
    """Configuration class for analytics settings and rules."""
    
    def __init__(self):
        self.default_config = {
            'numeric_columns': [],           # Columns for summary statistics
            'correlation_columns': [],       # Columns for correlation analysis
            'correlation_method': 'pearson', # Correlation method
            'group_columns': [],            # Columns to group by
            'agg_columns': [],              # Columns to aggregate
            'agg_functions': [              # Aggregation functions to apply
                'count',
                'avg',
                'stddev'
            ],
            'time_column': None,            # Column containing timestamps
            'metric_columns': [],           # Columns for time series analysis
            'window_size': 7,               # Window size for time series
            'outlier_columns': [],          # Columns for outlier detection
            'outlier_method': 'iqr',        # Outlier detection method
            'outlier_threshold': 1.5        # Threshold for outlier detection
        }
    
    def create_config(self,
                     numeric_columns: Optional[List[str]] = None,
                     correlation_columns: Optional[List[str]] = None,
                     correlation_method: Optional[str] = None,
                     group_columns: Optional[List[str]] = None,
                     agg_columns: Optional[List[str]] = None,
                     agg_functions: Optional[List[str]] = None,
                     time_column: Optional[str] = None,
                     metric_columns: Optional[List[str]] = None,
                     window_size: Optional[int] = None,
                     outlier_columns: Optional[List[str]] = None,
                     outlier_method: Optional[str] = None,
                     outlier_threshold: Optional[float] = None) -> Dict:
        """
        Create a configuration dictionary with custom settings.
        
        Args:
            numeric_columns: Columns for summary statistics
            correlation_columns: Columns for correlation analysis
            correlation_method: Correlation method
            group_columns: Columns to group by
            agg_columns: Columns to aggregate
            agg_functions: Aggregation functions to apply
            time_column: Column containing timestamps
            metric_columns: Columns for time series analysis
            window_size: Window size for time series
            outlier_columns: Columns for outlier detection
            outlier_method: Outlier detection method
            outlier_threshold: Threshold for outlier detection
            
        Returns:
            Configuration dictionary with specified settings
        """
        config = self.default_config.copy()
        
        if numeric_columns is not None:
            config['numeric_columns'] = numeric_columns
            
        if correlation_columns is not None:
            config['correlation_columns'] = correlation_columns
            
        if correlation_method is not None:
            config['correlation_method'] = correlation_method
            
        if group_columns is not None:
            config['group_columns'] = group_columns
            
        if agg_columns is not None:
            config['agg_columns'] = agg_columns
            
        if agg_functions is not None:
            config['agg_functions'] = agg_functions
            
        if time_column is not None:
            config['time_column'] = time_column
            
        if metric_columns is not None:
            config['metric_columns'] = metric_columns
            
        if window_size is not None:
            config['window_size'] = window_size
            
        if outlier_columns is not None:
            config['outlier_columns'] = outlier_columns
            
        if outlier_method is not None:
            config['outlier_method'] = outlier_method
            
        if outlier_threshold is not None:
            config['outlier_threshold'] = outlier_threshold
            
        return config
    
    def validate_config(self, config: Dict) -> bool:
        """
        Validate the configuration dictionary.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        required_keys = [
            'numeric_columns',
            'correlation_columns',
            'correlation_method',
            'group_columns',
            'agg_columns',
            'agg_functions',
            'time_column',
            'metric_columns',
            'window_size',
            'outlier_columns',
            'outlier_method',
            'outlier_threshold'
        ]
        
        # Check if all required keys are present
        if not all(key in config for key in required_keys):
            return False
        
        # Validate types
        if not isinstance(config['numeric_columns'], list):
            return False
            
        if not isinstance(config['correlation_columns'], list):
            return False
            
        if not isinstance(config['correlation_method'], str):
            return False
            
        if not isinstance(config['group_columns'], list):
            return False
            
        if not isinstance(config['agg_columns'], list):
            return False
            
        if not isinstance(config['agg_functions'], list):
            return False
            
        if config['time_column'] is not None and not isinstance(config['time_column'], str):
            return False
            
        if not isinstance(config['metric_columns'], list):
            return False
            
        if not isinstance(config['window_size'], int):
            return False
            
        if not isinstance(config['outlier_columns'], list):
            return False
            
        if not isinstance(config['outlier_method'], str):
            return False
            
        if not isinstance(config['outlier_threshold'], (int, float)):
            return False
            
        # Validate values
        valid_correlation_methods = ['pearson', 'spearman']
        if config['correlation_method'] not in valid_correlation_methods:
            return False
            
        valid_agg_functions = ['count', 'sum', 'avg', 'min', 'max', 'stddev']
        if not all(func in valid_agg_functions for func in config['agg_functions']):
            return False
            
        if config['window_size'] < 1:
            return False
            
        valid_outlier_methods = ['iqr', 'zscore']
        if config['outlier_method'] not in valid_outlier_methods:
            return False
            
        if config['outlier_threshold'] <= 0:
            return False
            
        return True 