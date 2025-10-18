"""
API v1 Blueprint
All v1 API endpoints
"""
import importlib
import os

from flask import Blueprint

# Create v1 blueprint
api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# Import all v1 routes
current_dir = os.path.dirname(__file__)
for filename in os.listdir(current_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]
        importlib.import_module(f".{module_name}", __name__)

__all__ = ["api_v1"]
