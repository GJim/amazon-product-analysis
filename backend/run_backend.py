"""
Script to run the FastAPI backend service with WebSocket support.
"""

import os
import sys
from pathlib import Path
import uvicorn

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Import settings after adding project root to path
from backend.config import settings


if __name__ == "__main__":
    # Run the FastAPI application using uvicorn with settings from config
    uvicorn.run(
        "backend.app:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=True, 
        log_level="info"
    )
