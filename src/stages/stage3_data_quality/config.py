"""
Configuration module for Stage 3 Data Quality

This module defines the configuration settings and validation rules for the data quality checks.
"""

from typing import Dict, List, Optional

class DataQualityConfig:
    """Configuration class for data quality settings and rules."""
    
    def __init__(self):
        self.default_config = {
            'required_columns': [],  # List of columns that must be complete
            'expected_types': {},    # Dictionary of column name to expected type
            'numeric_columns': [],   # List of columns to check for anomalies
            'anomaly_threshold': 3.0,  # Z-score threshold for anomaly detection
            'quality_thresholds': {
                'completeness': 0.95,  # Minimum completeness ratio
                'uniqueness': 0.01,    # Minimum uniqueness ratio
                'consistency': 0.99,   # Minimum consistency ratio
            }
        }
    
    def create_config(self, 
                     required_columns: Optional[List[str]] = None,
                     expected_types: Optional[Dict[str, str]] = None,
                     numeric_columns: Optional[List[str]] = None,
                     anomaly_threshold: Optional[float] = None,
                     quality_thresholds: Optional[Dict[str, float]] = None) -> Dict:
        """
        Create a configuration dictionary with custom settings.
        
        Args:
            required_columns: List of columns that must be complete
            expected_types: Dictionary mapping column names to expected types
            numeric_columns: List of numerical columns for anomaly detection
            anomaly_threshold: Z-score threshold for anomaly detection
            quality_thresholds: Dictionary of quality metric thresholds
            
        Returns:
            Configuration dictionary with specified settings
        """
        config = self.default_config.copy()
        
        if required_columns is not None:
            config['required_columns'] = required_columns
            
        if expected_types is not None:
            config['expected_types'] = expected_types
            
        if numeric_columns is not None:
            config['numeric_columns'] = numeric_columns
            
        if anomaly_threshold is not None:
            config['anomaly_threshold'] = anomaly_threshold
            
        if quality_thresholds is not None:
            config['quality_thresholds'].update(quality_thresholds)
            
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
            'required_columns',
            'expected_types',
            'numeric_columns',
            'anomaly_threshold',
            'quality_thresholds'
        ]
        
        # Check if all required keys are present
        if not all(key in config for key in required_keys):
            return False
            
        # Validate types
        if not isinstance(config['required_columns'], list):
            return False
            
        if not isinstance(config['expected_types'], dict):
            return False
            
        if not isinstance(config['numeric_columns'], list):
            return False
            
        if not isinstance(config['anomaly_threshold'], (int, float)):
            return False
            
        if not isinstance(config['quality_thresholds'], dict):
            return False
            
        # Validate threshold values
        for threshold in config['quality_thresholds'].values():
            if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
                return False
                
        return True 