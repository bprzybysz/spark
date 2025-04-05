# API Endpoints

This document describes the available API endpoints for the ML Model Serving API.

## Base URL

The API is served at the configured host and port (default: `http://localhost:8000`).

## Endpoints

### Health Check

```http
GET /health
```

Returns the health status of the API service.

**Response**
```json
{
    "status": "ok",
    "version": "0.1.0"
}
```

### List Models

```http
GET /models
```

Returns a list of available models in the registry.

**Response**
```json
{
    "models": [
        {
            "name": "model_name",
            "version": "1.0.0",
            "metadata": {
                // Model metadata if available
            }
        }
    ]
}
```

### Make Prediction

```http
POST /predict
```

Make predictions using a specified model.

**Request Body**
```json
{
    "model_name": "string",
    "model_version": "string",  // Optional, defaults to latest
    "features": {
        // Feature key-value pairs
    }
}
```

**Response**
```json
{
    "model_name": "string",
    "model_version": "string",
    "prediction": "any",
    "probability": "number",  // Optional
    "details": {
        // Additional prediction details
    }
}
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 404: Model not found
- 500: Internal server error

Error responses include a detail message explaining the error.
