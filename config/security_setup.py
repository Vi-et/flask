"""
Flask-Security-Too Setup with JWT
"""
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_security import Security, SQLAlchemyUserDatastore
from flask_wtf.csrf import CSRFProtect

from config.database import db


def init_security(app: Flask) -> tuple:
    """Initialize Flask-Security-Too with JWT"""

    # Initialize JWT Manager
    JWTManager(app)

    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = app.config.get("SECRET_KEY", "jwt-secret-string")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = app.config.get(
        "JWT_ACCESS_TOKEN_EXPIRES", 3600
    )
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = app.config.get(
        "JWT_REFRESH_TOKEN_EXPIRES", 2592000
    )  # 30 days

    # Initialize CSRF protection (required by Flask-Security)
    CSRFProtect(app)

    # Import models after app context is available
    from models.role import Role
    from models.user import User

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Flask-Security sẽ tự động tạo các endpoints:
    # POST /api/auth/login    - Login và nhận token
    # POST /api/auth/register - Register user
    # POST /api/auth/logout   - Logout

    return security, user_datastore
