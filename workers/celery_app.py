"""
Celery app configuration for Amazon Product Analysis workers.
"""

from celery import Celery
from workers.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_BROKER_DB,
    REDIS_BACKEND_DB,
    REDIS_PASSWORD,
)

# Create the Celery app instance
celery_app = Celery(
    "amazon_product_analysis",
    broker=f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}",
    backend=f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_BACKEND_DB}",
    include=["workers.tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Specify queue names
celery_app.conf.task_routes = {
    "workers.tasks.*": {"queue": "analysis_agent"},
}
