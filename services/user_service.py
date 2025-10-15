"""
User Service
Business logic for user management
"""
from typing import Dict, Any
from models.user import User
from utils.service_response_helper import ServiceResponseHelper
from utils.pagination_helper import PaginationHelper


class UserService:
    """Service class for user business logic"""

    @staticmethod
    def get_users_paginated(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        try:
            # Get paginated users
            users_pagination = User.query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            return ServiceResponseHelper.simple_paginated_success(queryset=users_pagination)
        except Exception as e:
            return ServiceResponseHelper.error(str(e))

    @staticmethod
    def get_user_by_id(user_id: int) -> Dict[str, Any]:
        try:
            user = User.query.get(user_id)
            if not user:
                return ServiceResponseHelper.not_found('User')
            
            return ServiceResponseHelper.success(data=user.to_dict())
        except Exception as e:
            return ServiceResponseHelper.error(str(e))

    @staticmethod
    def create_user(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new user
        
        Args:
            data: User data (name, email)
            
        Returns:
            Dictionary with created user data or error
        """
        try:
            # Validation
            if not data or not data.get('name') or not data.get('email'):
                return ServiceResponseHelper.bad_request('Name and email are required')
            
            email = data['email'].strip().lower()
            
            # Check if email already exists
            if User.get_by_email(email):
                return ServiceResponseHelper.already_exists('User', f"email {email}")
            
            # Create user
            new_user = User(
                name=data['name'].strip(),
                email=email
            )
            
            if new_user.save():
                return ServiceResponseHelper.created(new_user.to_dict(), 'User created successfully')
            else:
                return ServiceResponseHelper.operation_failed('create user')
        except Exception as e:
            return ServiceResponseHelper.error(str(e))

    @staticmethod
    def update_user(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user information
        
        Args:
            user_id: User ID to update
            data: Updated user data
            
        Returns:
            Dictionary with updated user data or error
        """
        try:
            user = User.query.get(user_id)
            
            if not user:
                return ServiceResponseHelper.not_found('User')
            
            if not data:
                return ServiceResponseHelper.bad_request('No data provided')
            
            # Update fields
            if 'name' in data:
                user.name = data['name'].strip()
                
            if 'email' in data:
                new_email = data['email'].strip().lower()
                # Check if new email already exists (but not for current user)
                if new_email != user.email and User.get_by_email(new_email):
                    return ServiceResponseHelper.already_exists('User', f"email {new_email}")
                user.email = new_email
            
            if user.save():
                return ServiceResponseHelper.updated(user.to_dict(), 'User updated successfully')
            else:
                return ServiceResponseHelper.operation_failed('update user')
        except Exception as e:
            return ServiceResponseHelper.error(str(e))

    @staticmethod
    def delete_user(user_id: int) -> Dict[str, Any]:
        """
        Delete user
        
        Args:
            user_id: User ID to delete
            
        Returns:
            Dictionary with success status or error
        """
        try:
            user = User.query.get(user_id)
            
            if not user:
                return ServiceResponseHelper.not_found('User')
            
            # Check if user has posts (optional business rule)
            from models.post import Post
            posts_count = Post.query.filter_by(author_id=user_id).count()
            if posts_count > 0:
                return ServiceResponseHelper.bad_request('Cannot delete user with existing posts')
            
            if user.delete():
                return ServiceResponseHelper.deleted('User deleted successfully')
            else:
                return ServiceResponseHelper.operation_failed('delete user')
        except Exception as e:
            return ServiceResponseHelper.error(str(e))

    @staticmethod
    def get_user_posts(user_id: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Get posts by specific user
        
        Args:
            user_id: User ID
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary with user posts data and pagination info
        """
        try:
            user = User.query.get(user_id)
            
            if not user:
                return ServiceResponseHelper.not_found('User')
            
            # Note: Pagination parameters already validated by PaginationHelper in routes
            
            # Get user's posts with pagination (need to use query)
            from models.post import Post
            posts_pagination = Post.query.filter_by(author_id=user_id).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            
            # Return with both user info and posts using ServiceResponseHelper
            return ServiceResponseHelper.success(
                data={
                    'user': user.to_dict(),
                    'posts': [post.to_dict() for post in posts_pagination.items]
                },
                pagination=PaginationHelper.get_pagination_info(posts_pagination)
            )
        except Exception as e:
            return ServiceResponseHelper.error(str(e))

    @staticmethod
    def search_users(query: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Search users by name or email
        
        Args:
            query: Search query
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary with search results and pagination info
        """
        try:
            if not query.strip():
                # Return empty results for empty query using helper
                empty_pagination = PaginationHelper.create_empty_pagination(per_page)
                return ServiceResponseHelper.paginated_success(
                    data=[],
                    pagination=empty_pagination
                )
            
            # Note: Pagination parameters already validated by PaginationHelper in routes
            
            # Search users by name or email
            users_pagination = User.query.filter(
                User.name.contains(query) | User.email.contains(query)
            ).paginate(page=page, per_page=per_page, error_out=False)
            
            # Use PaginationHelper to create pagination info
            pagination_info = PaginationHelper.get_pagination_info(users_pagination)
            
            return ServiceResponseHelper.paginated_success(
                data=[user.to_dict() for user in users_pagination.items],
                pagination=pagination_info
            )
        except Exception as e:
            return ServiceResponseHelper.error(str(e))