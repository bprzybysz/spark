"""
Batch scheduler for analytics pipeline

This module provides the BatchScheduler class for scheduling and managing analytics batch jobs.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

from src.stages.stage4_analytics.batch_processor import BatchProcessor
from src.core.logging.logger import Logger


class BatchScheduler:
    """Class for scheduling and managing analytics batch jobs."""
    
    def __init__(
        self,
        output_path: str = "data/analytics",
        schedule_file: str = "data/analytics/schedule.json",
        logger: Optional[Logger] = None
    ):
        """
        Initialize the BatchScheduler.
        
        Args:
            output_path: Path to save batch results
            schedule_file: Path to schedule configuration file
            logger: Optional logger instance
        """
        self.output_path = output_path
        self.schedule_file = schedule_file
        self.logger = logger
        self.processor = BatchProcessor(output_path=output_path, logger=logger)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(schedule_file), exist_ok=True)
        
        # Initialize or load schedule
        if os.path.exists(schedule_file):
            with open(schedule_file, 'r') as f:
                self.schedule = json.load(f)
        else:
            self.schedule = {
                "jobs": [],
                "last_updated": datetime.now().isoformat()
            }
            self._save_schedule()
    
    def _log(self, message: str, level: str = "info"):
        """Log a message if logger is available."""
        if self.logger:
            if level == "info":
                self.logger.info(message)
            elif level == "error":
                self.logger.error(message)
            elif level == "warning":
                self.logger.warning(message)
        else:
            print(f"[{level.upper()}] {message}")
    
    def _save_schedule(self):
        """Save the current schedule to disk."""
        self.schedule["last_updated"] = datetime.now().isoformat()
        with open(self.schedule_file, 'w') as f:
            json.dump(self.schedule, f, indent=2)
    
    def add_job(
        self,
        job_id: str,
        model_name: str,
        metrics_path: str,
        predictions_path: str,
        frequency: str = "daily",
        start_time: Optional[str] = None,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Add a new batch job to the schedule.
        
        Args:
            job_id: Unique identifier for the job
            model_name: Name of the model to analyze
            metrics_path: Path to metrics data
            predictions_path: Path to predictions data
            frequency: Job frequency (hourly, daily, weekly)
            start_time: When to start the job (ISO format)
            enabled: Whether the job is enabled
            
        Returns:
            Dictionary representing the added job
        """
        # Validate job ID uniqueness
        for job in self.schedule["jobs"]:
            if job["job_id"] == job_id:
                raise ValueError(f"Job with ID {job_id} already exists")
        
        # Set default start time to now if not provided
        if start_time is None:
            start_time = datetime.now().isoformat()
        
        # Create the job
        job = {
            "job_id": job_id,
            "model_name": model_name,
            "metrics_path": metrics_path,
            "predictions_path": predictions_path,
            "frequency": frequency,
            "start_time": start_time,
            "enabled": enabled,
            "last_run": None,
            "next_run": start_time,
            "status": "scheduled",
            "run_history": []
        }
        
        # Add job to schedule
        self.schedule["jobs"].append(job)
        self._save_schedule()
        
        self._log(f"Added job {job_id} for model {model_name} with {frequency} frequency")
        return job
    
    def update_job(
        self,
        job_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing batch job.
        
        Args:
            job_id: ID of job to update
            **kwargs: Job attributes to update
            
        Returns:
            Updated job dictionary
        """
        # Find the job
        job_index = None
        for i, job in enumerate(self.schedule["jobs"]):
            if job["job_id"] == job_id:
                job_index = i
                break
        
        if job_index is None:
            raise ValueError(f"Job with ID {job_id} not found")
        
        # Update job attributes
        job = self.schedule["jobs"][job_index]
        
        # Don't allow updating certain fields
        restricted_fields = ["job_id", "last_run", "run_history"]
        for field in restricted_fields:
            if field in kwargs:
                self._log(f"Cannot update field {field}", "warning")
                kwargs.pop(field)
        
        # Update remaining fields
        for key, value in kwargs.items():
            if key in job:
                job[key] = value
        
        # Update next_run if frequency changed
        if "frequency" in kwargs or "start_time" in kwargs:
            job["next_run"] = self._calculate_next_run(job)
        
        self._save_schedule()
        self._log(f"Updated job {job_id}")
        
        return job
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job from the schedule.
        
        Args:
            job_id: ID of job to delete
            
        Returns:
            True if job was deleted, False otherwise
        """
        initial_count = len(self.schedule["jobs"])
        self.schedule["jobs"] = [job for job in self.schedule["jobs"] if job["job_id"] != job_id]
        
        if len(self.schedule["jobs"]) < initial_count:
            self._save_schedule()
            self._log(f"Deleted job {job_id}")
            return True
        else:
            self._log(f"Job {job_id} not found", "warning")
            return False
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """
        List all scheduled jobs.
        
        Returns:
            List of job dictionaries
        """
        return self.schedule["jobs"]
    
    def _calculate_next_run(self, job: Dict[str, Any]) -> str:
        """
        Calculate the next run time for a job.
        
        Args:
            job: Job dictionary
            
        Returns:
            ISO formatted datetime string for next run
        """
        if not job["enabled"]:
            return None
        
        # If job has never run, use start_time
        if job["last_run"] is None:
            return job["start_time"]
        
        # Otherwise calculate based on frequency
        last_run = datetime.fromisoformat(job["last_run"])
        
        if job["frequency"] == "hourly":
            next_run = last_run + timedelta(hours=1)
        elif job["frequency"] == "daily":
            next_run = last_run + timedelta(days=1)
        elif job["frequency"] == "weekly":
            next_run = last_run + timedelta(weeks=1)
        else:
            # Default to daily
            next_run = last_run + timedelta(days=1)
        
        return next_run.isoformat()
    
    def _update_job_status(self, job: Dict[str, Any], status: str, results: Optional[Dict] = None):
        """
        Update job status and history.
        
        Args:
            job: Job dictionary
            status: New status
            results: Optional job results
        """
        job["status"] = status
        job["last_run"] = datetime.now().isoformat()
        job["next_run"] = self._calculate_next_run(job)
        
        # Add to history
        history_entry = {
            "run_time": job["last_run"],
            "status": status
        }
        
        if results:
            # Store summary of results
            history_entry["metrics_processed"] = "metrics" in results
            history_entry["predictions_processed"] = "predictions" in results
            
            if "metrics_error" in results:
                history_entry["metrics_error"] = results["metrics_error"]
            
            if "predictions_error" in results:
                history_entry["predictions_error"] = results["predictions_error"]
        
        # Keep history limited to last 10 entries
        job["run_history"].append(history_entry)
        if len(job["run_history"]) > 10:
            job["run_history"] = job["run_history"][-10:]
        
        self._save_schedule()
    
    def run_job(self, job_id: str) -> Dict[str, Any]:
        """
        Run a specific job.
        
        Args:
            job_id: ID of job to run
            
        Returns:
            Job results dictionary
        """
        # Find the job
        job = None
        for j in self.schedule["jobs"]:
            if j["job_id"] == job_id:
                job = j
                break
        
        if job is None:
            raise ValueError(f"Job with ID {job_id} not found")
        
        # Update status to running
        self._update_job_status(job, "running")
        self._log(f"Running job {job_id} for model {job['model_name']}")
        
        try:
            # Run the job
            results = self.processor.run_batch_job(
                metrics_path=job["metrics_path"],
                predictions_path=job["predictions_path"],
                model_name=job["model_name"]
            )
            
            # Update job status on completion
            self._update_job_status(job, "completed", results)
            self._log(f"Job {job_id} completed successfully")
            
            return results
            
        except Exception as e:
            # Update job status on error
            self._log(f"Error running job {job_id}: {str(e)}", "error")
            self._update_job_status(job, "failed", {"error": str(e)})
            raise
    
    def run_due_jobs(self) -> List[Dict[str, Any]]:
        """
        Run all jobs that are due.
        
        Returns:
            List of results for each job run
        """
        now = datetime.now()
        results = []
        
        for job in self.schedule["jobs"]:
            if not job["enabled"] or job["next_run"] is None:
                continue
            
            next_run = datetime.fromisoformat(job["next_run"])
            if next_run <= now and job["status"] != "running":
                try:
                    job_result = self.run_job(job["job_id"])
                    results.append({
                        "job_id": job["job_id"],
                        "model_name": job["model_name"],
                        "status": "completed",
                        "results": job_result
                    })
                except Exception as e:
                    results.append({
                        "job_id": job["job_id"],
                        "model_name": job["model_name"],
                        "status": "failed",
                        "error": str(e)
                    })
        
        return results
    
    def start_scheduler(self, interval_seconds: int = 300, max_runs: Optional[int] = None):
        """
        Start the scheduler loop.
        
        Args:
            interval_seconds: Interval in seconds between schedule checks
            max_runs: Maximum number of schedule runs (None for infinite)
        """
        self._log(f"Starting scheduler with {interval_seconds}s interval")
        run_count = 0
        
        try:
            while max_runs is None or run_count < max_runs:
                self._log(f"Checking for due jobs (run {run_count + 1})")
                results = self.run_due_jobs()
                
                if results:
                    self._log(f"Ran {len(results)} jobs")
                
                run_count += 1
                
                if max_runs is None or run_count < max_runs:
                    time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            self._log("Scheduler stopped by user")
        
        self._log("Scheduler stopped") 