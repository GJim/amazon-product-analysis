"""
Configuration settings for the Amazon Product Analysis backend.
"""

import os
from typing import List, Union
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment settings
    environment: str = os.environ.get("ENVIRONMENT", "development")
    debug: bool = bool(os.environ.get("DEBUG", True))

    # Server settings
    app_name: str = "Amazon Product Analysis API"
    app_version: str = "1.0.0"
    app_description: str = (
        "API for analyzing Amazon product pages with WebSocket support"
    )
    host: str = "0.0.0.0"
    port: int = int(os.environ.get("PORT", 8000))

    # API endpoint settings
    api_prefix: str = "/api"
    api_tags: List[str] = ["API"]

    # Task status constants
    task_status_pending: str = "pending"
    task_status_running: str = "running"
    task_status_success: str = "success"
    task_status_error: str = "error"

    # Redis settings
    redis_host: str = os.environ.get("REDIS_HOST", "localhost")
    redis_port: int = int(os.environ.get("REDIS_PORT", 6379))
    redis_password: str = os.environ.get("REDIS_PASSWORD", "")
    redis_db: int = int(os.environ.get("REDIS_DB", 0))
    redis_channel_prefix: str = os.environ.get(
        "REDIS_CHANNEL_PREFIX", "product_analysis"
    )

    # Database settings
    db_username: str = os.environ.get("DB_USERNAME", "postgres")
    db_password: str = os.environ.get("DB_PASSWORD", "postgres")
    db_host: str = os.environ.get("DB_HOST", "localhost")
    db_port: int = int(os.environ.get("DB_PORT", 5432))
    db_name: str = os.environ.get("DB_NAME", "amazon_product_analysis")

    # CORS settings
    allowed_origins: str = os.environ.get("ALLOWED_ORIGINS", "").split(",")

    # Computed database URL
    @property
    def database_url(self) -> str:
        """Generate database URL from components."""
        return f"postgresql+psycopg://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # CORS settings
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        return self.allowed_origins.split(",")

    # Security settings
    @property
    def security_headers(self) -> dict:
        """Security headers for production environment."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        }

    # Cookie settings
    @property
    def cookie_settings(self) -> dict:
        """Secure cookie settings for production environment."""
        return {"httponly": True, "secure": True, "samesite": "lax"}

    # Rate limiting settings
    rate_limit_enabled: bool = bool(os.environ.get("RATE_LIMIT_ENABLED", False))
    rate_limit_requests: int = int(os.environ.get("RATE_LIMIT_REQUESTS", 100))
    rate_limit_timespan: int = int(os.environ.get("RATE_LIMIT_TIMESPAN", 60))

    class Config:
        """Pydantic configuration."""

        env_file = ".env.backend"
        case_sensitive = False


# Create global settings instance
settings = Settings()
