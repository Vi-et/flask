"""
Authentication Service
Business logic for user authentication and authorization
"""
from typing import Dict, Any, Optional
from models.user import User
from models import db
from utils.service_response_helper import ServiceResponseHelper
from validators.auth_validators import (
    SignUpValidator, 
    LoginValidator, 
    ProfileUpdateValidator, 
    PasswordChangeValidator,
    UserCredentialsValidator
)
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt_identity,
    get_jwt
)


class AuthService:
    """Service class for authentication business logic"""
    
    @staticmethod
    def register_user(data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        try:
           
            validation_result = SignUpValidator.validate(**data)
   
            if not validation_result['is_valid']:
                print(validation_result)
                return ServiceResponseHelper.error(
                    validation_result['first_error'],
                    400
                )

            # Create new user with validated data
            name = data['name'].strip()
            email = data['email'].strip().lower()
            password = data['password']
            
            user = User(name=name, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Generate tokens
            tokens = user.generate_tokens()
            user.update_last_login()
            
            return ServiceResponseHelper.success(
                {
                    'user': user.to_dict(),
                    'tokens': tokens
                },
                "User registered successfully",
                status_code=201
            )
            
        except Exception as e:
            db.session.rollback()
            return ServiceResponseHelper.error(f"Registration failed: {str(e)}")
    
    @staticmethod
    def login_user(data: Dict[str, Any]) -> Dict[str, Any]:
        """Login user with email and password"""
        try:
            # Validate login data
            validation_result = LoginValidator.validate(data=data)
            if not validation_result['is_valid']:
                return ServiceResponseHelper.error(
                    validation_result['first_error'], 
                    400
                )
            
            email = data['email'].strip().lower()
            password = data['password']
            
            # Find user by email
            user = User.get_by_email(email)
            if not user:
                return ServiceResponseHelper.error(
                    "Invalid email or password", 
                    401
                )
            
            # Check if user is active
            if not user.is_active:
                return ServiceResponseHelper.error(
                    "Account is deactivated", 
                    401
                )
            
            # Verify password
            if not user.check_password(password):
                return ServiceResponseHelper.error(
                    "Invalid email or password", 
                    401
                )
            
            # Generate tokens
            tokens = user.generate_tokens()
            user.update_last_login()
            
            return ServiceResponseHelper.success(
                {
                    'user': user.to_dict(),
                    'tokens': tokens
                },
                "Login successful"
            )
            
        except Exception as e:
            return ServiceResponseHelper.error(f"Login failed: {str(e)}")
    
    @staticmethod
    def refresh_token() -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            current_user_id = get_jwt_identity()
            
            user = User.query.get(current_user_id)
            if not user or not user.is_active:
                return ServiceResponseHelper.error(
                    "User not found or inactive", 
                    404
                )
            
            # Generate new access token
            tokens = user.generate_tokens()
            
            return ServiceResponseHelper.success(
                {'tokens': tokens},
                "Token refreshed successfully"
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
                return ServiceResponseHelper.error(
                    "User not found", 
                    404
                )
            
            return ServiceResponseHelper.success(
                user.to_dict(),
                "User retrieved successfully"
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
                return ServiceResponseHelper.error(
                    "User not found", 
                    404
                )
            
            # Add current user ID for validation
            validation_data = data.copy()
            validation_data['current_user_id'] = current_user_id
            
            # Validate profile update data
            validation_result = ProfileUpdateValidator.validate(**validation_data)
            if not validation_result['is_valid']:
                return ServiceResponseHelper.error(
                    validation_result['first_error'], 
                    400
                )
            
            # Update allowed fields
            if 'name' in data:
                user.name = data['name'].strip()
            
            if 'email' in data:
                user.email = data['email'].strip().lower()
            
            db.session.commit()
            
            return ServiceResponseHelper.success(
                user.to_dict(),
                "Profile updated successfully"
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
                return ServiceResponseHelper.error(
                    "User not found", 
                    404
                )
            
            # Validate password change data
            validation_result = PasswordChangeValidator.validate(**data)
            if not validation_result['is_valid']:
                return ServiceResponseHelper.error(
                    validation_result['first_error'], 
                    400
                )
            
            current_password = data['current_password']
            new_password = data['new_password']
            
            # Verify current password
            if not user.check_password(current_password):
                return ServiceResponseHelper.error(
                    "Current password is incorrect", 
                    401
                )
            
            # Update password
            user.set_password(new_password)
            db.session.commit()
            
            return ServiceResponseHelper.success(
                {},
                "Password changed successfully"
            )
            
        except Exception as e:
            db.session.rollback()
            return ServiceResponseHelper.error(f"Password change failed: {str(e)}")
    
    @staticmethod
    def logout_user() -> Dict[str, Any]:
        """Logout user (for future blacklist implementation)"""
        try:
            # For now, just return success
            # In future: add token to blacklist
            return ServiceResponseHelper.success(
                {},
                "Logout successful"
            )
            
        except Exception as e:
            return ServiceResponseHelper.error(f"Logout failed: {str(e)}")
    
