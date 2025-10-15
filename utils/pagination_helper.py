"""
Pagination Helper
Utility functions for handling pagination parameters
"""
from flask import request
from typing import Dict, Tuple


class PaginationHelper:
    """Helper class for pagination operations"""
    
    # Default pagination settings
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 10
    MAX_PER_PAGE = 100
    
    @staticmethod
    def get_pagination_params() -> Dict[str, int]:
        """
        Extract and validate pagination parameters from request
        
        Returns:
            Dictionary with validated page and per_page values
        """
        page = request.args.get('page', PaginationHelper.DEFAULT_PAGE, type=int)
        per_page = request.args.get('per_page', PaginationHelper.DEFAULT_PER_PAGE, type=int)
        
        # Validate and sanitize values
        page = max(1, page)  # Page must be at least 1
        per_page = min(max(1, per_page), PaginationHelper.MAX_PER_PAGE)  # Between 1 and MAX_PER_PAGE
        
        return {
            'page': page,
            'per_page': per_page
        }
    
    @staticmethod
    def get_page() -> int:
        """Get page number from request"""
        return PaginationHelper.get_pagination_params()['page']
    
    @staticmethod
    def get_per_page() -> int:
        """Get per_page number from request"""
        return PaginationHelper.get_pagination_params()['per_page']
    
    @staticmethod
    def get_page_and_per_page() -> Tuple[int, int]:
        """
        Get page and per_page as tuple for easy unpacking with automatic validation
        
        Automatically validates and sanitizes pagination parameters:
        - page: minimum value 1
        - per_page: between 1 and MAX_PER_PAGE (100)
        
        Returns:
            Tuple of (validated_page, validated_per_page)
        """
        params = PaginationHelper.get_pagination_params()
        return params['page'], params['per_page']
    
    @staticmethod
    def create_pagination_info(pagination_obj) -> Dict[str, any]:
        """
        Create standardized pagination info from SQLAlchemy pagination object
        
        Args:
            pagination_obj: SQLAlchemy pagination object
            
        Returns:
            Dictionary with pagination metadata
        """
        return {
            'page': pagination_obj.page,
            'pages': pagination_obj.pages,
            'per_page': pagination_obj.per_page,
            'total': pagination_obj.total,
            'has_next': pagination_obj.has_next,
            'has_prev': pagination_obj.has_prev,
            'next_num': pagination_obj.next_num if pagination_obj.has_next else None,
            'prev_num': pagination_obj.prev_num if pagination_obj.has_prev else None
        }
    
    @staticmethod
    def get_pagination_info(pagination_obj) -> Dict[str, any]:
        """
        Alias for create_pagination_info for backward compatibility
        """
        return PaginationHelper.create_pagination_info(pagination_obj)
    
    @staticmethod
    def create_empty_pagination(per_page: int = None) -> Dict[str, any]:
        """
        Create empty pagination info for queries with no results
        
        Args:
            per_page: Items per page (optional, uses default if not provided)
            
        Returns:
            Dictionary with empty pagination metadata
        """
        if per_page is None:
            per_page = PaginationHelper.DEFAULT_PER_PAGE
            
        return {
            'page': 1,
            'pages': 0,
            'per_page': per_page,
            'total': 0,
            'has_next': False,
            'has_prev': False,
            'next_num': None,
            'prev_num': None
        }
    
    @staticmethod
    def get_offset(page: int, per_page: int) -> int:
        """
        Calculate offset for database queries
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Offset value for database queries
        """
        return (page - 1) * per_page
    
    @staticmethod
    def validate_pagination_params(page: int = None, per_page: int = None) -> Dict[str, int]:
        """
        Validate custom pagination parameters
        
        Args:
            page: Custom page number (optional)
            per_page: Custom per_page number (optional)
            
        Returns:
            Dictionary with validated parameters
        """
        if page is None:
            page = PaginationHelper.DEFAULT_PAGE
        if per_page is None:
            per_page = PaginationHelper.DEFAULT_PER_PAGE
            
        # Validate using the same logic as get_pagination_params
        page = max(1, page)
        per_page = min(max(1, per_page), PaginationHelper.MAX_PER_PAGE)
        
        return {
            'page': page,
            'per_page': per_page
        }
    
    @staticmethod
    def validate_and_get_params(page: int = None, per_page: int = None) -> Tuple[int, int]:
        """
        Validate custom pagination parameters and return as tuple
        
        Args:
            page: Custom page number (optional)
            per_page: Custom per_page number (optional)
            
        Returns:
            Tuple of (validated_page, validated_per_page)
        """
        validated = PaginationHelper.validate_pagination_params(page, per_page)
        return validated['page'], validated['per_page']