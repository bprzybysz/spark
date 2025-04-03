"""Setup file for the Spark ETL ML Pipeline project."""

from setuptools import setup, find_packages

setup(
    name="spark-etl-ml",
    version="0.1.0",
    description="A Spark ETL pipeline with ML capabilities",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "pyspark>=3.0.0",
        "numpy>=1.19.0",
        "pandas>=1.0.0",
        "scikit-learn>=0.24.0",
        "pytest>=6.0.0",
        "pytest-cov>=2.10.0"
    ],
    python_requires=">=3.8"
) 