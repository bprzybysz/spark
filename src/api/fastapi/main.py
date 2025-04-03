"""
FastAPI application for model serving.

This module provides a FastAPI application for serving machine learning models.
"""
import logging
from typing import Dict, Any, List, Optional

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.core.di.container import get_container
from src.core.config.settings import get_settings
from src.ml.models.registry import ModelNotFoundError


# Create the application
app = FastAPI(
    title="ML Model Serving API",
    description="API for serving machine learning models trained with the Spark ETL ML Pipeline",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with appropriate origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get container and logger
container = get_container()
logger = container.logger_factory().get_logger(__name__)


# Input/Output models
class PredictionRequest(BaseModel):
    """Model for prediction requests."""
    
    model_name: str = Field(..., description="Name of the model to use for prediction")
    model_version: Optional[str] = Field(None, description="Version of the model (defaults to latest)")
    features: Dict[str, Any] = Field(..., description="Features for prediction")


class PredictionResponse(BaseModel):
    """Model for prediction responses."""
    
    model_name: str = Field(..., description="Name of the model used for prediction")
    model_version: str = Field(..., description="Version of the model used")
    prediction: Any = Field(..., description="Prediction result")
    probability: Optional[float] = Field(None, description="Prediction probability (if applicable)")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional prediction details")


class HealthResponse(BaseModel):
    """Model for health check responses."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class ModelsResponse(BaseModel):
    """Model for listing available models."""
    
    models: List[Dict[str, Any]] = Field(..., description="List of available models")


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return {
        "status": "ok",
        "version": settings.version,
    }


@app.get("/models", response_model=ModelsResponse, tags=["Models"])
async def list_models():
    """List available models."""
    try:
        # This is a placeholder - implement the actual model registry integration
        model_registry = container.model_registry()
        models = model_registry.list_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list models",
        )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(request: PredictionRequest):
    """Make predictions using the specified model."""
    try:
        # This is a placeholder - implement the actual model registry and inference integration
        model_registry = container.model_registry()
        model = model_registry.get_model(request.model_name, request.model_version)
        
        # Make prediction
        result = model.predict(request.features)
        
        return {
            "model_name": request.model_name,
            "model_version": model.version,
            "prediction": result.prediction,
            "probability": result.probability,
            "details": result.details,
        }
    except ModelNotFoundError as e:
        logger.error(f"Model not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model not found: {e}",
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}",
        )


def start_server():
    """Start the FastAPI server."""
    settings = get_settings()
    uvicorn.run(
        "src.api.fastapi.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
        log_level=settings.api.log_level,
        workers=settings.api.workers,
    )


if __name__ == "__main__":
    start_server() 