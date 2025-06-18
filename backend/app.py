"""
FastAPI application for the Amazon Product Analysis backend with WebSocket support.
This server connects to Redis, subscribes to task channels, and relays messages
to connected web clients via WebSockets.
"""

import logging
import os
import time
import traceback
from pathlib import Path
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config import settings
from backend.routes import api_router, ws_router
from backend.services import redis_service

# Configure logging
log_level = logging.DEBUG if settings.debug else logging.INFO
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app with environment-specific settings
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
    docs_url=None if settings.environment == "production" else "/docs",
    redoc_url=None if settings.environment == "production" else "/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=(
        ["GET", "POST", "PUT", "DELETE"]
        if settings.environment == "production"
        else ["*"]
    ),
    allow_headers=(
        ["Content-Type", "Authorization"]
        if settings.environment == "production"
        else ["*"]
    ),
)


# Rate limiting middleware for production mode
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""

    def __init__(self, app, requests_limit: int = 100, timespan: int = 60):
        """Initialize rate limiting middleware.

        Args:
            app: The FastAPI application
            requests_limit: Maximum number of requests allowed per timespan
            timespan: Time window in seconds for rate limiting
        """
        super().__init__(app)
        self.requests_limit = requests_limit
        self.timespan = timespan
        self.clients = {}

    async def dispatch(self, request: Request, call_next):
        """Process each request for rate limiting."""
        # Skip rate limiting if not enabled
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host
        current_time = time.time()

        # Clean up old entries
        if client_ip in self.clients:
            self.clients[client_ip] = [
                ts
                for ts in self.clients[client_ip]
                if current_time - ts < self.timespan
            ]
        else:
            self.clients[client_ip] = []

        # Check rate limit
        if len(self.clients[client_ip]) >= self.requests_limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
            )

        # Add current request timestamp
        self.clients[client_ip].append(current_time)

        # Process the request
        return await call_next(request)


# Add security middlewares for production
if settings.environment == "production":
    # Only allow requests from trusted hosts
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"] + settings.cors_origins,
    )

    # Enable GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Add rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        requests_limit=settings.rate_limit_requests,
        timespan=settings.rate_limit_timespan,
    )


# Add security headers and cookie settings middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Add security headers in production
    if settings.environment == "production":
        for header_name, header_value in settings.security_headers.items():
            response.headers[header_name] = header_value

    # Apply secure cookie settings to all cookies
    for cookie in response.headers.getlist("set-cookie"):
        if cookie:
            # Apply secure cookie settings based on environment
            cookie_settings = settings.cookie_settings
            if "httponly" not in cookie.lower() and cookie_settings["httponly"]:
                response.headers["set-cookie"] = f"{cookie}; HttpOnly"
            if "secure" not in cookie.lower() and cookie_settings["secure"]:
                response.headers["set-cookie"] = f"{cookie}; Secure"
            if "samesite" not in cookie.lower():
                response.headers["set-cookie"] = (
                    f"{cookie}; SameSite={cookie_settings['samesite']}"
                )

    return response


# Exception handlers for better error handling and security
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with appropriate response."""
    error_detail = exc.errors()
    # In production, don't expose detailed error information
    if settings.environment == "production":
        error_detail = [
            {"msg": "Validation error", "loc": err["loc"]} for err in error_detail
        ]

    return JSONResponse(
        status_code=422,
        content={"detail": error_detail},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with appropriate response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with appropriate response."""
    logger.error(f"Unhandled exception: {str(exc)}")
    if settings.debug:
        error_detail = f"{str(exc)}\n{traceback.format_exc()}"
    else:
        error_detail = "Internal server error"

    return JSONResponse(
        status_code=500,
        content={"detail": error_detail},
    )


# Include API and WebSocket routers
app.include_router(api_router)
app.include_router(ws_router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    await redis_service.initialize()
    logger.info(
        f"{settings.app_name} started successfully in {settings.environment} mode"
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await redis_service.shutdown()
    logger.info(f"{settings.app_name} shutdown complete")
