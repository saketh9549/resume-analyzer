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
    MONGO_URI: str = Field(
        ...,
        description="MongoDB connection string. Required in all environments."
    )
    MONGO_DB: str = Field(
        default="resume_analyzer",
        description="Target MongoDB database name."
    )

    # Authentication & Security
    JWT_SECRET: str = Field(
        ...,
        description="Secret key for JWT generation. Required."
    )

    # AI Provider
    GEMINI_API_KEY: str = Field(
        ...,
        description="Google Gemini API key for AI generation. Required."
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
        settings.REDIS_URL = os.getenv("REDIS_URL") # Try to pull again just in case
except Exception as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.error("=====================================================")
    logger.error("CRITICAL STARTUP ERROR: CONFIGURATION VALIDATION FAILED")
    logger.error("=====================================================")
    logger.error(str(e))
    logger.error("Please verify that all required environment variables are set in the Render Dashboard.")
    # DO NOT call sys.exit(1) here as it abruptly kills the Render deployment without flushing logs properly.
    raise RuntimeError(f"Startup failed due to missing configuration: {str(e)}")
