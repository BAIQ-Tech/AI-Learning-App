"""
Backend package for the AI Learning application.
This package contains all the backend logic, API endpoints, and database models.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path if not already present
backend_path = str(Path(__file__).parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import database models to ensure they are registered with SQLAlchemy
try:
    from .database import Base, engine
    from .models import *  # Import all models to ensure they are registered with SQLAlchemy
    
    # Note: Table creation is handled by the main application init_db() function
    # to avoid circular imports and ensure proper model loading order
    
    __all__ = ['Base', 'engine']  # Make Base and engine available when importing from backend
    
except ImportError as e:
    print(f"Warning: Could not initialize database models: {e}")
    __all__ = []
