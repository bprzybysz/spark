# Development Guidelines

This document outlines the development workflow and best practices for the project.

## Environment Setup

### Python Version
- Python 3.11 is strictly required
- Use Poetry for dependency management

### Initial Setup
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## Development Workflow

### 1. Code Generation

The project uses templates for consistent code generation:

- Templates Location: `.cursor/templates`
- Automatic test generation
- Documentation synchronization

### 2. Pre-commit Checks

Before committing code, the following checks are automatically run:

```bash
# Code formatting
poetry run black {changed_files}

# Import sorting
poetry run isort {changed_files}

# Type checking
poetry run mypy {changed_files}
```

### 3. Testing

Tests are automatically run after commits:

```bash
# Run related tests
poetry run pytest tests/{related_tests}
```

### 4. Documentation

Documentation is automatically synchronized with code changes:

- Updates related documentation files
- Validates documentation links
- Requires examples in documentation

## Project Structure

### Service Template
- Code: `src/{module}/services/{name}_service.py`
- Tests: `tests/{module}/services/test_{name}_service.py`
- Docs: `docs/api/{module}/services/{name}.md`

### Model Template
- Code: `src/ml/models/{name}_model.py`
- Tests: `tests/ml/models/test_{name}_model.py`
- Docs: `docs/models/{name}.md`

## Best Practices

### 1. Code Quality
- Follow PEP 8 style guide
- Use type hints
- Write comprehensive docstrings
- Include unit tests

### 2. Documentation
- Keep documentation in sync with code
- Include practical examples
- Validate all documentation links
- Document API changes

### 3. Testing
- Write tests for new features
- Maintain test coverage
- Use appropriate test fixtures
- Mock external dependencies

### 4. Version Control
- Write clear commit messages
- Reference issues in commits
- Keep commits focused and atomic
- Follow branching strategy

## Debugging

- Log Level: DEBUG
- Break on errors enabled
- Context capture for debugging
- Use appropriate logging

## Tools and Extensions

### Code Quality
- Black for formatting
- isort for import sorting
- mypy for type checking
- pytest for testing

### Documentation
- Markdown for documentation
- Automatic link validation
- Example requirement checking
- Documentation synchronization

## Workflow Automation

### Development Workflow
```yaml
dev:
  pre_commit:
    - "poetry run black {changed_files}"
    - "poetry run isort {changed_files}"
    - "poetry run mypy {changed_files}"
  post_commit:
    - "poetry run pytest tests/{related_tests}"
```

### Documentation Workflow
```yaml
doc:
  on_code_change:
    - "update_related_docs {changed_files}"
    - "validate_doc_links"
```
