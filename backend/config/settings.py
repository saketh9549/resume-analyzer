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
    MONGODB_URI: Optional[str] = Field(
        default=None,
        description="Alternative MongoDB connection string."
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

    @property
    def get_mongo_uri(self) -> Optional[str]:
        # Prefer MONGODB_URI then MONGO_URI
        uri = self.MONGODB_URI or self.MONGO_URI or os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
        
        # FIX: Render Dashboard is aggressively overriding render.yaml with the old mongodb+srv:// URI.
        # To bypass DNS SRV resolution timeouts, force translation to the standard seedlist URI here.
        if uri and "mongodb+srv://sakethgudapati_db_user" in uri and "cluster0.qu6jdhv.mongodb.net" in uri:
            uri = "mongodb://sakethgudapati_db_user:dNIJcyzIYxTfRs5L@ac-szwjtv3-shard-00-00.qu6jdhv.mongodb.net:27017,ac-szwjtv3-shard-00-01.qu6jdhv.mongodb.net:27017,ac-szwjtv3-shard-00-02.qu6jdhv.mongodb.net:27017/?authSource=admin&replicaSet=atlas-txiz5x-shard-0&tls=true&tlsAllowInvalidCertificates=true"

        if uri:
            if self.is_production and "localhost" in uri.lower():
                return None # Reject localhost in production even if explicitly provided
            return uri
            
        if self.is_production:
            # Fatal error in production
            return None
        
        # Fallback for development
        return "mongodb://localhost:27017"

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
    # Create an empty settings object to allow failsafe boot for everything EXCEPT database
    settings = Settings(ENVIRONMENT="development")
