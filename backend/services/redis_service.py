"""
Redis service for managing connections and subscriptions.
"""

import asyncio
import logging
import redis.asyncio as redis
from typing import Dict, Any, Optional

from backend.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class RedisService:
    """Service for managing Redis connections and operations."""

    def __init__(self):
        """Initialize the Redis service."""
        self.pool: Optional[redis.ConnectionPool] = None
        self.active_subscriptions: Dict[str, asyncio.Task] = {}

    async def initialize(self):
        """Initialize the Redis connection pool."""
        if not self.pool:
            connection_kwargs = {
                "host": settings.redis_host,
                "port": settings.redis_port,
                "db": settings.redis_db,
                "decode_responses": True,
            }

            # Add password if configured
            if settings.redis_password:
                connection_kwargs["password"] = settings.redis_password

            self.pool = redis.ConnectionPool(**connection_kwargs)
            logger.info(f"Redis connection pool initialized")

    async def get_connection(self) -> redis.Redis:
        """Get a Redis connection from the pool."""
        if not self.pool:
            await self.initialize()
        return redis.Redis(connection_pool=self.pool)

    def add_subscription(self, channel_name: str, task: asyncio.Task):
        """Add a subscription task to the active subscriptions."""
        self.active_subscriptions[channel_name] = task
        logger.info(f"Created new Redis subscription for {channel_name}")

    def remove_subscription(self, channel_name: str):
        """Remove a subscription task from active subscriptions."""
        if channel_name in self.active_subscriptions:
            if not self.active_subscriptions[channel_name].done():
                self.active_subscriptions[channel_name].cancel()
            del self.active_subscriptions[channel_name]
            logger.info(f"Removed Redis subscription for {channel_name}")

    async def shutdown(self):
        """Clean up Redis resources."""
        # Cancel all active subscriptions
        for channel, task in self.active_subscriptions.items():
            if not task.done():
                task.cancel()

        # Clear subscription dictionary
        self.active_subscriptions.clear()

        # Close Redis connection pool
        if self.pool:
            await self.pool.disconnect()
        logger.info("Redis resources cleaned up")


# Create a global instance of the Redis service
redis_service = RedisService()
