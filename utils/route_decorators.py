"""
Route Decorators for Loguru Logging
Non-intrusive logging decorators for Flask routes
"""
import time
import functools
from flask import request, jsonify, g
from loguru import logger
from typing import Any, Callable


def log_route(route_name: str = None, log_request_body: bool = True):
    """
    Decorator to log Flask route calls
    
    Args:
        route_name: Custom name for the route (optional)
        log_request_body: Whether to log request body (default: True)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate route name
            name = route_name or f"{request.endpoint}"
            
            # Start timing
            start_time = time.time()
            
            # Log request
            request_data = _get_safe_request_data() if log_request_body else None
            logger.info(
                "🌐 Route: {method} {endpoint} - {name}",
                method=request.method,
                endpoint=request.path,
                name=name,
                extra={
                    "route_name": name,
                    "remote_addr": request.remote_addr,
                    "user_agent": request.headers.get('User-Agent', '')[:100],
                    "request_data": request_data,
                    "args": dict(request.args),
                    "request_id": id(request)
                }
            )
            
            try:
                # Execute route function
                result = func(*args, **kwargs)
                
                # Calculate duration
                duration = round((time.time() - start_time) * 1000, 2)
                
                # Determine status code
                status_code = 200
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                elif isinstance(result, tuple) and len(result) >= 2:
                    status_code = result[1]
                
                # Log successful response
                logger.info(
                    "✅ Route Success: {method} {endpoint} -> {status} ({duration}ms)",
                    method=request.method,
                    endpoint=request.path,
                    status=status_code,
                    duration=duration,
                    extra={
                        "route_name": name,
                        "request_id": id(request),
                        "response_size": _estimate_response_size(result)
                    }
                )
                
                return result
                
            except Exception as e:
                # Calculate duration for error case
                duration = round((time.time() - start_time) * 1000, 2)
                
                # Log error
                logger.error(
                    "❌ Route Error: {method} {endpoint} -> {error} ({duration}ms)",
                    method=request.method,
                    endpoint=request.path,
                    error=str(e),
                    duration=duration,
                    extra={
                        "route_name": name,
                        "request_id": id(request),
                        "error_type": type(e).__name__,
                        "traceback": logger.opt(exception=True).info("Route exception")
                    }
                )
                raise
                
        return wrapper
    return decorator


def log_api_route(resource: str, operation: str = None):
    """
    Specialized decorator for API routes
    
    Args:
        resource: Resource name (e.g., 'users', 'posts')
        operation: Operation type (e.g., 'list', 'create', 'update')
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Determine operation if not provided
            if not operation:
                method_operations = {
                    'GET': 'list' if not request.view_args else 'get',
                    'POST': 'create',
                    'PUT': 'update',
                    'PATCH': 'update', 
                    'DELETE': 'delete'
                }
                op = method_operations.get(request.method, 'unknown')
            else:
                op = operation
            
            route_name = f"{resource}.{op}"
            start_time = time.time()
            
            # Log API request
            logger.info(
                "📡 API: {method} {resource}.{operation}",
                method=request.method,
                resource=resource,
                operation=op,
                extra={
                    "api_resource": resource,
                    "api_operation": op,
                    "route_name": route_name,
                    "path_params": dict(request.view_args or {}),
                    "query_params": dict(request.args),
                    "request_id": id(request)
                }
            )
            
            try:
                result = func(*args, **kwargs)
                duration = round((time.time() - start_time) * 1000, 2)
                
                # Extract status and data info from result
                status_code, response_info = _analyze_api_response(result)
                
                logger.info(
                    "✅ API Success: {resource}.{operation} -> {status} ({duration}ms)",
                    resource=resource,
                    operation=op,
                    status=status_code,
                    duration=duration,
                    extra={
                        "api_resource": resource,
                        "api_operation": op,
                        "request_id": id(request),
                        "response_info": response_info
                    }
                )
                
                return result
                
            except Exception as e:
                duration = round((time.time() - start_time) * 1000, 2)
                
                logger.error(
                    "❌ API Error: {resource}.{operation} -> {error} ({duration}ms)",
                    resource=resource,
                    operation=op,
                    error=str(e),
                    duration=duration,
                    extra={
                        "api_resource": resource,
                        "api_operation": op,
                        "request_id": id(request),
                        "error_type": type(e).__name__
                    }
                )
                raise
                
        return wrapper
    return decorator


def log_service_call(service_name: str):
    """
    Decorator to log when routes call service methods
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger.debug(
                "🔧 Service Call: {service} from route {endpoint}",
                service=service_name,
                endpoint=request.endpoint,
                extra={
                    "service_name": service_name,
                    "calling_route": request.endpoint,
                    "request_id": id(request)
                }
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Helper functions
def _get_safe_request_data():
    """Get sanitized request data"""
    try:
        if request.is_json:
            data = request.get_json() or {}
            if isinstance(data, dict):
                # Hide sensitive fields
                sensitive_fields = ['password', 'token', 'secret', 'key', 'auth']
                return {
                    k: "***HIDDEN***" if any(field in k.lower() for field in sensitive_fields) else v
                    for k, v in data.items()
                }
            return "***JSON_DATA***"
        elif request.form:
            return "***FORM_DATA***"
        return None
    except Exception:
        return "***PARSE_ERROR***"


def _estimate_response_size(response):
    """Estimate response size"""
    try:
        if hasattr(response, 'get_data'):
            return len(response.get_data())
        elif isinstance(response, (dict, list)):
            return len(str(response))
        elif isinstance(response, tuple):
            return len(str(response[0])) if response else 0
        return 0
    except Exception:
        return 0


def _analyze_api_response(result):
    """Analyze API response for logging"""
    try:
        if hasattr(result, 'status_code'):
            status = result.status_code
            if hasattr(result, 'get_json'):
                data = result.get_json() or {}
                return status, {
                    "has_data": bool(data),
                    "data_keys": list(data.keys()) if isinstance(data, dict) else None
                }
            return status, {"type": "response_object"}
            
        elif isinstance(result, tuple) and len(result) >= 2:
            status = result[1]
            data = result[0]
            return status, {
                "has_data": bool(data),
                "data_type": type(data).__name__,
                "data_keys": list(data.keys()) if isinstance(data, dict) else None
            }
            
        return 200, {"type": type(result).__name__}
        
    except Exception:
        return 200, {"parse_error": True}