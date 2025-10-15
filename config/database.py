"""
Database initialization and utilities
"""
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()


def init_database(app):
    """Initialize database with sample data"""
    with app.app_context():
        # Create tables
        db.create_all()


def create_app_context(app):
    """Create application context for CLI commands"""
    return app.app_context()
