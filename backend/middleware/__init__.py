"""
Middleware package for the AI Learning backend.
Contains all middleware components.
"""

# Import all middleware to make them available when importing from backend.middleware
try:
    from .monitoring import *
    from .rate_limiter import *
except ImportError as e:
    print(f"Warning: Could not import some middleware: {e}")
