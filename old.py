"""
OLD AUTHENTICATION FILES - BACKUP BEFORE REBUILD
==============================================

This file contains all the old authentication-related code that was removed
during the authentication system rebuild. Keep for reference.

Files included:
- config/security_config.py
- config/security_setup.py  
- config/jwt_config.py
- routes/auth.py
- routes/protected.py
- validators/auth_validators.py
- utils/auth_decorators.py
- test_security_setup.py
"""

# ==============================================================================
# FILE: config/security_config.py
# ==============================================================================

"""
Flask-Security-Too Configuration
"""
import os
from datetime import timedelta


class SecurityConfig:
    """Flask-Security-Too configuration"""

    # Basic Security Settings
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_CONFIRMABLE = False  # Disable email confirmation for now
    SECURITY_TRACKABLE = True

    # Password Settings
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", "ntn_mommy")
    SECURITY_PASSWORD_LENGTH_MIN = 8
    SECURITY_PASSWORD_COMPLEXITY_CHECKER = None  # Disable for now

    # Fix bcrypt 72-byte limit
    SECURITY_HASHING_SCHEMES = ["bcrypt"]
    SECURITY_DEPRECATED_HASHING_SCHEMES: list[str] = []

    # Disable HMAC double hashing that causes 72-byte limit issues
    SECURITY_PASSWORD_SINGLE_HASH = True

    # Session Settings
    SECURITY_SESSION_PROTECTION = "strong"
    SECURITY_FRESH_LOGIN_WITHIN = timedelta(minutes=15)

    # Token Authentication (Flask-Security built-in)
    SECURITY_TOKEN_AUTHENTICATION_KEY = "auth-token"  # Response key name
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"  # Header name
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True  # Skip email confirmation
    
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # 30 days
    JWT_ALGORITHM = "HS256"
    

    # CSRF settings for API
    WTF_CSRF_ENABLED = False
    WTF_CSRF_CHECK_DEFAULT = False
    SECURITY_CSRF_PROTECT_MECHANISMS: list[str] = []
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True

    # URL Settings
    SECURITY_URL_PREFIX = "/api/auth"
    SECURITY_LOGIN_URL = "/login"
    SECURITY_LOGOUT_URL = "/logout"
    SECURITY_REGISTER_URL = "/register"
    SECURITY_CHANGE_URL = "/change-password"

    # Flash Messages (disable for API)
    SECURITY_FLASH_MESSAGES = False

    # JSON Responses
    SECURITY_WANT_JSON = True  # Return JSON responses instead of HTML

    # Secret Key
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-super-secret-key-change-this")

    # Additional Settings
    SECURITY_SEND_REGISTER_EMAIL = False  # Disable registration emails
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_SEND_PASSWORD_RESET_EMAIL = False


# ==============================================================================
# FILE: config/security_setup.py
# ==============================================================================

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


# ==============================================================================
# FILE: config/jwt_config.py
# ==============================================================================

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

        @jwt.token_in_blocklist_loader
        def check_if_token_revoked(_jwt_header, jwt_payload):
            """Check if token is in blacklist"""
            from models.token_blacklist import TokenBlacklist

            jti = jwt_payload["jti"]
            return TokenBlacklist.is_token_revoked(jti)


# ==============================================================================
# FILE: routes/auth.py
# ==============================================================================

"""
Authentication API endpoints
Routes for user registration, login, logout, and profile management
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.auth_service import AuthService
from utils.auth_decorators import auth_required, fresh_jwt_required
from utils.response_helper import ResponseHelper
from utils.route_decorators import log_api_route

# Create Blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
@log_api_route("auth", "register")
def register():
    """
    POST /api/auth/register
    Register a new user
    """
    data = request.get_json()
    result = AuthService.register_user(data)
    return ResponseHelper.service_response(result)


@auth_bp.route("/login", methods=["POST"])
@log_api_route("auth", "login")
def login():
    """
    POST /api/auth/login
    Login user with email and password
    """
    data = request.get_json()
    result = AuthService.login_user(data)
    return ResponseHelper.service_response(result)


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@log_api_route("auth", "refresh_token")
def refresh():
    """
    POST /api/auth/refresh
    Refresh access token using refresh token
    """
    result = AuthService.refresh_token()
    return ResponseHelper.service_response(result)


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
@log_api_route("auth", "logout")
def logout():
    """
    POST /api/auth/logout
    Logout user (invalidate token)
    """
    result = AuthService.logout_user()
    return ResponseHelper.service_response(result)


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
@log_api_route("auth", "get_profile")
def get_profile():
    """
    GET /api/auth/me
    Get current user profile
    """
    result = AuthService.get_current_user()
    return ResponseHelper.service_response(result)


@auth_bp.route("/me", methods=["PUT"])
@jwt_required()
@log_api_route("auth", "update_profile")
def update_profile():
    """
    PUT /api/auth/me
    Update current user profile
    """
    data = request.get_json()
    result = AuthService.update_user_profile(data)
    return ResponseHelper.service_response(result)


@auth_bp.route("/change-password", methods=["PUT"])
@fresh_jwt_required()
@log_api_route("auth", "change_password")
def change_password():
    """
    PUT /api/auth/change-password
    Change user password (requires fresh token)
    Note: Should revoke all user tokens after password change
    """
    data = request.get_json()
    result = AuthService.change_password(data)
    return ResponseHelper.service_response(result)


# ==============================================================================
# FILE: routes/protected.py
# ==============================================================================

"""
Protected routes for testing JWT authentication
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

protected_bp = Blueprint("protected", __name__, url_prefix="/api")


@protected_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user information from JWT token"""
    current_user_id = get_jwt_identity()
    jwt_claims = get_jwt()

    return jsonify(
        {
            "success": True,
            "data": {
                "user_id": current_user_id,
                "email": jwt_claims.get("email"),
                "is_admin": jwt_claims.get("is_admin"),
                "is_active": jwt_claims.get("is_active"),
                "fs_uniquifier": jwt_claims.get("fs_uniquifier"),
            },
        }
    )


@protected_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    """Get full user profile from database"""
    from models.user import User

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify({"success": True, "data": {"user": user.to_dict()}})


# ==============================================================================
# End of old authentication files backup
# ==============================================================================