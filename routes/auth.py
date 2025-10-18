"""
Authentication API endpoints
Routes for user registration, login, logout, and profile management
"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from constants.http_status import BAD_REQUEST
from services.auth_service import AuthService
from utils.response_helper import ResponseHelper
from utils.route_decorators import log_api_route
from validators.auth_validators import RegisterValidator

# Create Blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.route("/register", methods=["POST"])
@log_api_route("auth", "register")
def register():
    """
    POST /api/auth/register
    Register a new user
    """
    data = request.get_json()
    validate_result = RegisterValidator.validate(**data)
    if not validate_result["is_valid"]:
        return ResponseHelper.error_response(
            validate_result["first_error"], BAD_REQUEST
        )

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
@log_api_route("auth", "change_password")
def change_password():
    """
    PUT /api/auth/change-password
    Change user password (requires fresh token)
    Note: Should revoke all user tokens after password change
    """
    data = request.get_json()
    result = AuthService.change_password(data)

    # If password change successful, revoke current token for security
    if result.get("success"):
        try:
            from services.token_service import TokenService

            TokenService.revoke_current_token(reason="password_change")
        except Exception as e:
            # Don't fail password change if token revocation fails
            # Log the error but continue with successful password change
            print(f"Warning: Token revocation failed during password change: {e}")

    return ResponseHelper.service_response(result)


@auth_bp.route("/verify", methods=["GET"])
@jwt_required()
@log_api_route("auth", "verify_token")
def verify_token():
    """
    GET /api/auth/verify
    Verify if current token is valid
    """
    current_user_id = get_jwt_identity()
    return ResponseHelper.success(
        {"valid": True, "user_id": current_user_id, "message": "Token is valid"}
    )


# Health check endpoint (no auth required)
@auth_bp.route("/health", methods=["GET"])
@log_api_route("auth", "health_check")
def health_check():
    """
    GET /api/auth/health
    Authentication service health check
    """
    return ResponseHelper.success(
        {
            "service": "auth",
            "status": "healthy",
            "endpoints": [
                "POST /api/auth/register",
                "POST /api/auth/login",
                "POST /api/auth/refresh",
                "POST /api/auth/logout",
                "GET /api/auth/me",
                "PUT /api/auth/me",
                "PUT /api/auth/change-password",
                "GET /api/auth/verify",
            ],
        },
        "Authentication service is healthy",
    )
