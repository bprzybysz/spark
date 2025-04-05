"""Data quality dashboard configuration and metrics."""

from typing import Dict, List, Optional, Union
import json
from datetime import datetime
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, sum, when, desc

class DataQualityDashboard:
    """Dashboard for monitoring data quality metrics."""
    
    def __init__(self, metrics_path: str = "/tmp/data_quality_metrics"):
        """Initialize the dashboard.
        
        Args:
            metrics_path: Path to store metrics
        """
        self.metrics_path = metrics_path
        
    def calculate_completeness_metrics(
        self, df: DataFrame, columns: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """Calculate completeness metrics for specified columns.
        
        Args:
            df: Input DataFrame
            columns: List of columns to check, if None check all columns
            
        Returns:
            Dictionary of completeness metrics
        """
        if columns is None:
            columns = df.columns
            
        total_rows = df.count()
        metrics = {}
        
        for col_name in columns:
            non_null_count = df.filter(col(col_name).isNotNull()).count()
            metrics[f"{col_name}_completeness"] = non_null_count / total_rows
            
        return metrics
    
    def calculate_validity_metrics(
        self, df: DataFrame, rules: Dict[str, Dict[str, Union[str, List[str]]]]
    ) -> Dict[str, float]:
        """Calculate validity metrics based on rules.
        
        Args:
            df: Input DataFrame
            rules: Dictionary of validation rules
            
        Returns:
            Dictionary of validity metrics
        """
        metrics = {}
        total_rows = df.count()
        
        for col_name, rule in rules.items():
            rule_type = rule.get("type")
            valid_count = 0
            
            if rule_type == "range":
                min_val = rule.get("min")
                max_val = rule.get("max")
                valid_count = df.filter(
                    (col(col_name) >= min_val) & 
                    (col(col_name) <= max_val)
                ).count()
            
            elif rule_type == "regex":
                pattern = rule.get("pattern")
                valid_count = df.filter(
                    col(col_name).rlike(pattern)
                ).count()
            
            elif rule_type == "categorical":
                valid_values = rule.get("values", [])
                valid_count = df.filter(
                    col(col_name).isin(valid_values)
                ).count()
            
            metrics[f"{col_name}_validity"] = valid_count / total_rows
            
        return metrics
    
    def calculate_consistency_metrics(
        self, df: DataFrame, consistency_rules: List[Dict[str, str]]
    ) -> Dict[str, float]:
        """Calculate consistency metrics between columns.
        
        Args:
            df: Input DataFrame
            consistency_rules: List of consistency rules
            
        Returns:
            Dictionary of consistency metrics
        """
        metrics = {}
        total_rows = df.count()
        
        for rule in consistency_rules:
            rule_name = rule.get("name")
            condition = rule.get("condition")
            
            consistent_count = df.filter(condition).count()
            metrics[f"{rule_name}_consistency"] = consistent_count / total_rows
            
        return metrics
    
    def calculate_timeliness_metrics(
        self, df: DataFrame, timestamp_col: str, sla_hours: float = 24.0
    ) -> Dict[str, float]:
        """Calculate timeliness metrics for data freshness.
        
        Args:
            df: Input DataFrame
            timestamp_col: Column containing timestamps
            sla_hours: Expected freshness in hours
            
        Returns:
            Dictionary of timeliness metrics
        """
        current_time = datetime.now()
        
        # Calculate age of records
        df_with_age = df.withColumn(
            "age_hours",
            (current_time.timestamp() - col(timestamp_col).cast("timestamp").cast("long")) / 3600
        )
        
        # Calculate metrics
        metrics = {
            "freshness_rate": df_with_age.filter(
                col("age_hours") <= sla_hours
            ).count() / df.count(),
            "average_age_hours": df_with_age.select("age_hours").mean()[0],
            "max_age_hours": df_with_age.select("age_hours").max()[0]
        }
        
        return metrics
    
    def generate_dashboard_metrics(
        self,
        df: DataFrame,
        columns: Optional[List[str]] = None,
        validation_rules: Optional[Dict[str, Dict[str, Union[str, List[str]]]]] = None,
        consistency_rules: Optional[List[Dict[str, str]]] = None,
        timestamp_col: Optional[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """Generate comprehensive dashboard metrics.
        
        Args:
            df: Input DataFrame
            columns: List of columns to check
            validation_rules: Dictionary of validation rules
            consistency_rules: List of consistency rules
            timestamp_col: Column containing timestamps
            
        Returns:
            Dictionary of all metrics
        """
        metrics = {
            "completeness": self.calculate_completeness_metrics(df, columns),
            "row_count": df.count(),
            "column_count": len(df.columns)
        }
        
        if validation_rules:
            metrics["validity"] = self.calculate_validity_metrics(df, validation_rules)
            
        if consistency_rules:
            metrics["consistency"] = self.calculate_consistency_metrics(
                df, consistency_rules
            )
            
        if timestamp_col:
            metrics["timeliness"] = self.calculate_timeliness_metrics(
                df, timestamp_col
            )
            
        return metrics
    
    def save_metrics(self, metrics: Dict[str, Dict[str, float]]) -> None:
        """Save metrics to storage.
        
        Args:
            metrics: Dictionary of metrics to save
        """
        timestamp = datetime.now().isoformat()
        metrics["timestamp"] = timestamp
        
        with open(f"{self.metrics_path}/{timestamp}.json", "w") as f:
            json.dump(metrics, f, indent=2)
    
    def load_metrics_history(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[Dict[str, Dict[str, float]]]:
        """Load historical metrics.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of historical metrics
        """
        import glob
        import os
        
        metrics_files = glob.glob(f"{self.metrics_path}/*.json")
        metrics_history = []
        
        for file_path in metrics_files:
            with open(file_path, "r") as f:
                metrics = json.load(f)
                
            if start_date and metrics["timestamp"] < start_date:
                continue
            if end_date and metrics["timestamp"] > end_date:
                continue
                
            metrics_history.append(metrics)
            
        return sorted(metrics_history, key=lambda x: x["timestamp"]) 