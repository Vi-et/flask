import os

from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_EXPIRES = 3600
REFRESH_TOKEN_EXPIRES = 2592000
ALGORITHM = "HS256"
ERROR_MESSAGE_KEY = "message"
BCRYPT = "bcrypt"
HEADER_NAME = "Authorization"
SECRET_KEY = os.getenv("SECRET_KEY", "me_may_beo")


class JWTConfig:
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = ACCESS_TOKEN_EXPIRES  # 1 hour in seconds
    JWT_REFRESH_TOKEN_EXPIRES = REFRESH_TOKEN_EXPIRES  # 30 days in seconds
    JWT_ALGORITHM = ALGORITHM

    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_HEADER_NAME = HEADER_NAME
    JWT_HEADER_TYPE = "Bearer"

    JWT_ERROR_MESSAGE_KEY = ERROR_MESSAGE_KEY


class SecurityConfig:
    """Flask-Security-Too configuration"""

    # Basic Security Settings
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_CONFIRMABLE = False  # Disable email confirmation for now
    SECURITY_TRACKABLE = True

    # URL Settings
    SECURITY_URL_PREFIX = "/api/auth"
    SECURITY_LOGIN_URL = "/login"
    SECURITY_LOGOUT_URL = "/logout"
    SECURITY_REGISTER_URL = "/register"
    SECURITY_CHANGE_URL = "/change-password"

    # Password Settings
    SECURITY_PASSWORD_HASH = BCRYPT
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", "me_may_beo")
    SECURITY_PASSWORD_LENGTH_MIN = 8
    SECURITY_PASSWORD_COMPLEXITY_CHECKER = None

    # Fix bcrypt 72-byte limit
    SECURITY_HASHING_SCHEMES = [BCRYPT]
    SECURITY_DEPRECATED_HASHING_SCHEMES: list[str] = []

    # Disable HMAC double hashing that causes 72-byte limit issues
    SECURITY_PASSWORD_SINGLE_HASH = True

    # Token Authentication (Flask-Security built-in)
    SECURITY_TOKEN_AUTHENTICATION_KEY = "auth-token"  # Response key name
    SECURITY_TOKEN_AUTHENTICATION_HEADER = HEADER_NAME  # Header name
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True  # Skip email confirmation

    JWT_REFRESH_TOKEN_EXPIRES = REFRESH_TOKEN_EXPIRES
    JWT_ALGORITHM = ALGORITHM

    # CSRF settings for API
    WTF_CSRF_ENABLED = False
    WTF_CSRF_CHECK_DEFAULT = False
    SECURITY_CSRF_PROTECT_MECHANISMS: list[str] = []
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True

    # Flash Messages (disable for API)
    SECURITY_FLASH_MESSAGES = False

    # JSON Responses
    SECURITY_WANT_JSON = True  # Return JSON responses instead of HTML

    # Secret Key
    SECRET_KEY = SECRET_KEY

    # Additional Settings
    SECURITY_SEND_REGISTER_EMAIL = False  # Disable registration emails
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_SEND_PASSWORD_RESET_EMAIL = False
