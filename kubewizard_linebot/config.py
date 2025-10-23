from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # AI Configuration
    ai_google_api_key: str = Field(..., env="AI_GOOGLE_API_KEY")
    ai_model: str = Field(default="gemini-2.0-flash", env="AI_MODEL")
    ai_temperature: float = Field(default=0.7, env="AI_TEMPERATURE")
    
    # LINE Bot Configuration
    line_channel_secret: str = Field(default="your_channel_secret_here", env="LINE_CHANNEL_SECRET")
    line_channel_access_token: str = Field(default="your_access_token_here", env="LINE_CHANNEL_ACCESS_TOKEN")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Application Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug_level: int = Field(default=1, env="DEBUG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # 忽略額外的環境變數


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def validate_required_settings():
    """Validate that all required settings are present."""
    required_fields = [
        "ai_google_api_key"
    ]
    
    missing_fields = []
    for field in required_fields:
        if not getattr(settings, field, None):
            missing_fields.append(field.upper())
    
    if missing_fields:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")
    
    return True