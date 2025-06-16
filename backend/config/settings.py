"""
Configuration settings for the Amazon Product Analysis backend.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server settings
    APP_NAME: str = "Amazon Product Analysis API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "API for analyzing Amazon product pages with WebSocket support"
    )

    # Redis settings
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))

    # Database settings
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/amazon_product_analysis",
    )

    # OpenAI settings
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = int(os.environ.get("PORT", 8000))

    # CORS settings
    CORS_ORIGINS: list = ["*"]  # For production, restrict to your frontend domain

    class Config:
        env_file = ".env"


# Create global settings instance
settings = Settings()
