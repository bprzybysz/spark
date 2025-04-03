"""Base classes and utilities for stage implementations.

This module provides base classes and common functionality that can be
reused across different stages of the pipeline.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar, Generic
import json
import yaml

from pyspark.sql import SparkSession
from src.utility.logging import setup_logger

T = TypeVar('T')  # Generic type for stage-specific results

class StageStatus(Enum):
    """Status enum for stage execution."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class StageResult(Generic[T]):
    """Base class for stage execution results.
    
    Attributes:
        status: Execution status
        stage_name: Name of the stage
        output: Stage-specific output data
        errors: List of errors encountered
        warnings: List of warnings
        metadata: Additional metadata about execution
    """
    status: StageStatus
    stage_name: str
    output: Optional[T] = None
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values for collections."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}

class BaseStage(ABC):
    """Base class for pipeline stages.
    
    This class provides common functionality and enforces a consistent
    interface across different pipeline stages.
    """
    
    def __init__(
        self,
        name: str,
        spark: SparkSession,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the stage.
        
        Args:
            name: Stage name
            spark: Active SparkSession
            config: Optional stage configuration
        """
        self.name = name
        self.spark = spark
        self.config = config or {}
        self.logger = setup_logger(f"stage.{name}")
        
    @abstractmethod
    def validate_config(self) -> List[str]:
        """Validate stage configuration.
        
        Returns:
            List of validation error messages, empty if valid
        """
        pass
    
    @abstractmethod
    def execute(self) -> StageResult:
        """Execute the stage's main logic.
        
        Returns:
            StageResult containing execution status and output
        """
        pass
    
    def cleanup(self) -> None:
        """Clean up any resources used by the stage.
        
        This method should be overridden if the stage needs to clean up
        temporary files or other resources.
        """
        pass

class ProgressTracker:
    """Utility for tracking stage progress and updating progress.yaml."""
    
    def __init__(self, progress_file: Path):
        """Initialize the progress tracker.
        
        Args:
            progress_file: Path to progress.yaml
        """
        self.progress_file = progress_file
        self.logger = setup_logger("progress_tracker")
        
    def load_progress(self) -> Dict[str, Any]:
        """Load current progress from file.
        
        Returns:
            Dict containing progress data
        """
        try:
            with open(self.progress_file) as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load progress: {e}")
            return {"version": "1.0", "stages": {}, "components": {}}
    
    def update_stage_progress(
        self,
        stage_name: str,
        status: StageStatus,
        completion: float,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update progress for a specific stage.
        
        Args:
            stage_name: Name of the stage
            status: Current status
            completion: Completion percentage (0-100)
            details: Optional additional details
        """
        progress = self.load_progress()
        
        # Update stage info
        stage_info = {
            "status": status.value,
            "completion": completion,
            "last_updated": "2024-04-03",  # TODO: Use actual timestamp
        }
        if details:
            stage_info.update(details)
            
        # Update progress file
        if "stages" not in progress:
            progress["stages"] = {}
        progress["stages"][stage_name] = stage_info
        
        try:
            with open(self.progress_file, 'w') as f:
                yaml.dump(progress, f, default_flow_style=False)
        except Exception as e:
            self.logger.error(f"Failed to update progress: {e}")

class CodebaseManager:
    """Utility for managing codebase organization and cleanup."""
    
    def __init__(self, root_dir: Path):
        """Initialize the codebase manager.
        
        Args:
            root_dir: Project root directory
        """
        self.root_dir = root_dir
        self.logger = setup_logger("codebase_manager")
    
    def count_files(self, pattern: str = "*.py") -> int:
        """Count number of files matching pattern.
        
        Args:
            pattern: Glob pattern to match files
            
        Returns:
            Number of matching files
        """
        return len(list(self.root_dir.rglob(pattern)))
    
    def analyze_complexity(self) -> Dict[str, Any]:
        """Analyze codebase complexity metrics.
        
        Returns:
            Dict containing complexity metrics
        """
        # TODO: Implement complexity analysis
        return {}
    
    def cleanup_stage(self, stage_name: str) -> List[str]:
        """Clean up obsolete code after stage completion.
        
        Args:
            stage_name: Name of the stage to clean up
            
        Returns:
            List of files removed
        """
        # TODO: Implement stage cleanup
        return [] 