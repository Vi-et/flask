"""
Application Factory Pattern with Environment Loading
"""
import os
from flask import Flask, request
from config.config import config
from config.database import db, init_database

# Load environment variables from .env files
def load_env_vars():
    """Load environment variables from .env files"""
    try:
        from dotenv import load_dotenv
        
        # Get current environment
        env = os.environ.get('FLASK_ENV', 'development')
        
        # Map environment to .env files
        env_files = {
            'development': '.env',
            'production': '.env.production', 
            'testing': '.env.testing'
        }
        
        # Load base .env first (if exists)
        base_env = '.env'
        if os.path.exists(base_env):
            load_dotenv(base_env)
        
        # Load environment-specific .env file
        env_file = env_files.get(env, '.env')
        if os.path.exists(env_file) and env_file != base_env:
            load_dotenv(env_file, override=True)  # Override base settings
            
    except ImportError:
        print("⚠️  python-dotenv not installed. Using system environment variables.")

def create_app(config_name=None):
    """Create Flask application using factory pattern"""
    
    # Load environment variables first
    load_env_vars()
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['default']))
    
    # Override with environment variables if they exist
    app.config.update({
        key: os.environ.get(key, app.config.get(key))
        for key in [
            'SECRET_KEY', 'DATABASE_URL', 'MAIL_SERVER', 'MAIL_USERNAME',
            'REDIS_URL', 'APP_NAME', 'API_VERSION', 'MAX_CONTENT_LENGTH'
        ] if os.environ.get(key)
    })
    
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

def register_blueprints(app):
    """Register application blueprints"""
    from routes.main import main_bp
    from routes.blog import blog_bp
    from routes.forms import forms_bp
    from routes.api import api_bp
    from routes.errors import errors_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(forms_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(errors_bp)

def register_error_handlers(app):
    """Register custom error handlers"""
    from utils.helpers import APIException, handle_api_exception
    
    app.register_error_handler(APIException, handle_api_exception)

def register_context_processors(app):
    """Register template context processors"""
    
    @app.context_processor
    def inject_globals():
        return {
            'app_name': app.config.get('APP_NAME', 'Flask App'),
            'version': app.config.get('API_VERSION', '1.0.0')
        }

def register_cli_commands(app):
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
    
    @app.cli.command()
    def show_config():
        """Show current configuration"""
        print("\n📋 Current Configuration:")
        print("=" * 30)
        for key, value in sorted(app.config.items()):
            if 'PASSWORD' in key or 'SECRET' in key:
                print(f"{key}: {'*' * len(str(value))}")
            else:
                print(f"{key}: {value}")

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
        response.headers['X-API-Version'] = app.config.get('API_VERSION', '1.0.0')
        return response