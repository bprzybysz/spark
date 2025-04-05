# Stage 1: Schema Detection

## Overview

This stage provides automatic schema detection and inference for various data sources including:
- CSV files
- JSON files
- Parquet files (single files & directories)
- Hive tables (regular & partitioned)
- PDF documents

## Components

### Core Components

- **SchemaDetector**: Main class for detecting schemas from different data sources
- **SchemaDetectionStage**: Stage implementation that orchestrates the detection process
- **SchemaDetectionResult**: Data class that holds the detection results

### Processors

The stage uses a processor-based architecture to handle different file types:

- **BaseProcessor**: Abstract base class for all data source processors
- **ParquetProcessor**: Processor for Parquet files and directories
- **PDFProcessor**: Processor for PDF documents and text extraction
- (Additional processors for CSV/JSON are handled directly in the SchemaDetector)

## Features

- **Automatic Source Type Detection**: Automatically detects file type from extension or content
- **Schema Validation**: Validates detected schemas for common issues
- **Sample Data Extraction**: Provides sample data for verification and preview
- **Partition Handling**: Properly handles partitioned datasets
- **Complex Data Types**: Supports nested structures, arrays, and maps
- **Error Handling**: Robust error handling for various failure scenarios

## Usage Examples

```python
from pyspark.sql import SparkSession
from src.stages.stage1_schema_detection.detector import SchemaDetector, DataSourceType

# Initialize Spark and schema detector
spark = SparkSession.builder.appName("SchemaDetection").getOrCreate()
detector = SchemaDetector(spark)

# Detect schema from CSV file
csv_result = detector.detect_schema("path/to/data.csv")
print(f"CSV Schema: {csv_result.schema}")

# Detect schema from partitioned Parquet directory with explicit type
parquet_result = detector.detect_schema(
    "path/to/parquet_dir", 
    DataSourceType.PARQUET,
    sample_size=100
)
print(f"Parquet Schema: {parquet_result.schema}")
print(f"Sample Data:\n{parquet_result.sample_data}")

# Detect schema from Hive table
hive_result = detector.detect_schema("database_name.table_name", DataSourceType.HIVE)
print(f"Hive Schema: {hive_result.schema}")

# Validate the detected schema
validation_messages = detector.validate_schema(hive_result)
if validation_messages:
    print("Validation issues found:")
    for msg in validation_messages:
        print(f"- {msg}")
```

## Tests

The stage includes comprehensive tests covering:

- Schema detection for all supported file types
- Error handling and validation
- Hive integration tests with various table types
- Parquet processing with partitioning and schema evolution
- PDF text extraction and schema detection

## Configuration

The stage supports the following configuration options:

```yaml
stage_config:
  source_path: "path/to/data_source"  # Path to the data source
  source_type: "csv|json|parquet|hive"  # Optional explicit source type
  sample_size: 1000  # Number of records to sample (default: 1000)
  options:  # Source-specific options
    header: "true"  # For CSV: whether file has header
    delimiter: ","  # For CSV: field delimiter
    mergeSchema: "true"  # For Parquet: whether to merge schemas
```

## Future Improvements

- Add support for additional file types (Avocado, ORC, etc.)
- Implement schema evolution tracking
- Add data quality profiling
- Optimize performance for very large datasets 