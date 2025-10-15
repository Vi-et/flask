"""
Authentication Decorators
Decorators for protecting routes and checking permissions
"""
import functools

from flask import jsonify
from flask_jwt_extended import (
    get_jwt,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)

from models.user import User


def auth_required(optional=False):
    """
    Decorator to require authentication for routes

    Args:
        optional: If True, authentication is optional
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=optional)
                return func(*args, **kwargs)
            except Exception as e:
                if optional:
                    return func(*args, **kwargs)
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Authentication required",
                            "error": str(e),
                        }
                    ),
                    401,
                )

        return wrapper

    return decorator


def admin_required():
    """Decorator to require admin privileges"""

    def decorator(func):
        @functools.wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                user = User.query.get(current_user_id)

                if not user:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "User not found",
                                "error": "user_not_found",
                            }
                        ),
                        404,
                    )

                if not user.is_admin:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "Admin privileges required",
                                "error": "insufficient_privileges",
                            }
                        ),
                        403,
                    )

                return func(*args, **kwargs)

            except Exception as e:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Authorization failed",
                            "error": str(e),
                        }
                    ),
                    500,
                )

        return wrapper

    return decorator


def active_user_required():
    """Decorator to require active user"""

    def decorator(func):
        @functools.wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                user = User.query.get(current_user_id)

                if not user:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "User not found",
                                "error": "user_not_found",
                            }
                        ),
                        404,
                    )

                if not user.is_active:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "Account is deactivated",
                                "error": "account_deactivated",
                            }
                        ),
                        401,
                    )

                return func(*args, **kwargs)

            except Exception as e:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Authorization failed",
                            "error": str(e),
                        }
                    ),
                    500,
                )

        return wrapper

    return decorator


def owner_or_admin_required(user_id_param="user_id"):
    """
    Decorator to require user to be owner of resource or admin

    Args:
        user_id_param: Name of the parameter containing user ID
    """

    def decorator(func):
        @functools.wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                current_user = User.query.get(current_user_id)

                if not current_user or not current_user.is_active:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "User not found or inactive",
                                "error": "user_not_active",
                            }
                        ),
                        401,
                    )

                # Get target user ID from route parameters
                target_user_id = kwargs.get(user_id_param)

                # Allow if user is admin or accessing their own resource
                if current_user.is_admin or current_user_id == target_user_id:
                    return func(*args, **kwargs)

                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Access denied. You can only access your own resources.",
                            "error": "access_denied",
                        }
                    ),
                    403,
                )

            except Exception as e:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Authorization failed",
                            "error": str(e),
                        }
                    ),
                    500,
                )

        return wrapper

    return decorator


def fresh_jwt_required():
    """Decorator to require fresh JWT token"""

    def decorator(func):
        @functools.wraps(func)
        @jwt_required(fresh=True)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_current_user_helper():
    """Helper function to get current authenticated user"""
    try:
        current_user_id = get_jwt_identity()
        if current_user_id:
            return User.query.get(current_user_id)
        return None
    except Exception:
        return None


def get_current_user_id():
    """Helper function to get current user ID"""
    try:
        return get_jwt_identity()
    except Exception:
        return None


def is_current_user_admin():
    """Helper function to check if current user is admin"""
    try:
        user = get_current_user_helper()
        return user and user.is_admin
    except Exception:
        return False
