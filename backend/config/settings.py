from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Centralized Configuration Management.
    Enforces strict validation of environment variables at startup.
    Fails fast if critical variables are missing in production.
    """
    
    # Environment Configuration
    ENVIRONMENT: str = Field(default="development")

    # Critical Database Variables
    MONGO_URI: Optional[str] = Field(
        default=None,
        description="MongoDB connection string. Mandatory for database."
    )
    MONGO_DB: str = Field(
        default="resume_analyzer",
        description="Target MongoDB database name."
    )

    # Authentication & Security
    JWT_SECRET: Optional[str] = Field(
        default=None,
        description="Secret key for JWT generation."
    )

    # AI Provider
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API key for AI generation."
    )

    # External Services
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis connection URL for background jobs."
    )
    
    # Render Specific
    RENDER: bool = Field(default=False, description="Set to true automatically on Render.")

    model_config = SettingsConfigDict(
        env_file=".env" if os.path.exists(".env") else None,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production" or self.RENDER

# Global singleton settings instance
try:
    settings = Settings()
    if settings.is_production and not settings.REDIS_URL:
        settings.REDIS_URL = os.getenv("REDIS_URL")
except Exception as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to load settings: {e}")
    # Create an empty settings object to allow failsafe boot
    settings = Settings(ENVIRONMENT="development")
