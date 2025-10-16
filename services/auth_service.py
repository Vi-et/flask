"""
Authentication Service
Business logic for user authentication and authorization
"""
from typing import Any, Dict, Optional

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
)

from constants.error_messages import (
    ACCOUNT_DEACTIVATED,
    CURRENT_PASSWORD_INCORRECT,
    DATABASE_ERROR,
    INVALID_CREDENTIALS,
    USER_INACTIVE,
    USER_NOT_FOUND,
)
from constants.http_status import (
    BAD_REQUEST,
    CREATED,
    INTERNAL_SERVER_ERROR,
    NOT_FOUND,
    UNAUTHORIZED,
)
from constants.token_constants import (
    REFRESH_TOKEN_TYPE,
    TOKEN_ROTATION_REASON,
    TOKEN_TYPE_CLAIM,
)
from models import db
from models.user import User
from utils.service_response_helper import ServiceResponseHelper
from validators.auth_validators import (
    LoginValidator,
    PasswordChangeValidator,
    ProfileUpdateValidator,
    SignUpValidator,
    UserCredentialsValidator,
)


class AuthService:
    """Service class for authentication business logic"""

    @staticmethod
    def register_user(data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        try:
            validation_result = SignUpValidator.validate(**data)

            if not validation_result["is_valid"]:
                return ServiceResponseHelper.error(
                    validation_result["first_error"], BAD_REQUEST
                )

            # Create new user with validated data
            name = data["name"].strip()
            email = data["email"].strip().lower()
            password = data["password"]

            user = User(name=name, email=email)
            user.set_password(password)

            # Sử dụng BaseModel.save() method
            if not user.save():
                return ServiceResponseHelper.error(
                    DATABASE_ERROR, INTERNAL_SERVER_ERROR
                )

            # Generate tokens
            tokens = user.generate_tokens()
            user.update_last_login()

            return ServiceResponseHelper.success(
                {"user": user.to_dict(), "tokens": tokens},
                "User registered successfully",
                status_code=CREATED,
            )

        except Exception as e:
            # Note: user.save() already handles rollback internally
            return ServiceResponseHelper.error(f"Registration failed: {str(e)}")

    @staticmethod
    def login_user(data: Dict[str, Any]) -> Dict[str, Any]:
        """Login user with email and password"""
        try:
            # Validate login data
            validation_result = LoginValidator.validate(**data)
            if not validation_result["is_valid"]:
                return ServiceResponseHelper.error(
                    validation_result["first_error"], BAD_REQUEST
                )

            email = data["email"].strip().lower()
            password = data["password"]

            # Find user by email
            user = User.get_by_email(email)
            if not user:
                return ServiceResponseHelper.error(INVALID_CREDENTIALS, UNAUTHORIZED)

            # Check if user is active
            if not user.is_active:
                return ServiceResponseHelper.error(ACCOUNT_DEACTIVATED, UNAUTHORIZED)

            # Verify password
            if not user.check_password(password):
                return ServiceResponseHelper.error(INVALID_CREDENTIALS, UNAUTHORIZED)

            # Generate tokens
            tokens = user.generate_tokens()
            user.update_last_login()

            return ServiceResponseHelper.success(
                {"user": user.to_dict(), "tokens": tokens}, "Login successful"
            )

        except Exception as e:
            return ServiceResponseHelper.error(f"Login failed: {str(e)}")

    @staticmethod
    def refresh_token() -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            # Get current JWT claims
            current_jwt = get_jwt()
            current_user_id = get_jwt_identity()

            # Validate token type - must be refresh token
            if current_jwt.get(TOKEN_TYPE_CLAIM) != REFRESH_TOKEN_TYPE:
                return ServiceResponseHelper.error(
                    "Invalid token type. Refresh token required", UNAUTHORIZED
                )

            # Check if refresh token is blacklisted
            from services.token_service import TokenService

            jti = current_jwt.get("jti")
            if jti and TokenService.is_token_revoked(jti):
                return ServiceResponseHelper.error(
                    "Refresh token has been revoked", UNAUTHORIZED
                )

            user = User.query.get(current_user_id)
            if not user or not user.is_active:
                return ServiceResponseHelper.error(USER_INACTIVE, NOT_FOUND)

            # Revoke current refresh token first (Token Rotation)
            if jti:
                TokenService.revoke_token(
                    jti=jti,
                    user_id=current_user_id,
                    token_type=REFRESH_TOKEN_TYPE,
                    reason=TOKEN_ROTATION_REASON,
                )

            # Generate new access token AND refresh token
            tokens = user.generate_tokens()

            return ServiceResponseHelper.success(
                {"tokens": tokens}, "Access token refreshed successfully"
            )

        except Exception as e:
            return ServiceResponseHelper.error(f"Token refresh failed: {str(e)}")

    @staticmethod
    def get_current_user() -> Dict[str, Any]:
        """Get current authenticated user"""
        try:
            current_user_id = get_jwt_identity()

            user = User.query.get(current_user_id)
            if not user:
                return ServiceResponseHelper.error(USER_NOT_FOUND, NOT_FOUND)

            return ServiceResponseHelper.success(
                user.to_dict(), "User retrieved successfully"
            )

        except Exception as e:
            return ServiceResponseHelper.error(f"Failed to get user: {str(e)}")

    @staticmethod
    def update_user_profile(data: Dict[str, Any]) -> Dict[str, Any]:
        """Update current user profile"""
        try:
            current_user_id = get_jwt_identity()

            user = User.query.get(current_user_id)
            if not user:
                return ServiceResponseHelper.error("User not found", NOT_FOUND)

            # Add current user ID for validation
            validation_data = data.copy()
            validation_data["current_user_id"] = current_user_id

            # Validate profile update data
            validation_result = ProfileUpdateValidator.validate(**validation_data)
            if not validation_result["is_valid"]:
                return ServiceResponseHelper.error(
                    validation_result["first_error"], BAD_REQUEST
                )

            # Update allowed fields
            if "name" in data:
                user.name = data["name"].strip()

            if "email" in data:
                user.email = data["email"].strip().lower()

            db.session.commit()

            return ServiceResponseHelper.success(
                user.to_dict(), "Profile updated successfully"
            )

        except Exception as e:
            db.session.rollback()
            return ServiceResponseHelper.error(f"Profile update failed: {str(e)}")

    @staticmethod
    def change_password(data: Dict[str, Any]) -> Dict[str, Any]:
        """Change user password"""
        try:
            current_user_id = get_jwt_identity()

            user = User.query.get(current_user_id)
            if not user:
                return ServiceResponseHelper.error("User not found", NOT_FOUND)

            # Validate password change data
            validation_result = PasswordChangeValidator.validate(**data)
            if not validation_result["is_valid"]:
                return ServiceResponseHelper.error(
                    validation_result["first_error"], BAD_REQUEST
                )

            current_password = data["current_password"]
            new_password = data["new_password"]

            # Verify current password
            if not user.check_password(current_password):
                return ServiceResponseHelper.error(
                    CURRENT_PASSWORD_INCORRECT, UNAUTHORIZED
                )

            # Update password
            user.set_password(new_password)
            db.session.commit()

            return ServiceResponseHelper.success({}, "Password changed successfully")

        except Exception as e:
            db.session.rollback()
            return ServiceResponseHelper.error(f"Password change failed: {str(e)}")

    @staticmethod
    def logout_user() -> Dict[str, Any]:
        """Logout user by blacklisting current token"""
        try:
            from services.token_service import TokenService

            # Revoke current token
            result = TokenService.revoke_current_token(reason="logout")

            if result["success"]:
                return ServiceResponseHelper.success({}, "Logout successful")
            else:
                return result

        except Exception as e:
            return ServiceResponseHelper.error(f"Logout failed: {str(e)}")
