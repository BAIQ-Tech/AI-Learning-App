"""
WSGI config for production.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = str(Path(__file__).parent / 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
