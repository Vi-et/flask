"""
User API endpoints
RESTful routes for user management
"""
from flask import Blueprint, request

from services.user_service import UserService
from utils.pagination_helper import PaginationHelper
from utils.response_helper import ResponseHelper
from utils.route_decorators import log_api_route, log_service_call

# Create Blueprint với URL prefix
users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("/")
@log_api_route("users", "list")
def get_users():
    """
    GET /api/users/
    Get all users with optional filtering
    """
    # Get pagination parameters using helper
    page, per_page = PaginationHelper.get_page_and_per_page()

    # Call service
    result = UserService.get_users_paginated(page=page, per_page=per_page)

    # Use response helper
    return ResponseHelper.service_response(result)


@users_bp.route("/<int:user_id>")
@log_api_route("users", "get")
def get_user(user_id):
    """
    GET /api/users/{id}
    Get single user by ID
    """
    # Call service and use response helper
    result = UserService.get_user_by_id(user_id)
    return ResponseHelper.service_response(result)


@users_bp.route("/", methods=["POST"])
@log_api_route("users", "create")
def create_user():
    """
    POST /api/users/
    Create new user
    """
    # Get JSON data and call service
    data = request.get_json()
    result = UserService.create_user(data)

    # Use response helper with 201 status for success
    return ResponseHelper.service_response(result, success_status=201)


@users_bp.route("/<int:user_id>", methods=["PUT"])
@log_api_route("users", "update")
def update_user(user_id):
    """
    PUT /api/users/{id}
    Update user information
    """
    # Get JSON data and call service
    data = request.get_json()
    result = UserService.update_user(user_id, data)

    # Use response helper
    return ResponseHelper.service_response(result)


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@log_api_route("users", "delete")
def delete_user(user_id):
    """
    DELETE /api/users/{id}
    Delete user
    """
    # Call service and use response helper
    result = UserService.delete_user(user_id)
    return ResponseHelper.service_response(result)


@users_bp.route("/<int:user_id>/posts")
@log_api_route("users", "get_posts")
def get_user_posts(user_id):
    """
    GET /api/users/{id}/posts
    Get all posts by specific user
    """
    # Get pagination parameters using helper
    page, per_page = PaginationHelper.get_page_and_per_page()

    # Call service and use response helper
    result = UserService.get_user_posts(user_id, page=page, per_page=per_page)
    return ResponseHelper.service_response(result)


@users_bp.route("/search")
def search_users():
    """
    GET /api/users/search?q=query
    Search users by name or email
    """
    query = request.args.get("q", "", type=str)
    page, per_page = PaginationHelper.get_page_and_per_page()

    # Call service and use response helper
    result = UserService.search_users(query, page=page, per_page=per_page)
    return ResponseHelper.service_response(result)
