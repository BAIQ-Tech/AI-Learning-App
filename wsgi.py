"""
WSGI config for production.
"""
import os
import sys
from pathlib import Path

# Add project root and backend to Python path
project_root = str(Path(__file__).parent)
backend_path = str(Path(__file__).parent / 'backend')

# Add paths to Python path if not already present
for path in [project_root, backend_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Set environment variables
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('PYTHONPATH', project_root)

# Import the FastAPI app after setting up the path
from backend.main import app as application

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    import uvicorn
    uvicorn.run("main:application", host="0.0.0.0", port=port, reload=False)
