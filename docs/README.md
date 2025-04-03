# Documentation

This directory contains comprehensive documentation for the Spark ETL ML Pipeline project.

## Structure

- `architecture/` - System architecture documentation
- `api/` - API documentation
- `data/` - Data pipeline documentation
- `ml/` - Machine learning documentation
- `dev/` - Developer guides

## Building Documentation

Documentation is built using [MkDocs](https://www.mkdocs.org/) with the Material theme.

To build and serve the documentation locally:

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Serve documentation
mkdocs serve
```

The documentation will be available at `http://localhost:8000`.

## Contributing to Documentation

When contributing to documentation:

1. Follow the established formatting style
2. Place API references in the `api/` directory
3. Place architecture diagrams in the `architecture/` directory
4. Include code examples where appropriate
5. Update the navigation in `mkdocs.yml` if adding new pages 