"""
Main entry point for the application.
This file is used by Render to start the FastAPI application.
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = str(Path(__file__).parent)
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the FastAPI app from the backend module
from backend.main import app as application

# This allows the file to be run directly for local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:application", host="0.0.0.0", port=port, reload=True)
