# Architecture Overview

This document provides a high-level overview of the Spark ETL ML Pipeline architecture.

## System Components

The system is composed of several key components that work together to provide a comprehensive data engineering and machine learning pipeline:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Data Sources   │────▶│  Data Pipeline  │────▶│  ML Pipeline    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  API Consumers  │◀────│  API Layer      │◀────│  Model Serving  │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Core Modules

### Data Pipeline

- **Hive Integration**: Data warehousing and storage
- **Spark Streams**: Real-time data processing pipeline
- **ETL**: Batch data processing using Spark
- **Schema Management**: Automatic schema detection and validation

### ML Pipeline

- **Training**: Jupyter notebook environment for model development
- **Models**: Model definitions, registry and versioning
- **Inference**: Model inference optimization

### API Layer

- **FastAPI**: RESTful API for model serving
- **MCP Servers**: Message Communication Protocol for external system integration
- **Pydantic Models**: Data validation and serialization

### Core Infrastructure

- **Dependency Injection**: Service container and lifecycle management
- **Configuration**: Configuration management with environment-specific settings
- **Logging**: Comprehensive logging and monitoring

## Data Flow

1. **Data Ingestion**: Raw data is ingested through Spark Streaming or batch processes
2. **Data Processing**: ETL pipelines transform raw data into analysis-ready datasets
3. **Data Storage**: Processed data is stored in Hive or other storage systems
4. **Model Training**: ML models are trained using the processed data
5. **Model Serving**: Trained models are deployed for inference via FastAPI
6. **API Consumption**: External systems consume predictions through the API

## Modular Design

The system follows a modular design pattern, with clear separation of concerns:

- **Service Interfaces**: Define contracts between components
- **Implementations**: Provide concrete implementations of services
- **Factories**: Create and configure service instances
- **Composition Root**: Wire dependencies together

This approach enables:

- **Testability**: Components can be easily mocked and tested in isolation
- **Maintainability**: Clear boundaries between components
- **Extensibility**: New implementations can be added without modifying existing code

## Deployment Architecture

The system can be deployed in various configurations:

- **Local Development**: All components running locally for development
- **Containerized**: Docker containers for each component
- **Distributed**: Components distributed across multiple machines
- **Cloud-native**: Deployed on cloud infrastructure (e.g., Kubernetes)

## Configuration Management

Configuration is managed through a hierarchical approach:

1. **Default Configuration**: Baseline settings in code
2. **Environment Configuration**: Environment-specific overrides
3. **Local Configuration**: Development-specific settings (not in version control)
4. **Command-line Arguments**: Overrides for specific runs

This allows for flexible deployment across different environments while maintaining configuration consistency. 