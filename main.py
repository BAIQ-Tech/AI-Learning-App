"""
Main entry point for the application.
This file is used by Render to start the FastAPI application.
"""
import os
import sys
from pathlib import Path

# Add the project root and backend directory to Python path
project_root = str(Path(__file__).parent)
backend_path = str(Path(__file__).parent / 'backend')

for path in [project_root, backend_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import the FastAPI app from the backend module
from backend.main import app as application

# This allows the file to be run directly for local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:application", host="0.0.0.0", port=port, reload=True)
