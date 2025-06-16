"""
FastAPI application for the Amazon Product Analysis backend with WebSocket support.
This server connects to Redis, subscribes to task channels, and relays messages
to connected web clients via WebSockets.
"""

import logging
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.routes import api_router, ws_router
from backend.services import redis_service

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API and WebSocket routers
app.include_router(api_router)
app.include_router(ws_router)

# Absolute path to /frontend/out
client_dir = Path(__file__).parent.parent / "frontend" / "out"

# Serve the frontend (Next.js export) at the root path
if client_dir.exists():
    app.mount("/", StaticFiles(directory=client_dir, html=True), name="frontend")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    await redis_service.initialize()
    logger.info(f"{settings.APP_NAME} started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await redis_service.shutdown()
    logger.info(f"{settings.APP_NAME} shutdown complete")
