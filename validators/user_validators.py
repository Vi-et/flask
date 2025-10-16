"""
User Validators
Validation logic for user-related operations
"""
from typing import Any, Dict


class UserListValidator:
    """Validator for user listing parameters"""

    @classmethod
    def validate(cls, **data: Any) -> Dict[str, Any]:
        """Validate user list query parameters"""
        errors = []

        # Optional pagination parameters
        page = data.get("page")
        if page is not None:
            if not isinstance(page, int) or page < 1:
                errors.append("Page must be a positive integer")

        per_page = data.get("per_page")
        if per_page is not None:
            if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
                errors.append("Per page must be an integer between 1 and 100")

        # Optional search parameters
        search = data.get("search")
        if search is not None:
            if not isinstance(search, str) or len(search) < 2 or len(search) > 100:
                errors.append("Search must be a string between 2 and 100 characters")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "first_error": errors[0] if errors else None,
        }


class UserUpdateValidator:
    """Validator for user update operations (admin only)"""

    @classmethod
    def validate(cls, **data: Any) -> Dict[str, Any]:
        """Validate user update data"""
        errors = []

        if "name" in data:
            name = data["name"]
            if not isinstance(name, str) or len(name) < 2 or len(name) > 100:
                errors.append("Name must be a string between 2 and 100 characters")

        if "email" in data:
            email = data["email"]
            if not isinstance(email, str) or "@" not in email or len(email) > 255:
                errors.append("Invalid email format")

        if "is_active" in data:
            if not isinstance(data["is_active"], bool):
                errors.append("is_active must be a boolean")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "first_error": errors[0] if errors else None,
        }


class UserCreateValidator:
    """Validator for admin user creation"""

    @classmethod
    def validate(cls, **data: Any) -> Dict[str, Any]:
        """Validate user creation data"""
        errors = []

        # Required fields
        if "name" not in data:
            errors.append("Name is required")
        elif not isinstance(data["name"], str) or len(data["name"]) < 2:
            errors.append("Name must be at least 2 characters")

        if "email" not in data:
            errors.append("Email is required")
        elif not isinstance(data["email"], str) or "@" not in data["email"]:
            errors.append("Invalid email format")

        if "password" not in data:
            errors.append("Password is required")
        elif not isinstance(data["password"], str) or len(data["password"]) < 8:
            errors.append("Password must be at least 8 characters")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "first_error": errors[0] if errors else None,
        }


def validate_user_bulk_operation(**data: Any) -> Dict[str, Any]:
    """Validate bulk user operations"""
    errors = []

    if "user_ids" not in data:
        errors.append("user_ids is required")
    elif not isinstance(data["user_ids"], list) or len(data["user_ids"]) == 0:
        errors.append("user_ids must be a non-empty array")

    if "operation" in data:
        valid_ops = ["activate", "deactivate", "delete"]
        if data["operation"] not in valid_ops:
            errors.append(f"operation must be one of: {', '.join(valid_ops)}")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "first_error": errors[0] if errors else None,
    }


def validate_user_create(**data: Any) -> Dict[str, Any]:
    """Validate user creation data (function version)"""
    return UserCreateValidator.validate(**data)


def validate_user_update(**data: Any) -> Dict[str, Any]:
    """Validate user update data (function version)"""
    return UserUpdateValidator.validate(**data)


def validate_user_search(**data: Any) -> Dict[str, Any]:
    """Validate user search parameters (function version)"""
    return UserListValidator.validate(**data)
