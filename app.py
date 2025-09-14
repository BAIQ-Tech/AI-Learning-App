"""
Main entry point for the FastAPI application.
This file is needed for Render to properly import the application.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = str(Path(__file__).parent / 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Import the FastAPI app
from main import app

# This allows the file to be run directly for local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
