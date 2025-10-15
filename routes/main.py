"""
Main API routes - Health check and info endpoints
"""
import os
from datetime import datetime

from flask import Blueprint, jsonify

# Create Blueprint
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def health_check():
    """API Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "message": "Flask API is running",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }
    )


@main_bp.route("/info")
def api_info():
    """API information endpoint"""
    from flask import current_app

    from config.database import db
    from models.user import User

    # Get database info
    db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "Unknown")
    users_count = User.query.count()

    return jsonify(
        {
            "api_name": "Flask Modular API",
            "version": "1.0.0",
            "environment": os.environ.get("FLASK_ENV", "development"),
            "database": {
                "uri": db_uri,
                "users_count": users_count,
                "connected": True if db else False,
            },
            "endpoints": {
                "users": "/api/users",
                "posts": "/api/posts",
                "contacts": "/api/contacts",
                "search": "/api/search",
            },
            "documentation": "https://your-api-docs.com",
        }
    )
