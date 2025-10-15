"""
Services Package
Business logic layer for the Flask API

This package contains service classes that handle business logic,
separating it from route handlers and models.

Services:
- UserService: User management business logic
- PostService: Post management business logic  
- ContactService: Contact management business logic
- SearchService: Search functionality business logic
"""

from .user_service import UserService


__all__ = [
    'UserService',
    'PostService', 
    'ContactService',
    'SearchService'
]