"""
Utils package for the AI Learning backend.
Contains utility functions and helpers.
"""

# Import all utilities to make them available when importing from backend.utils
try:
    from .logger import *
    from .exceptions import *
except ImportError as e:
    print(f"Warning: Could not import some utilities: {e}")
