# PDF Processor

## Overview
The PDF Processor extends schema detection capabilities to PDF files, enabling extraction and analysis of text from PDF documents within the data processing pipeline.

## Features
- PDF content extraction and conversion to structured data
- Schema detection for PDF documents
- Text statistics and entity extraction
- Validation of PDF files (encrypted, empty, etc.)

## Usage

### Basic Usage
```python
from pyspark.sql import SparkSession
from src.stages.stage1_schema_detection.processors.pdf_processor import PDFProcessor

# Initialize SparkSession
spark = SparkSession.builder.appName("pdf-processing").getOrCreate()

# Create processor
processor = PDFProcessor(spark)

# Extract schema and data
schema = processor.extract_schema("document.pdf")
df = processor.extract_sample_data("document.pdf")

# Validate PDF file
validation_messages = processor.validate("document.pdf")
for message in validation_messages:
    print(message)
```

### Advanced Options
The PDF processor supports several options to customize processing:

```python
# Enable entity extraction
df = processor.extract_sample_data(
    "document.pdf", 
    options={
        "include_entities": True,  # Extract emails, URLs, dates
        "include_stats": True      # Include text statistics
    }
)

# Process only first 5 pages
df = processor.extract_sample_data("document.pdf", limit=5)
```

## Schema
The generated schema for PDF documents includes the following fields:

| Field | Type | Description |
|-------|------|-------------|
| page_number | Long | Page number in the document |
| text_content | String | Extracted text content |
| word_count | Long | Number of words in the text |
| extracted_at | Timestamp | When extraction occurred |
| char_count* | Long | Number of characters |
| sentence_count* | Long | Approximate number of sentences |
| avg_word_length* | Double | Average word length |
| emails** | Array[String] | Extracted email addresses |
| urls** | Array[String] | Extracted URLs |
| dates** | Array[String] | Extracted date strings |

\* Included when `include_stats=True` (default)  
\** Included when `include_entities=True`

## Integration
The PDF Processor is integrated with other components:

- **Schema Detection Stage**: Automatically detects PDF files based on extension
- **Data Quality Pipeline**: Text quality metrics can be applied to extracted content
- **Documentation Analysis**: Enables content extraction from PDF documentation

## Limitations
- PDF files with security restrictions may not be processable
- Image-based PDFs require OCR (not currently supported)
- PDF forms and interactive elements are not supported
- Very large PDFs may require additional memory configuration 