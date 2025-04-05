"""
Data source processors for schema detection.

This package contains processors for different data source types.
"""

from src.stages.stage1_schema_detection.processors.base_processor import DataSourceProcessor
from src.stages.stage1_schema_detection.processors.pdf_processor import PDFProcessor
from src.stages.stage1_schema_detection.processors.parquet_processor import ParquetProcessor

__all__ = ['DataSourceProcessor', 'PDFProcessor', 'ParquetProcessor'] 