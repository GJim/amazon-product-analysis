"""Configuration settings for the Amazon product analysis application."""

import os

# Redis configuration
REDIS_HOST = str(os.getenv("REDIS_HOST", "localhost"))
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_BROKER_DB = int(os.getenv("REDIS_BROKER_DB", 1))
REDIS_BACKEND_DB = int(os.getenv("REDIS_BACKEND_DB", 2))
REDIS_PASSWORD = str(os.getenv("REDIS_PASSWORD", ""))  # Change in production
REDIS_CHANNEL_PREFIX = str(os.getenv("REDIS_CHANNEL_PREFIX", "product_analysis"))
