"""
Token Type Constants
Constants for JWT token types and related values
"""

# Token Types
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

# Token Reasons
LOGOUT_REASON = "logout"
TOKEN_ROTATION_REASON = "token_rotation"
PASSWORD_CHANGE_REASON = "password_change"
MANUAL_REVOKE_REASON = "manual_revoke"
LOGOUT_ALL_REASON = "logout_all"

# Token Claims
TOKEN_TYPE_CLAIM = "type"
JTI_CLAIM = "jti"
SUBJECT_CLAIM = "sub"
EXPIRY_CLAIM = "exp"
