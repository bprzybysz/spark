# API Schema Validation

## Overview
This document describes the schema validation system used in our API endpoints. The validation ensures data consistency and provides clear error messages for invalid requests.

## Implementation

### Request Validation
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class DataSourceConfig(BaseModel):
    source_type: str = Field(..., description="Type of data source (parquet, csv, etc.)")
    path: str = Field(..., description="Path to the data source")
    options: Optional[dict] = Field(default={}, description="Additional options")

class ValidationResponse(BaseModel):
    is_valid: bool
    messages: List[str]
    details: Optional[dict]
```

### Response Validation
```python
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

app = FastAPI()

@app.post("/validate/schema", response_model=ValidationResponse)
async def validate_schema(config: DataSourceConfig):
    try:
        # Validate schema
        validation_result = schema_validator.validate(config)
        return ValidationResponse(
            is_valid=validation_result.is_valid,
            messages=validation_result.messages,
            details=validation_result.details
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
```

## Validation Rules

### Data Types
- **Numeric Types**: int, float, decimal
- **String Types**: str, char
- **Date/Time Types**: date, timestamp
- **Complex Types**: struct, array, map

### Constraints
1. **Nullability**
   - Required fields
   - Optional fields
   - Default values

2. **Range Constraints**
   - Minimum/maximum values
   - String length
   - Array size

3. **Pattern Matching**
   - Regular expressions
   - Format validation
   - Custom validators

## Error Handling

### Error Types
1. **Schema Validation Errors**
   ```json
   {
     "detail": {
       "loc": ["body", "source_type"],
       "msg": "field required",
       "type": "value_error.missing"
     }
   }
   ```

2. **Type Conversion Errors**
   ```json
   {
     "detail": {
       "loc": ["body", "options", "partition_count"],
       "msg": "value is not a valid integer",
       "type": "type_error.integer"
     }
   }
   ```

3. **Constraint Violations**
   ```json
   {
     "detail": {
       "loc": ["body", "path"],
       "msg": "path must be absolute",
       "type": "value_error.path"
     }
   }
   ```

### Error Response Format
```json
{
  "status": "error",
  "code": 422,
  "message": "Validation error",
  "details": [
    {
      "field": "source_type",
      "error": "Invalid source type. Must be one of: parquet, csv, json"
    }
  ]
}
```

## Best Practices

### Input Validation
1. Always validate request bodies using Pydantic models
2. Use appropriate field types and constraints
3. Provide clear error messages
4. Include field descriptions in OpenAPI documentation

### Response Validation
1. Define response models for all endpoints
2. Include appropriate status codes
3. Maintain consistent error response format
4. Document all possible response scenarios

## Testing

### Unit Tests
```python
def test_schema_validation():
    config = DataSourceConfig(
        source_type="parquet",
        path="/data/example.parquet"
    )
    response = client.post("/validate/schema", json=config.dict())
    assert response.status_code == 200
    assert response.json()["is_valid"] == True
```

### Integration Tests
```python
def test_invalid_schema():
    config = {
        "source_type": "invalid",
        "path": "/data/example.data"
    }
    response = client.post("/validate/schema", json=config)
    assert response.status_code == 422
    assert "Invalid source type" in response.json()["detail"]
```

## OpenAPI Documentation
```yaml
paths:
  /validate/schema:
    post:
      summary: Validate data source schema
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DataSourceConfig'
      responses:
        '200':
          description: Successful validation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ValidationResponse'
        '422':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
```

## Future Improvements
1. Add support for custom validation rules
2. Implement schema caching
3. Add schema versioning
4. Enhance validation performance
5. Add support for more complex data types 