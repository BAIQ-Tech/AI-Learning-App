"""
Models package for the AI Learning backend.
Contains all database models and related functionality.
"""

# Import models in dependency order to avoid foreign key issues
try:
    # First import base models from the main models.py file
    import sys
    from pathlib import Path
    
    # Add parent directory to path to import from models.py
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Import base models first (User, etc.)
    from backend.models import *
    
    # Then import extended models that depend on base models
    from .gamification import *
    from .social import *
    
except ImportError as e:
    print(f"Warning: Could not import some models: {e}")
