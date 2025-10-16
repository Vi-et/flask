"""
Flask-Security-Too Configuration
"""
import os
from datetime import timedelta


class SecurityConfig:
    """Flask-Security-Too configuration"""

    # Basic Security Settings
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_CONFIRMABLE = False  # Disable email confirmation for now
    SECURITY_TRACKABLE = True

    # Password Settings
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", "ntn_mommy")
    SECURITY_PASSWORD_LENGTH_MIN = 8
    SECURITY_PASSWORD_COMPLEXITY_CHECKER = None  # Disable for now

    # Fix bcrypt 72-byte limit
    SECURITY_HASHING_SCHEMES = ["bcrypt"]
    SECURITY_DEPRECATED_HASHING_SCHEMES: list[str] = []

    # Disable HMAC double hashing that causes 72-byte limit issues
    SECURITY_PASSWORD_SINGLE_HASH = True

    # Session Settings
    SECURITY_SESSION_PROTECTION = "strong"
    SECURITY_FRESH_LOGIN_WITHIN = timedelta(minutes=15)

    # Token Authentication (Flask-Security built-in)
    SECURITY_TOKEN_AUTHENTICATION_KEY = "auth-token"  # Response key name
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"  # Header name
    SECURITY_TOKEN_MAX_AGE = 3600  # 1 hour token expiry
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True  # Skip email confirmation

    # CSRF settings for API
    WTF_CSRF_ENABLED = False
    WTF_CSRF_CHECK_DEFAULT = False
    SECURITY_CSRF_PROTECT_MECHANISMS: list[str] = []
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True

    # URL Settings
    SECURITY_URL_PREFIX = "/api/auth"
    SECURITY_LOGIN_URL = "/login"
    SECURITY_LOGOUT_URL = "/logout"
    SECURITY_REGISTER_URL = "/register"
    SECURITY_CHANGE_URL = "/change-password"

    # Flash Messages (disable for API)
    SECURITY_FLASH_MESSAGES = False

    # JSON Responses
    SECURITY_WANT_JSON = True  # Return JSON responses instead of HTML

    # Secret Key
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-super-secret-key-change-this")

    # Additional Settings
    SECURITY_SEND_REGISTER_EMAIL = False  # Disable registration emails
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_SEND_PASSWORD_RESET_EMAIL = False
