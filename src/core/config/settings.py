"""
Application settings module.

This module defines the application settings using Pydantic for validation
and environment variable loading.
"""
from typing import Dict, Any, Optional, List, Literal, Union
import os
from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.fields import FieldInfo

from .m1_optimized_settings import M1SparkSettings, M1MLSettings


class SparkSettings(BaseModel):
    """Spark configuration settings."""
    
    master: str = Field(default="local[*]")
    app_name: str = Field(default="SparkETLMLPipeline")
    executor_memory: str = Field(default="4g")
    driver_memory: str = Field(default="2g")
    executor_cores: int = Field(default=4)
    local_dir: str = Field(default="/tmp/spark-local")
    warehouse_dir: str = Field(default="/tmp/spark-warehouse")
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert settings to a dict for Spark configuration."""
        return {
            "spark.master": self.master,
            "spark.app.name": self.app_name,
            "spark.executor.memory": self.executor_memory,
            "spark.driver.memory": self.driver_memory,
            "spark.executor.cores": str(self.executor_cores),
            "spark.local.dir": self.local_dir,
            "spark.sql.warehouse.dir": self.warehouse_dir,
        }


class HiveSettings(BaseModel):
    """Hive configuration settings."""
    
    host: str = Field(default="localhost")
    port: int = Field(default=10000)
    user: str = Field(default="hive")
    password: str = Field(default="")
    database: str = Field(default="default")
    metastore_uris: str = Field(default="thrift://localhost:9083")


class KafkaSettings(BaseModel):
    """Kafka configuration settings."""
    
    bootstrap_servers: str = Field(default="localhost:9092")
    group_id: str = Field(default="spark-etl-ml-group")
    auto_offset_reset: str = Field(default="earliest")
    schema_registry_url: str = Field(default="http://localhost:8081")


class ApiSettings(BaseModel):
    """API configuration settings."""
    
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=4)
    log_level: str = Field(default="info")
    reload: bool = Field(default=True)
    debug: bool = Field(default=False)


class MLSettings(BaseModel):
    """Machine Learning configuration settings."""
    
    model_dir: str = Field(default="./models")
    training_data_path: str = Field(default="./data/training")
    batch_size: int = Field(default=64)
    epochs: int = Field(default=10)
    learning_rate: float = Field(default=0.001)


class LogSettings(BaseModel):
    """Logging configuration settings."""
    
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file: str = Field(default="logs/application.log")
    max_bytes: int = Field(default=10485760)  # 10MB
    backup_count: int = Field(default=5)


class SecuritySettings(BaseModel):
    """Security configuration settings."""
    
    secret_key: str = Field(default="your-secret-key-here")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_delta: int = Field(default=86400)  # 24 hours


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore"
    )
    
    # Project settings
    project_name: str = Field(default="Spark ETL ML Pipeline")
    version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)
    testing: bool = Field(default=False)
    profile: Literal["default", "dev"] = Field(default="default")
    
    # Component settings
    spark: Union[SparkSettings, M1SparkSettings] = Field(default_factory=SparkSettings)
    hive: HiveSettings = Field(default_factory=HiveSettings)
    kafka: KafkaSettings = Field(default_factory=KafkaSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    ml: Union[MLSettings, M1MLSettings] = Field(default_factory=MLSettings)
    log: LogSettings = Field(default_factory=LogSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    
    @field_validator("spark", "ml", mode="before")
    @classmethod
    def set_profile_settings(cls, v: Any, info: FieldInfo) -> Any:
        """Set profile-specific settings."""
        values = info.data
        field_name = info.field_name
        
        if values.get("profile") == "dev":
            if isinstance(v, dict):
                return M1SparkSettings(**v) if field_name == "spark" else M1MLSettings(**v)
            return M1SparkSettings() if field_name == "spark" else M1MLSettings()
        if isinstance(v, dict):
            return SparkSettings(**v) if field_name == "spark" else MLSettings(**v)
        return v
    
    def get_log_file_path(self) -> Path:
        """Get the absolute path to the log file."""
        log_file = Path(self.log.file)
        if not log_file.is_absolute():
            log_file = Path.cwd() / log_file
        
        # Ensure the directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        return log_file


def get_settings(override_settings: Optional[Dict[str, Any]] = None) -> Settings:
    """
    Get application settings.
    
    Args:
        override_settings: Optional dictionary of settings to override.
        
    Returns:
        Settings: Application settings.
    """
    settings = Settings()
    
    if override_settings:
        for key, value in override_settings.items():
            setattr(settings, key, value)
    
    return settings 