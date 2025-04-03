# Spark ETL ML Pipeline

A comprehensive data engineering and machine learning pipeline integrating Hive, Spark Streaming, Spark ETL, and TensorFlow with FastAPI serving.

## Features

- **Data Engineering**
  - Hive integration for data warehousing
  - Spark Streaming for real-time data processing
  - Batch ETL with PySpark
  - Automatic schema detection and validation

- **Machine Learning**
  - Jupyter Notebook training environment
  - TensorFlow and PySpark ML integration
  - Model versioning and registry
  - Inference optimization

- **API & Serving**
  - FastAPI for model serving
  - Pydantic schemas for validation
  - MCP (Message Communication Protocol) servers
  - External API integration

- **Core Architecture**
  - Dependency Injection
  - Modular service architecture
  - Comprehensive logging
  - Configuration management

## Getting Started

### Prerequisites

- Python 3.10 (strict requirement)
- Java 11+
- Spark 3.3+
- Docker (optional)
- Poetry (for dependency management)

### Package Management

We use Poetry for dependency management to ensure reproducible builds and isolated environments:

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Create new environment and install dependencies
poetry install

# Add new dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Export requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt
```

### Environment Management

The project uses isolated environments per component:

- `poetry.lock` - Main dependency lock file
- `.env` - Environment variables (from .env.example)
- `config/` - Component-specific configurations
- `secrets/` - Secrets management (using HashiCorp Vault)

### Secrets Management

Secrets are managed using HashiCorp Vault:

```bash
# Initialize Vault (first time only)
vault operator init

# Store a secret
vault kv put secret/database password=mypassword

# Retrieve a secret
vault kv get secret/database
```

See [Secrets Management Guide](docs/security/secrets.md) for details.

## Documentation Structure

```
docs/
├── architecture/          # System architecture documentation
│   ├── overview.md       # High-level system design
│   └── decisions.md      # Architecture decisions
├── api/                  # API documentation
│   ├── endpoints.md      # API endpoints
│   └── schemas.md        # Data schemas
├── data/                 # Data pipeline documentation
│   ├── etl.md           # ETL processes
│   └── streaming.md      # Streaming pipeline
├── ml/                   # Machine learning documentation
│   ├── models.md         # Model architecture
│   └── training.md       # Training pipeline
├── workflow/             # Workflow documentation
│   ├── progress.md       # Project progress tracking
│   └── development.md    # Development guidelines
└── security/             # Security documentation
    └── secrets.md        # Secrets management
```

## Development Workflow

### Code Generation

Use Cursor tools for code generation:

```bash
# Generate new service
cursor generate service user_management

# Generate new model
cursor generate model recommendation
```

### Progress Tracking

Track development progress in `workflow/progress.yaml`:

```bash
# View current progress
poetry run python -m workflow.progress status

# Update task status
poetry run python -m workflow.progress update "Complete schema detection" --status done
```

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/your-org/spark-etl-ml-pipeline.git
   cd spark-etl-ml-pipeline
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running Components

#### ETL Pipelines

```bash
python -m src.data.etl.run --config config/etl.yaml
```

#### Streaming

```bash
python -m src.data.streams.run --config config/streams.yaml
```

#### Training

```bash
# Start Jupyter for interactive development
jupyter notebook notebooks/

# Or run a training job
python -m src.ml.training.run --config config/training.yaml
```

#### API

```bash
# Start the FastAPI server
python -m src.api.fastapi.main
```

## Project Structure

```
├── docs/                  # Documentation
├── notebooks/             # Jupyter notebooks for exploration and training
├── src/                   # Source code
│   ├── api/               # API components
│   │   ├── fastapi/       # FastAPI implementation
│   │   └── mcp/           # MCP servers
│   ├── core/              # Core components
│   │   ├── config/        # Configuration management
│   │   ├── di/            # Dependency injection
│   │   └── logging/       # Logging infrastructure
│   ├── data/              # Data components
│   │   ├── etl/           # Batch ETL
│   │   ├── hive/          # Hive integration
│   │   ├── schema/        # Schema management
│   │   └── streams/       # Streaming components
│   ├── ml/                # Machine learning components
│   │   ├── inference/     # Model inference
│   │   ├── models/        # Model definitions
│   │   └── training/      # Model training
│   └── common/            # Shared utilities
├── tests/                 # Test suite
├── workflow/              # Workflow definitions
│   ├── etl/               # ETL workflows
│   ├── inference/         # Inference workflows
│   ├── streaming/         # Streaming workflows
│   └── training/          # Training workflows
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore file
├── pyproject.toml         # Python project configuration
├── README.md              # This file
└── requirements.txt       # Dependencies
```

## Development

### Adding New Components

1. Follow the modular architecture pattern
2. Update the `workflow/codebasemap.json` with your new component
3. Add appropriate tests
4. Document your component

### Testing

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/data/
```

## Documentation

For full documentation, see the [docs](./docs/) directory or visit our documentation site.

## Contributing

1. Check `workflow/progress.yaml` for current status and next steps
2. Follow the [Development Guidelines](docs/workflow/development.md)
3. Use Poetry for dependency management
4. Ensure documentation is updated
5. Add tests for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 