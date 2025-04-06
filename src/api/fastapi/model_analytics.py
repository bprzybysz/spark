"""
FastAPI endpoints for model analytics.

This module provides endpoints for accessing model analytics data and managing batch jobs.
"""
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field

from src.core.di.container import get_container
from src.stages.stage4_analytics.batch_processor import BatchProcessor
from src.stages.stage4_analytics.batch_scheduler import BatchScheduler


# Create router
router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)

# Get container
container = get_container()
logger = container.logger_factory().get_logger(__name__)


# Models
class AnalyticsJobRequest(BaseModel):
    """Model for analytics job requests."""
    
    job_id: str = Field(..., description="Unique job identifier")
    model_name: str = Field(..., description="Name of the model to analyze")
    metrics_path: str = Field(..., description="Path to metrics data")
    predictions_path: str = Field(..., description="Path to predictions data")
    frequency: str = Field("daily", description="Job frequency (hourly, daily, weekly)")
    start_time: Optional[str] = Field(None, description="When to start the job (ISO format)")
    enabled: bool = Field(True, description="Whether the job is enabled")


class AnalyticsJobResponse(BaseModel):
    """Model for analytics job responses."""
    
    job_id: str = Field(..., description="Unique job identifier")
    model_name: str = Field(..., description="Name of the model")
    status: str = Field(..., description="Job status")
    next_run: Optional[str] = Field(None, description="Next scheduled run (ISO format)")
    last_run: Optional[str] = Field(None, description="Last run time (ISO format)")


class AnalyticsBatchRunResponse(BaseModel):
    """Model for batch run responses."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Run status")
    results_path: Optional[str] = Field(None, description="Path to results")
    error: Optional[str] = Field(None, description="Error message if any")


# Dependency for scheduler
def get_scheduler() -> BatchScheduler:
    """Dependency for batch scheduler."""
    return BatchScheduler(
        output_path=container.config().get("analytics_output_path", "data/analytics"),
        logger=logger
    )


# Endpoints
@router.get("/jobs", response_model=List[AnalyticsJobResponse])
async def list_jobs(scheduler: BatchScheduler = Depends(get_scheduler)):
    """List all analytics jobs."""
    try:
        jobs = scheduler.list_jobs()
        return [
            {
                "job_id": job["job_id"],
                "model_name": job["model_name"],
                "status": job["status"],
                "next_run": job["next_run"],
                "last_run": job["last_run"],
            }
            for job in jobs
        ]
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing jobs: {str(e)}",
        )


@router.post("/jobs", response_model=AnalyticsJobResponse)
async def create_job(
    job_request: AnalyticsJobRequest,
    scheduler: BatchScheduler = Depends(get_scheduler)
):
    """Create a new analytics job."""
    try:
        job = scheduler.add_job(
            job_id=job_request.job_id,
            model_name=job_request.model_name,
            metrics_path=job_request.metrics_path,
            predictions_path=job_request.predictions_path,
            frequency=job_request.frequency,
            start_time=job_request.start_time,
            enabled=job_request.enabled,
        )
        
        return {
            "job_id": job["job_id"],
            "model_name": job["model_name"],
            "status": job["status"],
            "next_run": job["next_run"],
            "last_run": job["last_run"],
        }
    except ValueError as e:
        logger.error(f"Invalid job request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating job: {str(e)}",
        )


@router.get("/jobs/{job_id}", response_model=AnalyticsJobResponse)
async def get_job(job_id: str, scheduler: BatchScheduler = Depends(get_scheduler)):
    """Get details of a specific job."""
    try:
        jobs = scheduler.list_jobs()
        for job in jobs:
            if job["job_id"] == job_id:
                return {
                    "job_id": job["job_id"],
                    "model_name": job["model_name"],
                    "status": job["status"],
                    "next_run": job["next_run"],
                    "last_run": job["last_run"],
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting job: {str(e)}",
        )


@router.delete("/jobs/{job_id}", response_model=Dict[str, bool])
async def delete_job(job_id: str, scheduler: BatchScheduler = Depends(get_scheduler)):
    """Delete a job."""
    try:
        success = scheduler.delete_job(job_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting job: {str(e)}",
        )


@router.post("/jobs/{job_id}/run", response_model=AnalyticsBatchRunResponse)
async def run_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    scheduler: BatchScheduler = Depends(get_scheduler)
):
    """Run a job manually."""
    async def run_job_background(job_id: str, scheduler: BatchScheduler):
        try:
            scheduler.run_job(job_id)
        except Exception as e:
            logger.error(f"Background job error: {e}")
    
    try:
        # Verify job exists
        jobs = scheduler.list_jobs()
        job = None
        for j in jobs:
            if j["job_id"] == job_id:
                job = j
                break
        
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )
        
        # Schedule job to run in background
        background_tasks.add_task(run_job_background, job_id, scheduler)
        
        return {
            "job_id": job_id,
            "status": "started",
            "results_path": f"{scheduler.output_path}/{job['model_name']}_*",
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting job: {str(e)}",
        )


@router.get("/model/{model_name}/metrics", response_model=Dict[str, Any])
async def get_model_metrics(
    model_name: str,
    limit: int = 10,
    scheduler: BatchScheduler = Depends(get_scheduler)
):
    """Get latest metrics for a model."""
    try:
        import glob
        import json
        
        # Find relevant metric files
        pattern = f"{scheduler.output_path}/{model_name}_metrics_*.json"
        files = sorted(glob.glob(pattern), reverse=True)[:limit]
        
        if not files:
            return {"metrics": [], "message": "No metrics found for this model"}
        
        # Load the metrics
        metrics = []
        for file in files:
            with open(file, 'r') as f:
                data = json.load(f)
                # Add filename for reference
                data["file"] = os.path.basename(file)
                metrics.append(data)
        
        return {"metrics": metrics}
    except Exception as e:
        logger.error(f"Error retrieving metrics for {model_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving metrics: {str(e)}",
        )


@router.get("/model/{model_name}/predictions", response_model=Dict[str, Any])
async def get_model_predictions(
    model_name: str,
    limit: int = 10,
    scheduler: BatchScheduler = Depends(get_scheduler)
):
    """Get latest prediction analytics for a model."""
    try:
        import glob
        import json
        import os
        
        # Find relevant prediction files
        pattern = f"{scheduler.output_path}/{model_name}_predictions_*.json"
        files = sorted(glob.glob(pattern), reverse=True)[:limit]
        
        if not files:
            return {"predictions": [], "message": "No prediction data found for this model"}
        
        # Load the prediction data
        predictions = []
        for file in files:
            with open(file, 'r') as f:
                data = json.load(f)
                # Add filename for reference
                data["file"] = os.path.basename(file)
                predictions.append(data)
        
        return {"predictions": predictions}
    except Exception as e:
        logger.error(f"Error retrieving prediction data for {model_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving prediction data: {str(e)}",
        ) 