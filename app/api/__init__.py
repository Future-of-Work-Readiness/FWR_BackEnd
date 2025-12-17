"""
API package.
Contains versioned API endpoints.
"""

from .v1 import api_router

__all__ = ["api_router"]
