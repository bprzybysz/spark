"""
Dependency Injection Container module.

This module defines the application's dependency injection container using dependency-injector.
It provides a centralized way to configure and provide dependencies throughout the application.
"""
from typing import Dict, Any, Optional

from dependency_injector import containers, providers

from src.core.config.settings import Settings
from src.core.logging.logger import LoggerFactory, Logger


class Container(containers.DeclarativeContainer):
    """Application container for dependency injection."""

    config = providers.Singleton(Settings)

    # Core providers
    logger_factory = providers.Factory(
        LoggerFactory,
        log_level=config.provided.log.level,
        log_format=config.provided.log.format,
        log_file=config.provided.log.file,
    )

    # Data providers (placeholders - will be implemented in respective modules)
    hive_client = providers.Singleton(
        lambda: None,  # Will be replaced with actual implementation
        config=config.provided.hive,
    )

    spark_session = providers.Singleton(
        lambda: None,  # Will be replaced with actual implementation
        config=config.provided.spark,
    )

    kafka_producer = providers.Factory(
        lambda: None,  # Will be replaced with actual implementation
        config=config.provided.kafka,
    )

    kafka_consumer = providers.Factory(
        lambda: None,  # Will be replaced with actual implementation
        config=config.provided.kafka,
    )

    # ML providers (placeholders - will be implemented in respective modules)
    model_registry = providers.Singleton(
        lambda: None,  # Will be replaced with actual implementation
        config=config.provided.ml,
    )

    # API providers (placeholders - will be implemented in respective modules)
    api_app = providers.Singleton(
        lambda: None,  # Will be replaced with actual implementation
        config=config.provided.api,
    )

    # Schema providers (placeholders - will be implemented in respective modules)
    schema_registry = providers.Singleton(
        lambda: None,  # Will be replaced with actual implementation
    )


_container: Optional[Container] = None


def get_container() -> Container:
    """
    Get the global container instance.
    
    Returns:
        Container instance
    """
    global _container
    if _container is None:
        _container = Container()
    return _container


def set_container(container: Container) -> None:
    """
    Set the global container instance.
    
    Args:
        container: Container instance to set
    """
    global _container
    _container = container


def get_container(override_config: Dict[str, Any] = None) -> Container:
    """
    Create and configure a dependency injection container.

    Args:
        override_config: Optional configuration overrides.

    Returns:
        Container: Configured dependency injection container.
    """
    container = Container()
    
    if override_config:
        container.config.override(override_config)
    
    return container 