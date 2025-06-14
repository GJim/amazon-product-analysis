"""
Celery app configuration for Amazon Product Analysis workers.
"""

from celery import Celery

# Create the Celery app instance
celery_app = Celery(
    "amazon_product_analysis",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
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
