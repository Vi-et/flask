"""
Common Error Messages Constants
Centralized error messages for consistency and maintainability
"""

# Authentication Errors
INVALID_CREDENTIALS = "Invalid email or password"
ACCOUNT_DEACTIVATED = "Account is deactivated"
UNAUTHORIZED_ACCESS = "Unauthorized access"
INVALID_TOKEN_TYPE = "Invalid token type"
TOKEN_EXPIRED = "Token has expired"
TOKEN_REVOKED = "Token has been revoked"

# User Errors
USER_NOT_FOUND = "User not found"
USER_INACTIVE = "User not found or inactive"
EMAIL_ALREADY_EXISTS = "Email already exists"
INVALID_EMAIL_FORMAT = "Invalid email format"

# Password Errors
INVALID_PASSWORD = "Invalid password"
PASSWORD_TOO_WEAK = "Password is too weak"
CURRENT_PASSWORD_INCORRECT = "Current password is incorrect"
PASSWORD_MISMATCH = "Passwords do not match"

# Validation Errors
VALIDATION_FAILED = "Validation failed"
REQUIRED_FIELD_MISSING = "Required field is missing"
INVALID_INPUT_FORMAT = "Invalid input format"

# System Errors
INTERNAL_ERROR = "Internal server error"
DATABASE_ERROR = "Database operation failed"
SERVICE_UNAVAILABLE = "Service temporarily unavailable"
