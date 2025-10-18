from typing import Any

from flask import Flask
from flask_jwt_extended import JWTManager

from config.auth.auth_config import JWTConfig
from config.database import db
from constants.error_messages import (
    FRESH_TOKEN_REQUIRED,
    INVALID_TOKEN,
    MISSING_TOKEN,
    REVOKED_TOKEN,
    TOKEN_EXPIRED,
)
from constants.http_status import FORBIDDEN, UNAUTHORIZED
from utils.response_helper import ResponseHelper


class AuthApp:
    @staticmethod
    def init_app(app: Flask) -> Any:
        """Initialize authentication-related extensions"""
        jwt_manager = JWTApp.init_app(app)
        return jwt_manager


class JWTApp:
    @staticmethod
    def init_app(app: Flask) -> JWTManager:
        """Initialize JWT Manager with app configuration"""
        app.config["JWT_SECRET_KEY"] = JWTConfig.JWT_SECRET_KEY
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = JWTConfig.JWT_ACCESS_TOKEN_EXPIRES
        app.config["JWT_REFRESH_TOKEN_EXPIRES"] = JWTConfig.JWT_REFRESH_TOKEN_EXPIRES
        app.config["JWT_ALGORITHM"] = JWTConfig.JWT_ALGORITHM
        app.config["JWT_TOKEN_LOCATION"] = JWTConfig.JWT_TOKEN_LOCATION
        app.config["JWT_HEADER_NAME"] = JWTConfig.JWT_HEADER_NAME
        app.config["JWT_HEADER_TYPE"] = JWTConfig.JWT_HEADER_TYPE

        jwt = JWTManager(app)
        JWTApp._setup_jwt_handlers(jwt)

        return jwt

    @staticmethod
    def _setup_jwt_handlers(jwt):
        """Setup JWT error handlers"""

        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return ResponseHelper.error_response(
                message=TOKEN_EXPIRED,
                status_code=UNAUTHORIZED,
            )

        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            return ResponseHelper.error_response(
                message=INVALID_TOKEN,
                status_code=UNAUTHORIZED,
            )

        @jwt.unauthorized_loader
        def missing_token_callback(error):
            return ResponseHelper.error_response(
                message=MISSING_TOKEN,
                status_code=UNAUTHORIZED,
            )

        @jwt.needs_fresh_token_loader
        def token_not_fresh_callback(jwt_header, jwt_payload):
            return ResponseHelper.error_response(
                message=FRESH_TOKEN_REQUIRED,
                status_code=FORBIDDEN,
            )

        @jwt.revoked_token_loader
        def revoked_token_callback(jwt_header, jwt_payload):
            return ResponseHelper.error_response(
                message=REVOKED_TOKEN,
                status_code=UNAUTHORIZED,
            )

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

        @jwt.token_in_blocklist_loader
        def check_if_token_revoked(_jwt_header, jwt_payload):
            """Check if token is in blacklist"""
            from models.token_blacklist import TokenBlacklist

            jti = jwt_payload["jti"]
            return TokenBlacklist.is_token_revoked(jti)
