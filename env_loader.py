#!/usr/bin/env python3
"""
Environment Variables Loader
Load .env files based on FLASK_ENV setting
"""
import os
from dotenv import load_dotenv

def load_environment():
    """Load appropriate .env file based on FLASK_ENV"""
    
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
        print(f"📁 Loaded base environment: {base_env}")
    
    # Load environment-specific .env file
    env_file = env_files.get(env, '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file, override=True)  # Override base settings
        print(f"🎯 Loaded {env} environment: {env_file}")
    else:
        print(f"⚠️  Environment file not found: {env_file}")
        print(f"💡 Using default environment variables for: {env}")
    
    # Print current environment info
    print(f"🌍 Current Environment: {env}")
    print(f"🐛 Debug Mode: {os.environ.get('FLASK_DEBUG', 'False')}")
    print(f"🏠 Host: {os.environ.get('FLASK_RUN_HOST', '127.0.0.1')}")
    print(f"🔌 Port: {os.environ.get('FLASK_RUN_PORT', '5000')}")

if __name__ == "__main__":
    # Test the environment loader
    print("🧪 Testing Environment Loader...")
    print("=" * 40)
    
    # Test different environments
    environments = ['development', 'production', 'testing']
    
    for env in environments:
        print(f"\n📋 Testing {env.upper()} environment:")
        print("-" * 30)
        
        # Set environment temporarily
        original_env = os.environ.get('FLASK_ENV')
        os.environ['FLASK_ENV'] = env
        
        # Load environment
        load_environment()
        
        # Restore original environment
        if original_env:
            os.environ['FLASK_ENV'] = original_env
        elif 'FLASK_ENV' in os.environ:
            del os.environ['FLASK_ENV']
    
    print("\n" + "=" * 40)
    print("✅ Environment loader test completed!")