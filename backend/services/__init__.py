"""
Services package for the AI Learning backend.
Contains all business logic services.
"""

# Import all services to make them available when importing from backend.services
try:
    from .ai_service import *
    from .analytics_service import *
    from .gamification_service import *
    from .social_service import *
except ImportError as e:
    print(f"Warning: Could not import some services: {e}")
