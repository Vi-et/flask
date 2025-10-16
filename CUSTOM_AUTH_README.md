# Custom JWT Authentication System

This branch (`feature/custom-jwt-auth`) preserves the complete custom JWT authentication implementation before migrating to Flask-Security-Too.

## 🚀 Features Implemented

### ✅ **Core Authentication**
- JWT-based authentication with Flask-JWT-Extended
- User registration and login
- Password hashing with Werkzeug
- Token-based session management

### ✅ **Token Management**
- Access tokens (short-lived: 1 hour)
- Refresh tokens (long-lived: 30 days)
- **Token blacklist system** for real logout
- **Refresh token rotation** for enhanced security
- JWT with custom claims (`type`, `jti`)

### ✅ **Security Features**
- Token blacklist with database persistence
- JTI (JWT ID) for granular token control
- Fresh JWT requirement for sensitive operations
- Password change invalidates all tokens
- Comprehensive input validation

### ✅ **API Endpoints**

#### Authentication (`/api/auth`)
```bash
POST /api/auth/register      # User registration
POST /api/auth/login         # User login
POST /api/auth/refresh       # Token refresh with rotation
POST /api/auth/logout        # Secure logout (blacklist token)
GET  /api/auth/me            # Get current user
PUT  /api/auth/me            # Update profile
PUT  /api/auth/change-password # Change password (fresh JWT)
GET  /api/auth/verify        # Verify token validity
GET  /api/auth/health        # Service health check
```

#### Token Management (`/api/tokens`)
```bash
GET  /api/tokens/            # List user tokens
GET  /api/tokens/info        # Current token info
POST /api/tokens/revoke      # Revoke specific token
GET  /api/tokens/blacklist   # View blacklisted tokens
DELETE /api/tokens/cleanup   # Cleanup expired tokens
```

#### Users (`/api/users`)
```bash
GET  /api/users/             # List users (authenticated)
GET  /api/users/{id}         # Get user details
POST /api/users/             # Create user (admin)
PUT  /api/users/{id}         # Update user (admin)
DELETE /api/users/{id}       # Delete user (admin)
```

## 📁 **Architecture**

### **Models**
- `User`: User entity with authentication methods
- `TokenBlacklist`: Revoked JWT tokens storage
- `Post`: Example relationship with User

### **Services**
- `AuthService`: Authentication business logic
- `TokenService`: Token blacklist operations
- `UserService`: User management operations

### **Security Components**
- HTTP status constants (`constants/http_status.py`)
- Error message constants (`constants/error_messages.py`)
- Token constants (`constants/token_constants.py`)
- Comprehensive validators for all operations

### **Database Features**
- SQLAlchemy ORM with migrations
- Token blacklist table with indexes
- User-Post relationships with cascading
- Automatic cleanup of expired tokens

## 🔧 **Key Implementation Details**

### **Token Blacklist System**
```python
# Real logout functionality
def logout_user():
    TokenService.revoke_current_token(reason="logout")

# Automatic cleanup
TokenBlacklist.cleanup_expired_tokens()
```

### **Refresh Token Rotation**
```python
# Security: Each refresh generates new tokens
def refresh_token():
    # Revoke current refresh token
    TokenService.revoke_token(old_jti, reason="token_rotation")
    # Generate new access + refresh tokens
    return user.generate_tokens()
```

### **Security Validations**
- JWT type checking (`access` vs `refresh`)
- Token blacklist validation on each request
- Fresh JWT requirement for password changes
- Comprehensive input validation with custom validators

## 🛠 **Migration Notes for Flask-Security-Too**

When migrating to Flask-Security-Too, consider:

1. **Database Schema**: User table compatibility
2. **Token Management**: How Flask-Security handles sessions
3. **API Endpoints**: Mapping to Flask-Security routes
4. **Custom Features**: Token blacklist system preservation
5. **Security Policies**: Role-based access control migration

## 📊 **Performance Characteristics**

- **Stateless**: JWTs don't require server-side sessions
- **Scalable**: Token validation without database lookup
- **Secure**: Blacklist prevents token replay attacks
- **Efficient**: Automatic cleanup of expired tokens

---

**This implementation is production-ready** with enterprise-level security features including token rotation, blacklisting, and comprehensive validation.
