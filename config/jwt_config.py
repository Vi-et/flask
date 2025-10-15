"""
JWT Authentication Configuration
"""
import os
from datetime import timedelta

from flask_jwt_extended import JWTManager


class JWTConfig:
    """JWT Configuration class"""

    @staticmethod
    def init_app(app):
        """Initialize JWT with Flask app"""

        # JWT Configuration
        app.config["JWT_SECRET_KEY"] = os.getenv(
            "JWT_SECRET_KEY", app.config["SECRET_KEY"]
        )
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
        app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
        app.config["JWT_ALGORITHM"] = "HS256"

        # JWT Location (where to look for tokens)
        app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
        app.config["JWT_HEADER_NAME"] = "Authorization"
        app.config["JWT_HEADER_TYPE"] = "Bearer"

        # JWT Error Messages
        app.config["JWT_ERROR_MESSAGE_KEY"] = "message"

        # Initialize JWT Manager
        jwt = JWTManager(app)

        # JWT Error Handlers
        JWTConfig._setup_jwt_handlers(jwt)

        return jwt

    @staticmethod
    def _setup_jwt_handlers(jwt):
        """Setup JWT error handlers"""

        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return {
                "success": False,
                "message": "Token has expired",
                "error": "token_expired",
            }, 401

        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            return {
                "success": False,
                "message": "Invalid token",
                "error": "invalid_token",
            }, 401

        @jwt.unauthorized_loader
        def missing_token_callback(error):
            return {
                "success": False,
                "message": "Authorization token is required",
                "error": "missing_token",
            }, 401

        @jwt.needs_fresh_token_loader
        def token_not_fresh_callback(jwt_header, jwt_payload):
            return {
                "success": False,
                "message": "Fresh token required",
                "error": "fresh_token_required",
            }, 401

        @jwt.revoked_token_loader
        def revoked_token_callback(jwt_header, jwt_payload):
            return {
                "success": False,
                "message": "Token has been revoked",
                "error": "token_revoked",
            }, 401

        @jwt.user_identity_loader
        def user_identity_lookup(user):
            """Define how to serialize user for JWT"""
            return user.id if hasattr(user, "id") else user

        @jwt.user_lookup_loader
        def user_lookup_callback(_jwt_header, jwt_data):
            """Define how to load user from JWT"""
            from models.user import User

            identity = jwt_data["sub"]
            return User.query.filter_by(id=identity).first()
