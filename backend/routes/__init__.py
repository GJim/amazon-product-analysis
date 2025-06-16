"""
Routes module for the Amazon Product Analysis backend.
"""
from backend.routes.api import router as api_router
from backend.routes.ws import router as ws_router

__all__ = ["api_router", "ws_router"]
