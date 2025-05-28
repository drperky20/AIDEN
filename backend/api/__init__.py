"""
AIDEN V2 API Package

This package exposes the FastAPI application (`app` from `main.py`) 
and the main API router (`router` from `routes.py`).
"""

from .main import app
from .routes import router

__all__ = ["app", "router"] 