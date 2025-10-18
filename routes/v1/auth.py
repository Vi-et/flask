"""
Authentication API endpoints v1
Routes for user registration, login, logout, and profile management
"""
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from constants.http_status import BAD_REQUEST
from routes.v1 import api_v1
from services.auth_service import AuthService
from utils.response_helper import ResponseHelper
from utils.route_decorators import log_api_route
from validators.auth_validators import RegisterValidator


@api_v1.route("/auth/register", methods=["POST"])
@log_api_route("auth", "register")
def register():
    """
    POST /api/v1/auth/register
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


@api_v1.route("/auth/login", methods=["POST"])
@log_api_route("auth", "login")
def login():
    """
    POST /api/v1/auth/login
    Login user with email and password
    """
    data = request.get_json()
    result = AuthService.login_user(data)
    return ResponseHelper.service_response(result)


@api_v1.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
@log_api_route("auth", "refresh_token")
def refresh():
    """
    POST /api/v1/auth/refresh
    Refresh access token using refresh token
    """
    result = AuthService.refresh_token()
    return ResponseHelper.service_response(result)


@api_v1.route("/auth/logout", methods=["POST"])
@jwt_required()
@log_api_route("auth", "logout")
def logout():
    """
    POST /api/v1/auth/logout
    Logout user by blacklisting token
    """
    result = AuthService.logout_user()
    return ResponseHelper.service_response(result)


@api_v1.route("/auth/me", methods=["GET"])
@jwt_required()
@log_api_route("auth", "get_profile")
def get_profile():
    """
    GET /api/v1/auth/me
    Get current user profile
    """
    result = AuthService.get_current_user()
    return ResponseHelper.service_response(result)


@api_v1.route("/auth/me", methods=["PUT"])
@jwt_required()
@log_api_route("auth", "update_profile")
def update_profile():
    """
    PUT /api/v1/auth/me
    Update current user profile
    """
    data = request.get_json()
    result = AuthService.update_user_profile(data)
    return ResponseHelper.service_response(result)


@api_v1.route("/auth/change-password", methods=["POST"])
@jwt_required()
@log_api_route("auth", "change_password")
def change_password():
    """
    POST /api/v1/auth/change-password
    Change user password
    """
    data = request.get_json()
    result = AuthService.change_password(data)
    return ResponseHelper.service_response(result)
