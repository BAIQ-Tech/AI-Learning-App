"""
Routes package for the AI Learning backend.
Contains all API route definitions.
"""

# Import all routes to make them available when importing from backend.routes
try:
    from .ai_routes import *
    from .analytics_routes import *
except ImportError as e:
    print(f"Warning: Could not import some routes: {e}")
