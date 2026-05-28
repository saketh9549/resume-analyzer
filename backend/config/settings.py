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
        default="redis://localhost:6379/0",
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
except Exception as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.error("CRITICAL ERROR: Failed to load environment variables. Are you missing required variables like MONGO_URI?")
    logger.error(str(e))
    # If we are in production, fail fast.
    if os.getenv("ENVIRONMENT") == "production" or os.getenv("RENDER"):
        import sys
        sys.exit(1)
    else:
        raise
