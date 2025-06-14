"""
FastAPI application for the Amazon Product Analysis backend.
"""
import logging
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult

from backend.models import ProductAnalysisRequest, TaskResponse, TaskStatusResponse
from workers.tasks import analyze_product

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Amazon Product Analysis API",
    description="API for analyzing Amazon product pages",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint that returns API information."""
    return {
        "name": "Amazon Product Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "Submit a product URL for analysis",
            "/task/{task_id}": "Check the status of a submitted analysis task"
        }
    }


@app.post("/analyze", response_model=TaskResponse)
async def analyze_product_url(request: ProductAnalysisRequest):
    """
    Submit an Amazon product URL for analysis.
    
    The analysis will be performed asynchronously, and a task ID will be returned
    for tracking the progress.
    """
    try:
        logger.info(f"Received analysis request for URL: {request.url}")
        
        # Submit the task to Celery
        task = analyze_product.delay(
            amazon_url=str(request.url),
            max_products=request.max_products,
            max_competitive=request.max_competitive
        )
        
        logger.info(f"Task submitted with ID: {task.id}")
        
        # Return the task ID to the client
        return TaskResponse(task_id=task.id, status="pending")
    
    except Exception as e:
        logger.error(f"Error submitting analysis task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit analysis task: {str(e)}"
        )


@app.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a previously submitted analysis task.
    
    Returns the current status and, if completed, the analysis results.
    """
    try:
        # Get the task result from Celery
        task_result = AsyncResult(task_id)
        
        # Check the status
        if task_result.state == 'PENDING':
            response = TaskStatusResponse(
                task_id=task_id,
                status="pending",
                result=None
            )
        elif task_result.state == 'STARTED':
            response = TaskStatusResponse(
                task_id=task_id,
                status="running",
                result=None
            )
        elif task_result.state == 'SUCCESS':
            response = TaskStatusResponse(
                task_id=task_id,
                status="success",
                result=task_result.result
            )
        elif task_result.state == 'FAILURE':
            response = TaskStatusResponse(
                task_id=task_id,
                status="error",
                result={"error": str(task_result.result)}
            )
        else:
            response = TaskStatusResponse(
                task_id=task_id,
                status=task_result.state.lower(),
                result=None
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving task status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve task status: {str(e)}"
        )
