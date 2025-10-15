"""
Service Response Helper
Utility functions for standardizing service layer responses
"""
from typing import Any, Dict, Optional


class ServiceResponseHelper:
    """Helper class for creating standardized service responses"""

    @staticmethod
    def success(
        data: Any = None,
        message: Optional[str] = None,
        status_code: int = 200,
        pagination: Optional[Dict[Any, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create success response for service layer

        Args:
            data: Response data (optional)
            message: Success message (optional)
            status_code: HTTP status code (default 200)
            pagination: Pagination info (optional)

        Returns:
            Standardized success response dictionary
        """
        response: Dict[str, Any] = {"success": True, "status_code": status_code}

        if data is not None:
            response["data"] = data

        if message:
            response["message"] = message

        if pagination:
            response["pagination"] = pagination

        return response

    @staticmethod
    def error(error_message: str, error_code: int = 400) -> Dict[str, Any]:
        """
        Create error response for service layer

        Args:
            error_message: Error description
            error_code: HTTP status code (default 400)

        Returns:
            Standardized error response dictionary
        """
        response = {"success": False, "status_code": error_code, "error": error_message}

        return response

    @staticmethod
    def not_found(resource_name: str = "Resource") -> Dict[str, Any]:
        """
        Create not found error response

        Args:
            resource_name: Name of the resource that wasn't found

        Returns:
            Standardized not found response dictionary
        """
        return ServiceResponseHelper.error(f"{resource_name} not found", 404)

    @staticmethod
    def bad_request(error_message: str) -> Dict[str, Any]:
        """
        Create bad request error response

        Args:
            error_message: Description of the bad request

        Returns:
            Standardized bad request response dictionary
        """
        return ServiceResponseHelper.error(error_message, 400)

    @staticmethod
    def validation_error(
        field_name: str, message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create validation error response

        Args:
            field_name: Name of the field that failed validation
            message: Custom validation message (optional)

        Returns:
            Standardized validation error response dictionary
        """
        if not message:
            message = f"{field_name} is required"
        return ServiceResponseHelper.bad_request(message)

    @staticmethod
    def already_exists(
        resource_name: str, identifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create already exists error response

        Args:
            resource_name: Name of the resource
            identifier: Specific identifier (e.g., email)

        Returns:
            Standardized already exists response dictionary
        """
        if identifier:
            message = f"{resource_name} with {identifier} already exists"
        else:
            message = f"{resource_name} already exists"
        return ServiceResponseHelper.bad_request(message)

    @staticmethod
    def operation_failed(
        operation: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create operation failed error response

        Args:
            operation: Name of the failed operation
            reason: Specific reason for failure (optional)

        Returns:
            Standardized operation failed response dictionary
        """
        if reason:
            message = f"Failed to {operation}: {reason}"
        else:
            message = f"Failed to {operation}"
        return ServiceResponseHelper.error(message, 500)

    @staticmethod
    def created(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
        """
        Create successful creation response

        Args:
            data: Created resource data
            message: Success message (optional)

        Returns:
            Standardized creation success response dictionary
        """
        if not message:
            message = "Resource created successfully"
        return ServiceResponseHelper.success(data=data, message=message)

    @staticmethod
    def updated(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
        """
        Create successful update response

        Args:
            data: Updated resource data
            message: Success message (optional)

        Returns:
            Standardized update success response dictionary
        """
        if not message:
            message = "Resource updated successfully"
        return ServiceResponseHelper.success(data=data, message=message)

    @staticmethod
    def deleted(message: Optional[str] = None) -> Dict[str, Any]:
        """
        Create successful deletion response

        Args:
            message: Success message (optional)

        Returns:
            Standardized deletion success response dictionary
        """
        if not message:
            message = "Resource deleted successfully"
        return ServiceResponseHelper.success(message=message)

    @staticmethod
    def paginated_success(
        data: list, pagination: Dict, message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create paginated success response

        Args:
            data: List of items
            pagination: Pagination metadata
            message: Success message (optional)

        Returns:
            Standardized paginated response dictionary
        """

        return ServiceResponseHelper.success(
            data=data, pagination=pagination, message=message
        )

    @staticmethod
    def simple_paginated_success(
        queryset: Any, message: Optional[str] = None
    ) -> Dict[str, Any]:
        data = [item.to_dict() for item in queryset.items]
        pagination = {
            "page": queryset.page,
            "pages": queryset.pages,
            "per_page": queryset.per_page,
            "total": queryset.total,
            "has_next": queryset.has_next,
            "has_prev": queryset.has_prev,
        }
        return ServiceResponseHelper.success(
            data=data, pagination=pagination, message=message
        )
