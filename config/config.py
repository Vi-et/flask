"""
Application Configuration
"""
import os
from datetime import timedelta


class Config:
    """Base configuration class"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key-here"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database
    # Option 1: Use environment variable (recommended)
    # Option 2: Use PostgreSQL directly (uncomment line below)
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://flask_user:flask_password_123@localhost:5432/flask_dev"
    )
    # Old SQLite: "sqlite:///blog.db"

    # Pagination
    POSTS_PER_PAGE = 5
    USERS_PER_PAGE = 10

    # API Settings
    API_VERSION = "1.0.0"
    APP_NAME = "My Flask App"


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = False
    SQLALCHEMY_ECHO = False  # Log SQL queries


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # In-memory database for tests
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
