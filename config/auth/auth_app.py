from flask import Flask
from flask_jwt_extended import JWTManager
from flask_security import Security, SQLAlchemyUserDatastore

from config.auth.auth_config import JWTConfig, SecurityConfig
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
    def init_app(app: Flask) -> None:
        """Initialize authentication-related extensions"""
        JWTApp.init_app(app)
        SecurityApp.init_app(app)


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


class SecurityApp:
    @staticmethod
    def init_app(app: Flask) -> Security:
        """Initialize Flask-Security-Too with app configuration"""
        app.config["SECURITY_REGISTERABLE"] = SecurityConfig.SECURITY_REGISTERABLE
        app.config["SECURITY_RECOVERABLE"] = SecurityConfig.SECURITY_RECOVERABLE
        app.config["SECURITY_CHANGEABLE"] = SecurityConfig.SECURITY_CHANGEABLE
        app.config["SECURITY_CONFIRMABLE"] = SecurityConfig.SECURITY_CONFIRMABLE
        app.config["SECURITY_TRACKABLE"] = SecurityConfig.SECURITY_TRACKABLE
        app.config["SECURITY_URL_PREFIX"] = SecurityConfig.SECURITY_URL_PREFIX
        app.config["SECURITY_LOGIN_URL"] = SecurityConfig.SECURITY_LOGIN_URL
        app.config["SECURITY_LOGOUT_URL"] = SecurityConfig.SECURITY_LOGOUT_URL
        app.config["SECURITY_REGISTER_URL"] = SecurityConfig.SECURITY_REGISTER_URL
        app.config["SECURITY_CHANGE_URL"] = SecurityConfig.SECURITY_CHANGE_URL
        app.config["SECURITY_PASSWORD_HASH"] = SecurityConfig.SECURITY_PASSWORD_HASH
        app.config["SECURITY_PASSWORD_SALT"] = SecurityConfig.SECURITY_PASSWORD_SALT
        app.config[
            "SECURITY_PASSWORD_LENGTH_MIN"
        ] = SecurityConfig.SECURITY_PASSWORD_LENGTH_MIN
        app.config[
            "SECURITY_PASSWORD_COMPLEXITY_CHECKER"
        ] = SecurityConfig.SECURITY_PASSWORD_COMPLEXITY_CHECKER
        app.config["SECURITY_HASHING_SCHEMES"] = SecurityConfig.SECURITY_HASHING_SCHEMES
        app.config[
            "SECURITY_DEPRECATED_HASHING_SCHEMES"
        ] = SecurityConfig.SECURITY_DEPRECATED_HASHING_SCHEMES
        app.config[
            "SECURITY_PASSWORD_SINGLE_HASH"
        ] = SecurityConfig.SECURITY_PASSWORD_SINGLE_HASH
        app.config[
            "SECURITY_TOKEN_AUTHENTICATION_KEY"
        ] = SecurityConfig.SECURITY_TOKEN_AUTHENTICATION_KEY
        app.config[
            "SECURITY_TOKEN_AUTHENTICATION_HEADER"
        ] = SecurityConfig.SECURITY_TOKEN_AUTHENTICATION_HEADER
        app.config[
            "SECURITY_LOGIN_WITHOUT_CONFIRMATION"
        ] = SecurityConfig.SECURITY_LOGIN_WITHOUT_CONFIRMATION
        app.config[
            "JWT_REFRESH_TOKEN_EXPIRES"
        ] = SecurityConfig.JWT_REFRESH_TOKEN_EXPIRES
        app.config["JWT_ALGORITHM"] = SecurityConfig.JWT_ALGORITHM
        app.config[
            "SECURITY_CSRF_PROTECT_MECHANISMS"
        ] = SecurityConfig.SECURITY_CSRF_PROTECT_MECHANISMS
        # CSRF settings for API
        app.config["WTF_CSRF_ENABLED"] = SecurityConfig.WTF_CSRF_ENABLED
        app.config["WTF_CSRF_CHECK_DEFAULT"] = SecurityConfig.WTF_CSRF_CHECK_DEFAULT
        app.config[
            "SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS"
        ] = SecurityConfig.SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS

        # Additional Flask-Security settings
        app.config["SECURITY_FLASH_MESSAGES"] = SecurityConfig.SECURITY_FLASH_MESSAGES
        app.config["SECURITY_WANT_JSON"] = SecurityConfig.SECURITY_WANT_JSON
        app.config["SECRET_KEY"] = SecurityConfig.SECRET_KEY
        app.config[
            "SECURITY_SEND_REGISTER_EMAIL"
        ] = SecurityConfig.SECURITY_SEND_REGISTER_EMAIL
        app.config[
            "SECURITY_SEND_PASSWORD_CHANGE_EMAIL"
        ] = SecurityConfig.SECURITY_SEND_PASSWORD_CHANGE_EMAIL
        app.config[
            "SECURITY_SEND_PASSWORD_RESET_EMAIL"
        ] = SecurityConfig.SECURITY_SEND_PASSWORD_RESET_EMAIL

        from models.role import Role
        from models.user import User

        # Setup Flask-Security
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        security = Security(app, user_datastore)

        return user_datastore, security
