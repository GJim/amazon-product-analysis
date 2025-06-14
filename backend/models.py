"""
Data models for the FastAPI backend.
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional


class ProductAnalysisRequest(BaseModel):
    """Request model for product analysis."""

    url: HttpUrl = Field(..., description="Amazon product URL to analyze")
    max_products: int = Field(
        10, description="Maximum number of products to collect", ge=1, le=50
    )
    max_competitive: int = Field(
        5, description="Maximum number of competitive products to analyze", ge=1, le=20
    )


class TaskResponse(BaseModel):
    """Response model with task ID."""

    task_id: str = Field(
        ..., description="Celery task ID for tracking the analysis job"
    )
    status: str = Field("pending", description="Initial status of the task")


class TaskStatusResponse(BaseModel):
    """Response model for task status."""

    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(
        ..., description="Status of the task (pending, running, success, error)"
    )
    result: Optional[dict] = Field(
        None, description="Analysis results if task is completed"
    )
