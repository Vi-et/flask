"""
Response Helper
Utility functions for standardizing API responses
"""
from flask import jsonify
from typing import Dict, Any, Tuple


class ResponseHelper:
    """Helper class for standardizing API responses"""

    @staticmethod
    def success_response(data: Any = None, message: str = None, 
                        status_code: int = 200, **kwargs) -> Tuple[Any, int]:
        """
        Create success response
        
        Args:
            data: Response data
            message: Success message  
            status_code: HTTP status code (default 200)
            **kwargs: Additional fields (pagination, etc.)
            
        Returns:
            Tuple of (jsonified response, status_code)
        """
        response = {
            'status': 'success'
        }
        
        if data is not None:
            response['data'] = data
            
        if message:
            response['message'] = message
            
        # Add additional fields
        response.update(kwargs)
        
        return jsonify(response), status_code

    @staticmethod
    def error_response(message: str, status_code: int = 500, 
                      error_code: str = None, **kwargs) -> Tuple[Any, int]:
        """
        Create error response
        
        Args:
            message: Error message
            status_code: HTTP status code (default 500)
            error_code: Custom error code
            **kwargs: Additional error fields
            
        Returns:
            Tuple of (jsonified response, status_code)
        """
        response = {
            'status': 'error',
            'message': message
        }
        
        if error_code:
            response['error_code'] = error_code
            
        # Add additional fields
        response.update(kwargs)
        
        return jsonify(response), status_code

    @staticmethod
    def service_response(result: Dict[str, Any], success_status: int = 200, 
                        success_message_key: str = 'message') -> Tuple[Any, int]:
        """
        Convert service result to HTTP response
        
        Args:
            result: Service method result dictionary
            success_status: HTTP status for success (default 200)
            success_message_key: Key for success message in result
            
        Returns:
            Tuple of (jsonified response, status_code)
        """
        if result['success']:
            response_data = {
                'status': 'success'
            }
            
            # Add data if present
            if 'data' in result:
                response_data['data'] = result['data']
                
            # Add message if present
            if success_message_key in result:
                response_data['message'] = result[success_message_key]
                
            # Add other fields (pagination, etc.)
            for key, value in result.items():
                if key not in ['success', 'data', success_message_key]:
                    response_data[key] = value
                    
            return jsonify(response_data), success_status
        else:
            # Error response
            status_code = result.get('error_code', 500)
            return ResponseHelper.error_response(
                message=result['error'],
                status_code=status_code
            )

    @staticmethod
    def paginated_response(data: list, pagination: Dict[str, Any], 
                          message: str = None) -> Tuple[Any, int]:
        """
        Create paginated success response
        
        Args:
            data: List of items
            pagination: Pagination metadata
            message: Optional message
            
        Returns:
            Tuple of (jsonified response, 200)
        """
        return ResponseHelper.success_response(
            data=data,
            message=message,
            pagination=pagination
        )

    @staticmethod
    def created_response(data: Any, message: str = "Resource created successfully") -> Tuple[Any, int]:
        """
        Create 201 Created response
        
        Args:
            data: Created resource data
            message: Success message
            
        Returns:
            Tuple of (jsonified response, 201)
        """
        return ResponseHelper.success_response(
            data=data,
            message=message,
            status_code=201
        )

    @staticmethod
    def not_found_response(message: str = "Resource not found") -> Tuple[Any, int]:
        """
        Create 404 Not Found response
        
        Args:
            message: Error message
            
        Returns:
            Tuple of (jsonified response, 404)
        """
        return ResponseHelper.error_response(
            message=message,
            status_code=404
        )

    @staticmethod
    def validation_error_response(message: str = "Validation failed", 
                                 errors: Dict = None) -> Tuple[Any, int]:
        """
        Create 400 Validation Error response
        
        Args:
            message: Error message
            errors: Validation errors dictionary
            
        Returns:
            Tuple of (jsonified response, 400)
        """
        kwargs = {}
        if errors:
            kwargs['errors'] = errors
            
        return ResponseHelper.error_response(
            message=message,
            status_code=400,
            **kwargs
        )