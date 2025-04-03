# Stage 5: Model Training and Evaluation

This stage implements machine learning model training and evaluation using PySpark ML. It provides a flexible framework for training both classification and regression models, with support for feature engineering, hyperparameter tuning, and comprehensive model evaluation.

## Components

### Configuration (`config.py`)

Defines configuration classes and validation for model training and evaluation:

- `ModelType`: Supported model types (Classification, Regression)
- `ModelAlgorithm`: Available algorithms for each model type
- `EvaluationMetric`: Supported evaluation metrics
- `FeatureConfig`: Feature engineering configuration
- `TrainingConfig`: Model training configuration
- `EvaluationConfig`: Model evaluation configuration

### Model Training (`training/model_trainer.py`)

Implements model training functionality:

- Feature preparation pipeline
- Model creation and configuration
- Hyperparameter tuning using cross-validation
- Model persistence and loading
- Training metrics collection

### Model Evaluation (`evaluation/model_evaluator.py`)

Provides comprehensive model evaluation capabilities:

- Multiple evaluation metrics for classification and regression
- Feature importance analysis
- Prediction analysis and visualization
- Cross-validation metrics
- Model comparison utilities

### Utilities (`utils/model_utils.py`)

Helper functions for model training and evaluation:

- Train-test split preparation
- Schema validation
- Model persistence
- Prediction analysis
- Feature correlation analysis
- Data leakage detection

## Usage

### Basic Training Example

```python
from src.stages.stage5_model.config import (
    ModelType,
    ModelAlgorithm,
    EvaluationMetric,
    FeatureConfig,
    TrainingConfig
)
from src.stages.stage5_model.training.model_trainer import ModelTrainer

# Configure feature engineering
feature_config = FeatureConfig(
    categorical_columns=["category"],
    numerical_columns=["feature1", "feature2"],
    categorical_encoding="one_hot",
    numerical_scaling="standard"
)

# Configure model training
training_config = TrainingConfig(
    model_type=ModelType.CLASSIFICATION,
    model_algorithm=ModelAlgorithm.RANDOM_FOREST_CLASSIFIER,
    feature_config=feature_config,
    label_column="label",
    evaluation_metric=EvaluationMetric.F1_SCORE,
    hyperparameters={
        "numTrees": [10, 20, 30],
        "maxDepth": [5, 10, 15]
    }
)

# Train model
trainer = ModelTrainer(training_config)
model, metrics = trainer.train_model(input_df)

# Save model
model_path = trainer.save_model(
    model,
    "models",
    "random_forest_classifier",
    metrics
)
```

### Basic Evaluation Example

```python
from src.stages.stage5_model.config import (
    ModelType,
    EvaluationMetric,
    EvaluationConfig
)
from src.stages.stage5_model.evaluation.model_evaluator import ModelEvaluator

# Configure evaluation
eval_config = EvaluationConfig(
    model_type=ModelType.CLASSIFICATION,
    metrics=[
        EvaluationMetric.ACCURACY,
        EvaluationMetric.PRECISION,
        EvaluationMetric.RECALL,
        EvaluationMetric.F1_SCORE
    ],
    label_column="label"
)

# Evaluate model
evaluator = ModelEvaluator(eval_config)
metrics = evaluator.evaluate_model(predictions_df)

# Generate detailed analysis
feature_importance = evaluator.get_feature_importance(
    predictions_df,
    ["category", "feature1", "feature2"]
)
predictions_summary = evaluator.generate_predictions_summary(
    predictions_df
)
```

## Configuration Options

### Feature Engineering

- Categorical encoding: one-hot, label
- Numerical scaling: standard, minmax, robust
- Text vectorization: tfidf, count, word2vec
- Date encoding: cyclic, timestamp

### Model Types

#### Classification
- Logistic Regression
- Random Forest Classifier
- Gradient Boosted Classifier

#### Regression
- Linear Regression
- Random Forest Regressor
- Gradient Boosted Regressor

### Evaluation Metrics

#### Classification
- Accuracy
- Precision
- Recall
- F1 Score
- ROC AUC

#### Regression
- MSE
- RMSE
- MAE
- R2
- Explained Variance

## Testing

The stage includes comprehensive test coverage:

```bash
# Run all Stage 5 tests
pytest tests/stage5_model/

# Run specific test files
pytest tests/stage5_model/test_config.py
pytest tests/stage5_model/test_model_trainer.py
pytest tests/stage5_model/test_model_evaluator.py
pytest tests/stage5_model/test_model_utils.py
```

## Dependencies

- PySpark ML
- NumPy
- Pandas
- scikit-learn (for additional metrics)

## Best Practices

1. **Feature Engineering**
   - Always validate input schema
   - Handle missing values appropriately
   - Scale numerical features
   - Encode categorical variables

2. **Model Training**
   - Use cross-validation for hyperparameter tuning
   - Monitor training metrics
   - Save model metadata with timestamps
   - Check for data leakage

3. **Model Evaluation**
   - Use multiple evaluation metrics
   - Generate comprehensive prediction analysis
   - Check feature importance
   - Validate model stability with cross-validation

4. **Model Persistence**
   - Save models with metadata
   - Version control model artifacts
   - Document model configurations
   - Track evaluation metrics

## Contributing

When contributing to this stage:

1. Follow the established code style
2. Add appropriate tests
3. Update documentation
4. Validate configurations
5. Test with both classification and regression tasks 