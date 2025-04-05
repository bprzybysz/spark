"""
PDF processor for schema detection.
"""

import os
import re
import json
import tempfile
import datetime
from typing import Dict, List, Optional, Union

import pypdf
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType, TimestampType, ArrayType

from src.stages.stage1_schema_detection.processors.base_processor import DataSourceProcessor
from src.stages.stage1_schema_detection.utils.text_extraction import clean_text, extract_entities, calculate_text_stats

class PDFProcessor(DataSourceProcessor):
    """Processor for PDF data sources."""
    
    def can_process(self, source_path: str) -> bool:
        """Check if this processor can handle the given source.
        
        Args:
            source_path: Path to the data source
            
        Returns:
            True if this is a PDF file, False otherwise
        """
        return source_path.lower().endswith('.pdf')
    
    def extract_schema(self, source_path: str, options: Optional[Dict] = None) -> StructType:
        """Extract schema from PDF file.
        
        PDF files don't have a built-in schema, so we create a standard text-based schema.
        
        Args:
            source_path: Path to the PDF file
            options: Additional options for processing
            
        Returns:
            Schema representing the PDF content
        """
        options = options or {}
        include_entities = options.get("include_entities", False)
        include_stats = options.get("include_stats", True)
        
        # Base schema
        fields = [
            StructField("page_number", LongType(), False),
            StructField("text_content", StringType(), True),
            StructField("word_count", LongType(), True),
            StructField("extracted_at", TimestampType(), True)
        ]
        
        # Add statistics fields if requested
        if include_stats:
            fields.extend([
                StructField("char_count", LongType(), True),
                StructField("sentence_count", LongType(), True),
                StructField("avg_word_length", DoubleType(), True)
            ])
        
        # Add entity fields if requested
        if include_entities:
            fields.extend([
                StructField("emails", ArrayType(StringType()), True),
                StructField("urls", ArrayType(StringType()), True),
                StructField("dates", ArrayType(StringType()), True)
            ])
        
        return StructType(fields)
    
    def extract_sample_data(self, source_path: str, limit: int = 100, 
                           options: Optional[Dict] = None) -> DataFrame:
        """Extract text content from the PDF file.
        
        Args:
            source_path: Path to the PDF file
            limit: Maximum number of pages to extract
            options: Additional options for processing
            
        Returns:
            DataFrame containing the extracted text
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"PDF file not found: {source_path}")
        
        options = options or {}
        include_entities = options.get("include_entities", False)
        include_stats = options.get("include_stats", True)
        
        try:
            # Extract text from PDF
            reader = pypdf.PdfReader(source_path)
            total_pages = len(reader.pages)
            pages_to_extract = min(total_pages, limit)
            
            extracted_data = []
            for i in range(pages_to_extract):
                page = reader.pages[i]
                text_content = page.extract_text()
                cleaned_text = clean_text(text_content)
                
                # Prepare record
                record = {
                    "page_number": i + 1,
                    "text_content": cleaned_text,
                    "word_count": len(re.findall(r'\w+', cleaned_text)),
                    "extracted_at": datetime.datetime.now()
                }
                
                # Add statistics if requested
                if include_stats:
                    stats = calculate_text_stats(cleaned_text)
                    record.update({
                        "char_count": stats["char_count"],
                        "sentence_count": stats["sentence_count"],
                        "avg_word_length": stats["avg_word_length"]
                    })
                
                # Add entities if requested
                if include_entities:
                    entities = extract_entities(cleaned_text)
                    record.update(entities)
                
                extracted_data.append(record)
            
            # Convert to DataFrame
            temp_dir = tempfile.mkdtemp()
            temp_json_path = os.path.join(temp_dir, "pdf_extracted.json")
            
            with open(temp_json_path, 'w') as f:
                json.dump(extracted_data, f)
            
            # Create DataFrame from the JSON file
            schema = self.extract_schema(source_path, options)
            df = self.spark.read.schema(schema).json(temp_json_path)
            
            # Clean up temporary files
            if os.path.exists(temp_json_path):
                os.remove(temp_json_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            
            return df
        
        except Exception as e:
            # Create an empty DataFrame with the correct schema
            schema = self.extract_schema(source_path, options)
            return self.spark.createDataFrame([], schema)
    
    def validate(self, source_path: str, options: Optional[Dict] = None) -> List[str]:
        """Validate the PDF file.
        
        Args:
            source_path: Path to the PDF file
            options: Additional options for processing
            
        Returns:
            List of validation messages/errors
        """
        validation_messages = []
        
        if not os.path.exists(source_path):
            validation_messages.append(f"File not found: {source_path}")
            return validation_messages
        
        try:
            # Check if file is a valid PDF
            reader = pypdf.PdfReader(source_path)
            
            # Check if PDF is encrypted
            if reader.is_encrypted:
                validation_messages.append(f"PDF is encrypted: {source_path}")
            
            # Check if PDF has pages
            if len(reader.pages) == 0:
                validation_messages.append(f"PDF has no pages: {source_path}")
            
            # Check if text can be extracted from first page
            if len(reader.pages) > 0:
                text = reader.pages[0].extract_text()
                if not text.strip():
                    validation_messages.append(f"Page 1 has no extractable text")
        
        except Exception as e:
            validation_messages.append(f"Invalid PDF file: {str(e)}")
        
        return validation_messages 