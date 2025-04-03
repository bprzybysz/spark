# Workflow Components

This directory contains workflow definitions, orchestration code, and pipeline configurations for the data engineering and ML pipeline project.

## Structure

- `codebasemap.json` - Provides a structured map of the entire codebase and its components
- `etl/` - ETL workflow configurations and orchestration
- `streaming/` - Streaming data workflow configurations
- `training/` - ML model training workflow components
- `inference/` - Model inference and serving workflow components

## Workflow Definitions

Each workflow directory contains:

1. Configuration files
2. DAG definitions (if using Airflow)
3. Orchestration scripts
4. Documentation

## Usage

To execute workflows:

1. Ensure all dependencies are installed
2. Configure the appropriate environment variables
3. Run the desired workflow script

Example:

```bash
# Run the ETL workflow
python -m workflow.etl.run

# Run the training workflow
python -m workflow.training.run
```

## Development

When extending workflows:

1. Follow the existing patterns
2. Update the `codebasemap.json` with any new components
3. Document the workflow in the appropriate README
4. Add tests for new workflow components 