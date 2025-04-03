# Documentation

This directory contains comprehensive documentation for the Spark ETL ML Pipeline project.

## Structure

- `architecture/` - System architecture and design documentation
  - `overview.md` - High-level system architecture
  - `data_flow.md` - Data processing pipeline details
  - `ml_pipeline.md` - Machine learning pipeline architecture

- `dev/` - Developer guides and references
  - `setup_guide.md` - Development environment setup
  - `code_style_guide.md` - Coding standards and style guide
  - `testing_guide.md` - Testing practices and guidelines
  - `contribution_guide.md` - How to contribute to the project

- `api/` - API documentation
  - `endpoints.md` - REST API endpoints
  - `models.md` - Data models and schemas
  - `examples.md` - API usage examples

- `stages/` - Pipeline stage documentation
  - `stage1_schema.md` - Schema detection and validation
  - `stage2_transform.md` - Data transformation
  - `stage3_quality.md` - Data quality checks
  - `stage4_analytics.md` - Data analytics and aggregation

## Building Documentation

Documentation is built using [MkDocs](https://www.mkdocs.org/) with the Material theme.

### Local Development

1. Install documentation dependencies:
```bash
poetry install --with docs
```

2. Serve documentation locally:
```bash
poetry run mkdocs serve
```

The documentation will be available at `http://localhost:8000`.

## Contributing to Documentation

When contributing to documentation:

1. Follow the Google Developer Documentation Style Guide
2. Use Markdown for all documentation files
3. Include code examples with syntax highlighting
4. Add type hints in code examples
5. Follow the directory structure:
   - API references go in `api/`
   - Architecture docs go in `architecture/`
   - Developer guides go in `dev/`
   - Stage-specific docs go in `stages/`
6. Update navigation in `mkdocs.yml` when adding new pages
7. Ensure all links are valid
8. Include doctest examples where appropriate

### Documentation Standards

- Line length: 100 characters
- Code blocks: Include language for syntax highlighting
- Headers: Use ATX-style headers (#)
- Lists: Use - for unordered lists
- Links: Use reference-style links for repeated URLs
- Images: Include alt text and captions
- Tables: Use standard Markdown tables

### Code Examples

Code examples should:
- Include type hints
- Follow the project's code style guide
- Be tested where possible
- Include comments explaining complex parts
- Show both usage and expected output

Example:
```python
from typing import List
from pyspark.sql import DataFrame

def transform_data(df: DataFrame, columns: List[str]) -> DataFrame:
    """Transform the specified columns in the DataFrame.
    
    Args:
        df: Input DataFrame
        columns: List of columns to transform
        
    Returns:
        DataFrame with transformed columns
    """
    # Implementation
```

### Review Process

Documentation changes follow the same review process as code:

1. Create a feature branch
2. Make documentation changes
3. Build docs locally to verify
4. Submit a pull request
5. Address review comments
6. Merge after approval 