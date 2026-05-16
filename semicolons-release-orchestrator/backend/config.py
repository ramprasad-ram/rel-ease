"""
Configuration management for the Release Orchestration Platform.
Supports multiple environments: development, production, testing.
"""
from typing import TYPE_CHECKING, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Release Orchestration Platform"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./release_orchestrator.db"
    database_url_prod: Optional[str] = None
    database_echo: bool = False
    
    # Mock CI/CD Settings
    mock_cicd_enabled: bool = True
    mock_cicd_delay_min: int = 2
    mock_cicd_delay_max: int = 5
    mock_cicd_failure_rate: float = 0.1  # 10% failure rate
    
    # AI Agent Settings
    ai_agent_enabled: bool = True
    ai_agent_confidence_threshold: float = 0.7
    ai_agent_timeout: int = 30
    
    # Workflow Settings
    workflow_max_retries: int = 3
    workflow_retry_delay: int = 5
    
    # Slack Integration
    slack_webhook_url: Optional[str] = None
    slack_enabled: bool = False
    
    # Rollback Agent Settings
    rollback_agent_enabled: bool = True
    rollback_error_threshold: float = 0.15  # 15% error rate
    rollback_critical_threshold: float = 0.30  # 30% error rate
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class DevelopmentSettings(Settings):
    """Development environment settings."""
    debug: bool = True
    database_echo: bool = True
    log_level: str = "DEBUG"


class ProductionSettings(Settings):
    """Production environment settings."""
    debug: bool = False
    database_echo: bool = False
    log_level: str = "WARNING"
    
    def model_post_init(self, __context) -> None:
        """Override database_url with production URL if available."""
        if self.database_url_prod:
            object.__setattr__(self, 'database_url', self.database_url_prod)


class TestingSettings(Settings):
    """Testing environment settings."""
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./test_release_orchestrator.db"
    database_echo: bool = False
    log_level: str = "DEBUG"
    mock_cicd_delay_min: int = 0
    mock_cicd_delay_max: int = 1


@lru_cache()
def get_settings(environment: str = "development") -> Settings:
    """
    Get settings based on environment.
    
    Args:
        environment: Environment name (development, production, testing)
        
    Returns:
        Settings instance for the specified environment
    """
    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "testing": TestingSettings,
    }
    
    settings_class = settings_map.get(environment.lower(), DevelopmentSettings)
    return settings_class()


# Default settings instance
settings = get_settings()

# Made with Bob
