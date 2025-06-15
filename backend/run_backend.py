"""
Script to run the FastAPI backend service.
"""

import os
import sys
from pathlib import Path
import uvicorn


if __name__ == "__main__":
    # Add the project root to the Python path
    project_root = Path(__file__).parent.parent.absolute()
    sys.path.insert(0, str(project_root))
    
    # Run the FastAPI application using uvicorn
    uvicorn.run(
        "backend.app:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
