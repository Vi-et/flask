"""
Application Factory Pattern
"""
import os
from typing import Optional

from flask import Flask, request

from config.config import config
from config.database import db, init_database
from utils.loguru_config import LoguruConfig


def create_app(config_name: Optional[str] = None) -> Flask:
    """Create Flask application using factory pattern"""

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app: Flask = Flask(__name__)

    # Load configuration
    app.config.from_object(config.get(config_name, config["default"]))

    # Initialize Loguru logging
    LoguruConfig.init_app(app)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register context processors
    register_context_processors(app)

    # Register CLI commands
    register_cli_commands(app)

    # Initialize database
    with app.app_context():
        init_database(app)

    return app


def register_blueprints(app: Flask) -> None:
    """Auto-register all blueprints from routes directory"""
    from blueprint_discovery import auto_register_blueprints

    # Auto-discover và register tất cả blueprints
    auto_register_blueprints(app, routes_dir="routes", verbose=False)


def register_error_handlers(app: Flask) -> None:
    """Register custom error handlers"""
    from utils.helpers import APIException, handle_api_exception

    app.register_error_handler(APIException, handle_api_exception)


def register_context_processors(app: Flask) -> None:
    """Register template context processors"""

    @app.context_processor
    def inject_globals():
        return {
            "app_name": app.config.get("APP_NAME", "Flask App"),
            "version": app.config.get("API_VERSION", "1.0.0"),
        }


def register_cli_commands(app: Flask) -> None:
    """Register CLI commands"""

    @app.cli.command()
    def init_db():
        """Initialize database"""
        init_database(app)
        print("✅ Database initialized!")

    @app.cli.command()
    def reset_db():
        """Reset database"""
        db.drop_all()
        db.create_all()
        init_database(app)
        print("🔄 Database reset complete!")


# Request/Response hooks
def register_hooks(app):
    """Register request/response hooks"""

    @app.before_request
    def before_request():
        """Log requests in development"""
        if app.debug:
            print(f"Request: {request.method} {request.path}")

    @app.after_request
    def after_request(response):
        """Add custom headers"""
        response.headers["X-API-Version"] = app.config.get("API_VERSION", "1.0.0")
        return response
