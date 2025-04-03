"""
TensorFlow model implementation module.

This module provides a TensorFlow implementation of the Model class.
"""
import os
from typing import Dict, Any, List, Optional, Tuple, Union, cast

import numpy as np
import tensorflow as tf
from tensorflow import keras

from src.ml.models.registry import Model, ModelMetadata, PredictionResult


class TensorFlowModel(Model[keras.Model]):
    """TensorFlow implementation of the Model class."""
    
    def __init__(
        self,
        name: str,
        version: str,
        model_impl: keras.Model,
        metadata: Optional[ModelMetadata] = None,
        preprocessor: Optional[Any] = None,
    ):
        """
        Initialize a TensorFlow model.
        
        Args:
            name: Name of the model
            version: Version of the model
            model_impl: The TensorFlow model implementation
            metadata: Optional model metadata
            preprocessor: Optional preprocessing function or transformer
        """
        super().__init__(name, version, model_impl, metadata)
        self.preprocessor = preprocessor
    
    def predict(self, features: Dict[str, Any]) -> PredictionResult:
        """
        Make a prediction using the model.
        
        Args:
            features: Dictionary of feature values
            
        Returns:
            PredictionResult: Prediction result
        """
        # Preprocess features if needed
        X = self._preprocess_features(features)
        
        # Make prediction
        raw_prediction = self.model_impl.predict(X, verbose=0)
        
        # Process prediction based on model type
        prediction, probability = self._process_prediction(raw_prediction)
        
        return PredictionResult(
            prediction=prediction,
            probability=probability,
            details={"features": features},
        )
    
    def _preprocess_features(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Preprocess features for the model.
        
        Args:
            features: Dictionary of feature values
            
        Returns:
            np.ndarray: Preprocessed features
        """
        # If we have a preprocessor, use it
        if self.preprocessor is not None:
            # This is a simplified example; in a real implementation,
            # you would handle different types of preprocessors
            return self.preprocessor(features)
        
        # Otherwise, just convert to numpy array
        feature_list = []
        if self.metadata and self.metadata.features:
            # If we have metadata with feature names, use them to order features
            for feature_name in self.metadata.features:
                if feature_name in features:
                    feature_list.append(features[feature_name])
                else:
                    raise ValueError(f"Missing feature: {feature_name}")
        else:
            # Otherwise, just use all features
            feature_list = list(features.values())
        
        # Convert to numpy array
        X = np.array([feature_list])
        
        return X
    
    def _process_prediction(
        self,
        raw_prediction: np.ndarray,
    ) -> Tuple[Union[float, int, str, List[Any]], Optional[float]]:
        """
        Process raw prediction to get prediction and probability.
        
        Args:
            raw_prediction: Raw prediction from the model
            
        Returns:
            Tuple[Any, Optional[float]]: Prediction and probability
        """
        # Get output shape to determine model type
        output_shape = raw_prediction.shape
        
        # Get the last layer activation function
        try:
            last_layer = self.model_impl.layers[-1]
            activation = last_layer.activation.__name__ if hasattr(last_layer, 'activation') else None
        except (IndexError, AttributeError):
            activation = None
        
        # Binary classification
        if output_shape[1] == 1 and activation in ['sigmoid', None]:
            probability = float(raw_prediction[0][0])
            prediction = 1 if probability >= 0.5 else 0
            return prediction, probability
        
        # Multi-class classification
        elif output_shape[1] > 1 and activation in ['softmax', None]:
            probabilities = raw_prediction[0]
            prediction_idx = int(np.argmax(probabilities))
            probability = float(probabilities[prediction_idx])
            return prediction_idx, probability
        
        # Regression
        else:
            prediction = float(raw_prediction[0][0])
            return prediction, None
    
    @classmethod
    def load(
        cls,
        model_path: str,
        name: str,
        version: str,
        metadata: Optional[ModelMetadata] = None,
        preprocessor_path: Optional[str] = None,
    ) -> "TensorFlowModel":
        """
        Load a TensorFlow model from disk.
        
        Args:
            model_path: Path to the saved model
            name: Name of the model
            version: Version of the model
            metadata: Optional model metadata
            preprocessor_path: Optional path to the saved preprocessor
            
        Returns:
            TensorFlowModel: Loaded model
        """
        # Load the TensorFlow model
        model_impl = keras.models.load_model(model_path)
        
        # Load preprocessor if specified
        preprocessor = None
        if preprocessor_path and os.path.exists(preprocessor_path):
            # In a real implementation, you would load the preprocessor
            # based on its type (e.g., scikit-learn, TensorFlow, etc.)
            pass
        
        return cls(
            name=name,
            version=version,
            model_impl=model_impl,
            metadata=metadata,
            preprocessor=preprocessor,
        )
    
    def save(self, model_dir: str, save_preprocessor: bool = True) -> None:
        """
        Save the model to disk.
        
        Args:
            model_dir: Directory to save the model
            save_preprocessor: Whether to save the preprocessor
        """
        os.makedirs(model_dir, exist_ok=True)
        
        # Save the TensorFlow model
        model_path = os.path.join(model_dir, "model")
        self.model_impl.save(model_path)
        
        # Save preprocessor if specified
        if save_preprocessor and self.preprocessor is not None:
            # In a real implementation, you would save the preprocessor
            # based on its type (e.g., scikit-learn, TensorFlow, etc.)
            pass
        
        # Save metadata if available
        if self.metadata:
            metadata_path = os.path.join(model_dir, "metadata.json")
            with open(metadata_path, "w") as f:
                import json
                json.dump(self.metadata.model_dump(), f, default=str, indent=2) 