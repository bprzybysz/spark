# Development Environment Setup

This guide explains how to set up your development environment for the project.

## Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- Java 8 or higher (for Spark)
- Git

## Initial Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Configure Poetry to create virtual environments in the project directory (optional):
```bash
poetry config virtualenvs.in-project true
```

4. Install dependencies:
```bash
poetry install
```

5. Set up pre-commit hooks:
```bash
poetry run pre-commit install
```

## Development Tools

### Code Quality Tools

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Style guide enforcement
- **mypy**: Static type checking
- **pylint**: Code analysis

These tools are configured in:
- `pyproject.toml`: Poetry and tool-specific settings
- `.cursorcodestyle**: Main code style configuration

### Testing Tools

- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **pytest-spark**: Spark testing utilities

Run tests with:
```bash
poetry run pytest
```

### Documentation Tools

- **MkDocs**: Documentation generator
- **Material theme**: Documentation styling

Build documentation with:
```bash
poetry run mkdocs serve
```

## IDE Setup

### VS Code

1. Install recommended extensions:
   - Python
   - Pylance
   - Python Test Explorer
   - markdownlint

2. Configure settings:
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "editor.rulers": [100],
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true,
    "python.poetryPath": "poetry"
}
```

### PyCharm

1. Install plugins:
   - Poetry
   - Black
   - Mypy

2. Configure settings:
   - Set Black as formatter
   - Enable "Format on Save"
   - Set line length to 100
   - Enable type checking mode
   - Set Poetry as package manager

## Environment Variables

Create a `.env` file in the project root:
```bash
PYSPARK_PYTHON=/path/to/python
PYSPARK_DRIVER_PYTHON=/path/to/python
SPARK_LOCAL_IP=127.0.0.1
```

## Project Structure

```
├── src/
│   ├── stages/
│   │   ├── stage1_schema/
│   │   ├── stage2_transform/
│   │   ├── stage3_quality/
│   │   └── stage4_analytics/
│   ├── core/
│   └── utils/
├── tests/
│   ├── stage1_schema/
│   ├── stage2_transform/
│   ├── stage3_quality/
│   └── stage4_analytics/
├── docs/
├── poetry.lock
├── pyproject.toml
└── README.md
```

## Development Workflow

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make changes and ensure all checks pass:
```bash
# Format code
poetry run black .
poetry run isort .

# Run linters
poetry run flake8
poetry run mypy .

# Run tests
poetry run pytest
```

3. Commit changes following the commit message format:
```bash
git commit -m "feat(scope): description"
```

4. Push changes and create a pull request:
```bash
git push origin feature/your-feature-name
```

## Troubleshooting

### Common Issues

1. **Poetry environment issues**:
```bash
poetry env remove python
poetry install
```

2. **Spark connection issues**:
```bash
export SPARK_LOCAL_IP=127.0.0.1
```

3. **Import errors**:
```bash
# Reinstall in development mode
poetry install
```

### Getting Help

- Check the project documentation
- Review existing issues
- Create a new issue with:
  - Environment details
  - Steps to reproduce
  - Expected vs actual behavior 