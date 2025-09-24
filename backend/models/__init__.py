"""
Models package for the AI Learning backend.
Contains all database models and related functionality.
"""

# Import all models to make them available when importing from backend.models
try:
    from .gamification import *
    from .social import *
except ImportError as e:
    print(f"Warning: Could not import some models: {e}")
