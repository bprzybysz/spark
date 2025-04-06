"""Test script for importing PDF to Hive, extracting text, and storing results."""

import os
import sys
import base64
import PyPDF2
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest
import pandas as pd
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, BinaryType
from pyspark.sql.functions import col, udf, lit

from src.data.spark.session import SparkSessionFactory
from src.utility.monitoring import enable_spark_ui, get_spark_ui_config, find_available_port

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PDF_FILE_PATH = os.path.join("data", "pdf", "AWS Certified Solutions Architect - Associate.pdf")
PDF_DB_NAME = "document_db"
PDF_TABLE_NAME = "pdf_documents"
TEXT_TABLE_NAME = "extracted_text"


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF binary data.
    
    Args:
        pdf_bytes: Raw PDF binary data
        
    Returns:
        str: Extracted text from PDF
    """
    try:
        # Create a file-like object from bytes
        from io import BytesIO
        pdf_file = BytesIO(pdf_bytes)
        
        # Parse PDF with PyPDF2
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"
            
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return f"Error: {str(e)}"


def setup_spark_session() -> SparkSession:
    """
    Set up a Spark session with Hive support and UI enabled.
    
    Returns:
        SparkSession: Configured Spark session
    """
    # Find an available port for Spark UI
    port = find_available_port(4040)
    if not port:
        logger.warning("No available ports found, using default port 4040")
        port = 4040
    
    # Create event log directory
    event_log_dir = os.path.join(os.getcwd(), "spark-events")
    os.makedirs(event_log_dir, exist_ok=True)
    
    # Get UI config
    ui_config = get_spark_ui_config(port=port)
    
    # Add Hive-specific configurations
    warehouse_dir = os.path.join(os.getcwd(), "spark-warehouse")
    os.makedirs(warehouse_dir, exist_ok=True)
    
    ui_config.update({
        "spark.sql.catalogImplementation": "hive",
        "spark.sql.warehouse.dir": warehouse_dir,
        "spark.hadoop.javax.jdo.option.ConnectionURL": f"jdbc:derby:;databaseName={warehouse_dir}/metastore_db;create=true",
        "spark.hadoop.datanucleus.schema.autoCreateAll": "true",
        "spark.hadoop.hive.metastore.schema.verification": "false",
        # Increase SQL output max
        "spark.sql.debug.maxToStringFields": "100",
        # Hive optimizations
        "spark.sql.hive.metastorePartitionPruning": "true",
        "spark.sql.hive.convertMetastoreParquet": "true"
    })
    
    # Create and return session
    factory = SparkSessionFactory(
        app_name="PDFToHiveTest",
        master="local[*]",
        config=ui_config,
        enable_hive=True
    )
    
    spark = factory.create_session()
    enable_spark_ui(spark, port=port, auto_open=True)
    
    # Verify Hive is enabled
    if spark.conf.get("spark.sql.catalogImplementation") != "hive":
        logger.error("Hive support is not enabled!")
    
    return spark


def read_pdf_to_dataframe(spark: SparkSession, pdf_path: str) -> DataFrame:
    """
    Read PDF file into a Spark DataFrame.
    
    Args:
        spark: SparkSession
        pdf_path: Path to PDF file
        
    Returns:
        DataFrame: DataFrame containing PDF binary data
    """
    # Define schema for PDF DataFrame
    pdf_schema = StructType([
        StructField("filename", StringType(), False),
        StructField("content", BinaryType(), False),
        StructField("file_size", StringType(), False),
        StructField("year", StringType(), False),
        StructField("month", StringType(), False),
        StructField("doc_type", StringType(), False)
    ])
    
    # Read PDF file as binary
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    with open(pdf_file, "rb") as f:
        pdf_content = f.read()
    
    # Create DataFrame with a single row
    pdf_row = [(
        pdf_file.name,
        pdf_content,
        str(pdf_file.stat().st_size),
        "2023",  # Year partition
        "04",    # Month partition
        "certification"  # Document type partition
    )]
    
    return spark.createDataFrame(pdf_row, pdf_schema)


def store_pdf_in_hive(spark: SparkSession, pdf_df: DataFrame) -> None:
    """
    Store PDF DataFrame in Hive.
    
    Args:
        spark: SparkSession
        pdf_df: DataFrame containing PDF data
    """
    # Create database if not exists
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {PDF_DB_NAME}")
    spark.sql(f"USE {PDF_DB_NAME}")
    
    # Store PDF in Hive table partitioned by year, month and doc_type
    pdf_df.write.mode("overwrite") \
        .partitionBy("year", "month", "doc_type") \
        .saveAsTable(f"{PDF_DB_NAME}.{PDF_TABLE_NAME}")
    
    logger.info(f"PDF stored in Hive table: {PDF_DB_NAME}.{PDF_TABLE_NAME}")
    
    # Show table metadata
    spark.sql(f"DESCRIBE EXTENDED {PDF_DB_NAME}.{PDF_TABLE_NAME}").show(truncate=False)
    spark.sql(f"SHOW PARTITIONS {PDF_DB_NAME}.{PDF_TABLE_NAME}").show()


def extract_and_store_text(spark: SparkSession) -> None:
    """
    Extract text from PDF stored in Hive and store it in another Hive table.
    
    Args:
        spark: SparkSession
    """
    # Register UDF for text extraction
    extract_text_udf = udf(extract_text_from_pdf, StringType())
    
    # Read PDF from Hive
    pdf_df = spark.table(f"{PDF_DB_NAME}.{PDF_TABLE_NAME}")
    
    # Extract text
    text_df = pdf_df.select(
        col("filename"),
        extract_text_udf(col("content")).alias("extracted_text"),
        col("file_size"),
        col("year"),
        col("month"),
        col("doc_type"),
        lit("text").alias("content_type")
    )
    
    # Store extracted text in another Hive table
    text_df.write.mode("overwrite") \
        .partitionBy("year", "month", "doc_type", "content_type") \
        .saveAsTable(f"{PDF_DB_NAME}.{TEXT_TABLE_NAME}")
    
    logger.info(f"Extracted text stored in Hive table: {PDF_DB_NAME}.{TEXT_TABLE_NAME}")
    
    # Show extracted text
    spark.sql(f"SELECT filename, substr(extracted_text, 1, 500) as text_sample FROM {PDF_DB_NAME}.{TEXT_TABLE_NAME}").show(truncate=False)
    
    # Show partitions
    spark.sql(f"SHOW PARTITIONS {PDF_DB_NAME}.{TEXT_TABLE_NAME}").show()


def test_pdf_import_and_extract():
    """Test importing PDF to Hive, extracting text, and storing in another table."""
    try:
        # Setup Spark session
        logger.info("Setting up Spark session with Hive support")
        spark = setup_spark_session()
        
        # Read PDF file into DataFrame
        logger.info(f"Reading PDF file: {PDF_FILE_PATH}")
        pdf_df = read_pdf_to_dataframe(spark, PDF_FILE_PATH)
        
        # Store PDF in Hive
        logger.info("Storing PDF in Hive")
        store_pdf_in_hive(spark, pdf_df)
        
        # Extract text and store in another table
        logger.info("Extracting text from PDF and storing in Hive")
        extract_and_store_text(spark)
        
        # Verify data exists in both tables
        pdf_count = spark.sql(f"SELECT COUNT(*) FROM {PDF_DB_NAME}.{PDF_TABLE_NAME}").collect()[0][0]
        text_count = spark.sql(f"SELECT COUNT(*) FROM {PDF_DB_NAME}.{TEXT_TABLE_NAME}").collect()[0][0]
        
        assert pdf_count > 0, "No PDF records found in Hive"
        assert text_count > 0, "No text records found in Hive"
        
        logger.info(f"PDF records: {pdf_count}, Text records: {text_count}")
        logger.info("Test completed successfully")
        
        # Don't drop the tables as requested by the user
        logger.info("Tables left in Hive for manual inspection")
        
        # Keep the Spark UI running until user presses Enter
        print("\n===== PDF to Hive Test Completed =====")
        print(f"PDF stored in: {PDF_DB_NAME}.{PDF_TABLE_NAME}")
        print(f"Extracted text stored in: {PDF_DB_NAME}.{TEXT_TABLE_NAME}")
        print("Spark UI is available at http://localhost:4040")
        print("Tables have been preserved for manual inspection")
        input("Press Enter to exit and close Spark session...")
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        raise
    finally:
        # Don't close the Spark session to allow for UI inspection
        pass


if __name__ == "__main__":
    test_pdf_import_and_extract() 