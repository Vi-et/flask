"""
Flask-Loguru Configuration
Modern, structured logging with zero configuration
"""
import sys
import time
from pathlib import Path
from typing import Any, Callable, Optional

from flask import Flask, g, request
from loguru import logger


class LoguruConfig:
    """Loguru logging configuration for Flask"""

    @staticmethod
    def init_app(app: Flask) -> None:
        """Initialize Loguru with Flask app"""

        # Remove default handler
        logger.remove()

        # Console handler with colors
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>",
            level="INFO" if not app.debug else "DEBUG",
            colorize=True,
        )

        # File handler for persistent logs
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True)

        logger.add(
            "logs/app_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="00:00",  # New file daily
            retention="30 days",
            compression="zip",
        )

        # JSON structured logs for production
        logger.add(
            "logs/structured_{time:YYYY-MM-DD}.json",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
            rotation="100 MB",
            serialize=True,  # JSON format
        )

        # Hook into Flask request lifecycle
        LoguruConfig._setup_request_logging(app)

        logger.info("🚀 Loguru logging initialized")

    @staticmethod
    def _setup_request_logging(app: Flask) -> None:
        """Setup automatic request/response logging"""

        @app.before_request
        def log_request():
            """Log incoming requests"""
            g.start_time = time.time()

            # Sanitize sensitive data
            safe_data = LoguruConfig._sanitize_request_data(request)

            logger.info(
                "📥 Request: {method} {path}",
                method=request.method,
                path=request.path,
                extra={
                    "request_id": id(request),
                    "remote_addr": request.remote_addr,
                    "user_agent": request.headers.get("User-Agent", "")[:100],
                    "content_type": request.content_type,
                    "data": safe_data,
                },
            )

        @app.after_request
        def log_response(response):
            """Log outgoing responses"""
            duration = round((time.time() - g.start_time) * 1000, 2)

            logger.info(
                "📤 Response: {method} {path} -> {status} ({duration}ms)",
                method=request.method,
                path=request.path,
                status=response.status_code,
                duration=duration,
                extra={
                    "request_id": id(request),
                    "response_size": response.content_length or 0,
                    "content_type": response.content_type,
                },
            )

            return response

        @app.teardown_request
        def log_errors(error):
            """Log any request errors"""
            if error:
                logger.error(
                    "💥 Request Error: {error}",
                    error=str(error),
                    extra={
                        "request_id": id(request),
                        "method": request.method,
                        "path": request.path,
                        "error_type": type(error).__name__,
                    },
                )

    @staticmethod
    def _sanitize_request_data(request):
        """Remove sensitive information from request data"""
        try:
            if request.is_json:
                data = request.get_json() or {}
                # Remove password fields
                sensitive_fields = ["password", "token", "secret", "key"]
                return (
                    {
                        k: "***HIDDEN***"
                        if any(field in k.lower() for field in sensitive_fields)
                        else v
                        for k, v in data.items()
                    }
                    if isinstance(data, dict)
                    else "***JSON_DATA***"
                )
            elif request.form:
                return "***FORM_DATA***"
            else:
                return None
        except Exception:
            return "***PARSE_ERROR***"


# Service method decorators using Loguru
def log_service_method(service_name: Optional[str] = None) -> Callable:
    """Decorator to log service method calls"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            name = service_name or f"{func.__module__}.{func.__qualname__}"

            # Log method entry
            logger.debug(
                "🔧 Service Call: {name}",
                name=name,
                extra={
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                    "function": func.__name__,
                },
            )

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = round((time.time() - start_time) * 1000, 2)

                # Log success
                logger.info(
                    "✅ Service Success: {name} ({duration}ms)",
                    name=name,
                    duration=duration,
                    extra={"function": func.__name__},
                )

                return result

            except Exception as e:
                duration = round((time.time() - start_time) * 1000, 2)

                # Log error
                logger.error(
                    "❌ Service Error: {name} -> {error} ({duration}ms)",
                    name=name,
                    error=str(e),
                    duration=duration,
                    extra={"function": func.__name__, "error_type": type(e).__name__},
                )
                raise

        return wrapper

    return decorator


def log_database_operation(table: Optional[str] = None) -> Callable:
    """Decorator to log database operations"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            operation = table or "database"

            logger.debug(
                "🗄️  Database Operation: {operation}.{function}",
                operation=operation,
                function=func.__name__,
            )

            try:
                result = func(*args, **kwargs)
                logger.debug(
                    "✅ Database Success: {operation}.{function}",
                    operation=operation,
                    function=func.__name__,
                )
                return result

            except Exception as e:
                logger.error(
                    "❌ Database Error: {operation}.{function} -> {error}",
                    operation=operation,
                    function=func.__name__,
                    error=str(e),
                    extra={"error_type": type(e).__name__},
                )
                raise

        return wrapper

    return decorator
