"""
Application utilities and helpers
"""
import re
from functools import wraps

from flask import current_app, jsonify, request


def validate_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_json_content_type(f):
    """Decorator to validate JSON content type"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ["POST", "PUT", "PATCH"]:
            if not request.is_json:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Content-Type must be application/json",
                        }
                    ),
                    400,
                )
        return f(*args, **kwargs)

    return decorated_function


def paginate_query(query, page=1, per_page=10, max_per_page=100):
    """Helper function for pagination"""
    # Limit per_page to prevent abuse
    per_page = min(per_page, max_per_page)

    return query.paginate(page=page, per_page=per_page, error_out=False)


def create_response(status="success", data=None, message=None, **kwargs):
    """Create standardized API response"""
    response = {"status": status}

    if data is not None:
        response["data"] = data

    if message:
        response["message"] = message

    # Add any additional kwargs
    response.update(kwargs)

    return response


class APIException(Exception):
    """Custom API exception"""

    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def handle_api_exception(e):
    """Handle custom API exceptions"""
    return jsonify(create_response(status="error", message=e.message)), e.status_code
