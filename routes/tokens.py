"""
Token Management API endpoints
Routes for token blacklist and session management
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from services.token_service import TokenService
from utils.auth_decorators import admin_required
from utils.response_helper import ResponseHelper
from utils.route_decorators import log_api_route

# Create Blueprint
tokens_bp = Blueprint("tokens", __name__, url_prefix="/api/tokens")


@tokens_bp.route("/info", methods=["GET"])
@jwt_required()
@log_api_route("tokens", "get_info")
def get_token_info():
    """
    GET /api/tokens/info
    Get information about current token
    """
    result = TokenService.get_token_info()
    return ResponseHelper.service_response(result)


@tokens_bp.route("/revoke", methods=["POST"])
@jwt_required()
@log_api_route("tokens", "revoke")
def revoke_current_token():
    """
    POST /api/tokens/revoke
    Revoke current token (same as logout but explicit)
    """
    data = request.get_json() or {}
    reason = data.get("reason", "manual_revoke")

    result = TokenService.revoke_current_token(reason=reason)
    return ResponseHelper.service_response(result)


@tokens_bp.route("/revoke/<token_jti>", methods=["POST"])
@admin_required()
@log_api_route("tokens", "revoke_specific")
def revoke_specific_token(token_jti):
    """
    POST /api/tokens/revoke/{jti}
    Admin: Revoke specific token by JTI
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    token_type = data.get("token_type", "access")
    reason = data.get("reason", "admin_revoke")

    if not user_id:
        return ResponseHelper.bad_request_response("user_id is required")

    result = TokenService.revoke_token(token_jti, user_id, token_type, reason)
    return ResponseHelper.service_response(result)


@tokens_bp.route("/blacklist", methods=["GET"])
@jwt_required()
@log_api_route("tokens", "get_blacklist")
def get_user_blacklisted_tokens():
    """
    GET /api/tokens/blacklist
    Get current user's blacklisted tokens
    """
    from flask_jwt_extended import get_jwt_identity

    user_id = get_jwt_identity()
    result = TokenService.get_user_blacklisted_tokens(user_id)
    return ResponseHelper.service_response(result)


@tokens_bp.route("/blacklist/<int:user_id>", methods=["GET"])
@admin_required()
@log_api_route("tokens", "get_user_blacklist")
def get_user_blacklisted_tokens_admin(user_id):
    """
    GET /api/tokens/blacklist/{user_id}
    Admin: Get specific user's blacklisted tokens
    """
    result = TokenService.get_user_blacklisted_tokens(user_id)
    return ResponseHelper.service_response(result)


@tokens_bp.route("/cleanup", methods=["POST"])
@admin_required()
@log_api_route("tokens", "cleanup")
def cleanup_expired_tokens():
    """
    POST /api/tokens/cleanup
    Admin: Clean up expired blacklisted tokens
    """
    result = TokenService.cleanup_expired_tokens()
    return ResponseHelper.service_response(result)


@tokens_bp.route("/validate/<token_jti>", methods=["GET"])
@admin_required()
@log_api_route("tokens", "validate")
def validate_token(token_jti):
    """
    GET /api/tokens/validate/{jti}
    Admin: Check if token JTI is valid (not blacklisted)
    """
    is_valid = TokenService.is_token_valid(token_jti)

    return ResponseHelper.success(
        {"jti": token_jti, "is_valid": is_valid, "is_blacklisted": not is_valid}
    )


# Health check endpoint
@tokens_bp.route("/health", methods=["GET"])
@log_api_route("tokens", "health_check")
def health_check():
    """
    GET /api/tokens/health
    Token service health check
    """
    return ResponseHelper.success(
        {
            "service": "tokens",
            "status": "healthy",
            "endpoints": [
                "GET /api/tokens/info",
                "POST /api/tokens/revoke",
                "POST /api/tokens/revoke/{jti}",
                "GET /api/tokens/blacklist",
                "GET /api/tokens/blacklist/{user_id}",
                "POST /api/tokens/cleanup",
                "GET /api/tokens/validate/{jti}",
            ],
        },
        "Token management service is healthy",
    )
