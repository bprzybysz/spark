"""
Model registry module.

This module provides a registry for managing machine learning models.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Generic, TypeVar

from pydantic import BaseModel, Field


class ModelNotFoundError(Exception):
    """Exception raised when a model is not found in the registry."""
    pass


class ModelMetadata(BaseModel):
    """Metadata for a machine learning model."""
    
    name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version of the model")
    description: Optional[str] = Field(None, description="Description of the model")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    framework: str = Field(..., description="ML framework used (e.g., 'tensorflow', 'sklearn')")
    tags: List[str] = Field(default_factory=list, description="Tags for the model")
    metrics: Dict[str, float] = Field(default_factory=dict, description="Model performance metrics")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model hyperparameters")
    features: List[str] = Field(default_factory=list, description="Features used by the model")
    target: Optional[str] = Field(None, description="Target variable")
    path: str = Field(..., description="Path to the model files")
    

class PredictionResult(BaseModel):
    """Result of a model prediction."""
    
    prediction: Any = Field(..., description="Prediction value")
    probability: Optional[float] = Field(None, description="Prediction probability if applicable")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional prediction details")


# Type variable for the model implementation
T = TypeVar("T")


class Model(Generic[T]):
    """
    Base class for machine learning models.
    
    This class wraps the actual model implementation and provides a consistent
    interface for working with models regardless of the underlying framework.
    """
    
    def __init__(
        self,
        name: str,
        version: str,
        model_impl: T,
        metadata: Optional[ModelMetadata] = None,
    ):
        """
        Initialize a model.
        
        Args:
            name: Name of the model
            version: Version of the model
            model_impl: The actual model implementation
            metadata: Optional model metadata
        """
        self.name = name
        self.version = version
        self.model_impl = model_impl
        self.metadata = metadata
    
    def predict(self, features: Dict[str, Any]) -> PredictionResult:
        """
        Make a prediction using the model.
        
        Args:
            features: Dictionary of feature values
            
        Returns:
            PredictionResult: Prediction result
        """
        raise NotImplementedError("Subclasses must implement predict")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        result = {
            "name": self.name,
            "version": self.version,
        }
        
        if self.metadata:
            result["metadata"] = self.metadata.model_dump()
        
        return result


class ModelRegistry:
    """Registry for managing machine learning models."""
    
    def __init__(self, models_dir: str = "./models"):
        """
        Initialize the model registry.
        
        Args:
            models_dir: Directory where models are stored
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self._models: Dict[str, Dict[str, Model]] = {}
        self._load_models()
    
    def _load_models(self) -> None:
        """Load models from the registry directory."""
        # This is just a placeholder. In a real implementation, this would
        # scan the models directory and load the models.
        pass
    
    def register_model(
        self,
        model: Model,
        metadata: Optional[ModelMetadata] = None,
    ) -> None:
        """
        Register a model with the registry.
        
        Args:
            model: The model to register
            metadata: Optional metadata for the model
        """
        name = model.name
        version = model.version
        
        # Create model directory if it doesn't exist
        model_dir = self.models_dir / name / version
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metadata if provided
        if metadata:
            metadata_path = model_dir / "metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata.model_dump(), f, default=str, indent=2)
        
        # Add model to registry
        if name not in self._models:
            self._models[name] = {}
        
        self._models[name][version] = model
    
    def get_model(
        self,
        name: str,
        version: Optional[str] = None,
    ) -> Model:
        """
        Get a model from the registry.
        
        Args:
            name: Name of the model
            version: Version of the model (defaults to latest)
            
        Returns:
            Model: The requested model
            
        Raises:
            ModelNotFoundError: If the model is not found
        """
        if name not in self._models:
            raise ModelNotFoundError(f"Model '{name}' not found")
        
        if version is None:
            # Get the latest version
            versions = sorted(self._models[name].keys())
            if not versions:
                raise ModelNotFoundError(f"No versions found for model '{name}'")
            
            version = versions[-1]
        
        if version not in self._models[name]:
            raise ModelNotFoundError(f"Version '{version}' not found for model '{name}'")
        
        return self._models[name][version]
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all models in the registry.
        
        Returns:
            List[Dict[str, Any]]: List of models with their metadata
        """
        result = []
        
        for name, versions in self._models.items():
            for version, model in versions.items():
                result.append(model.to_dict())
        
        return result
    
    def delete_model(self, name: str, version: Optional[str] = None) -> None:
        """
        Delete a model from the registry.
        
        Args:
            name: Name of the model
            version: Version of the model (if None, delete all versions)
            
        Raises:
            ModelNotFoundError: If the model is not found
        """
        if name not in self._models:
            raise ModelNotFoundError(f"Model '{name}' not found")
        
        if version is None:
            # Delete all versions
            del self._models[name]
            
            # Delete model directory
            model_dir = self.models_dir / name
            if model_dir.exists():
                import shutil
                shutil.rmtree(model_dir)
        else:
            if version not in self._models[name]:
                raise ModelNotFoundError(f"Version '{version}' not found for model '{name}'")
            
            # Delete specific version
            del self._models[name][version]
            
            # Delete version directory
            version_dir = self.models_dir / name / version
            if version_dir.exists():
                import shutil
                shutil.rmtree(version_dir)
            
            # Remove model if no versions left
            if not self._models[name]:
                del self._models[name]


# Singleton registry instance
_registry: Optional[ModelRegistry] = None


def get_registry(models_dir: Optional[str] = None) -> ModelRegistry:
    """
    Get the model registry instance.
    
    Args:
        models_dir: Optional directory where models are stored
        
    Returns:
        ModelRegistry: The model registry instance
    """
    global _registry
    
    if _registry is None:
        _registry = ModelRegistry(models_dir=models_dir or "./models")
    
    return _registry 