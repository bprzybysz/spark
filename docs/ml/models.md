# Machine Learning Models

This document describes the machine learning model architecture and implementation details.

## Model Registry

The project uses a centralized model registry to manage all machine learning models. The registry handles model versioning, metadata, and lifecycle management.

### Model Metadata

Each model in the registry includes the following metadata:

```python
{
    "name": "string",              # Name of the model
    "version": "string",           # Version of the model
    "description": "string",       # Optional description
    "created_at": "datetime",      # Creation timestamp
    "framework": "string",         # ML framework used (e.g., 'tensorflow', 'sklearn')
    "tags": ["string"],           # Tags for the model
    "metrics": {                   # Model performance metrics
        "metric_name": "float"
    },
    "parameters": {                # Model hyperparameters
        "param_name": "any"
    },
    "features": ["string"],       # Features used by the model
    "target": "string",           # Target variable
    "path": "string"              # Path to model files
}
```

## TensorFlow Model Implementation

The project includes a TensorFlow-based model implementation with the following features:

### Model Types Support

- Binary Classification
  - Single output node with sigmoid activation
  - Outputs prediction (0/1) and probability

- Multi-class Classification
  - Multiple output nodes with softmax activation
  - Outputs class index and probability

- Regression
  - Single output node with linear activation
  - Outputs predicted value

### Feature Processing

- Optional preprocessor support for feature transformation
- Automatic feature ordering based on metadata
- Numpy array conversion for model input

### Model Persistence

Models can be saved to and loaded from disk:

- Model architecture and weights
- Preprocessor state (if applicable)
- Model metadata
- Version information

## Model Usage

Example of using a model for prediction:

```python
# Get model from registry
model = model_registry.get_model("model_name", version="1.0.0")

# Make prediction
result = model.predict({
    "feature1": value1,
    "feature2": value2
})

# Access prediction results
prediction = result.prediction
probability = result.probability
details = result.details
```

## Adding New Models

To add a new model type:

1. Inherit from the base `Model` class
2. Implement the `predict` method
3. Add appropriate serialization methods
4. Register the model with the registry

See the TensorFlow model implementation for a reference example.
