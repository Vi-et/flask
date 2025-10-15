# 🔐 JWT Authentication System

## Tổng quan

Hệ thống authentication được xây dựng với **JWT (JSON Web Tokens)** cho Flask API, bao gồm:

- ✅ User registration & login
- ✅ JWT token generation & validation
- ✅ Password hashing với Werkzeug
- ✅ Role-based access control (Admin/User)
- ✅ Route protection decorators
- ✅ Token refresh mechanism

## 🏗️ Architecture

### **Components:**
1. **User Model** - Extended với auth fields
2. **AuthService** - Business logic layer
3. **JWT Config** - Token configuration
4. **Auth Decorators** - Route protection
5. **Auth Routes** - API endpoints

## 📊 Database Schema

### **Updated User Table:**
```sql
users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,    -- NEW
    is_active BOOLEAN DEFAULT 1,            -- NEW
    is_admin BOOLEAN DEFAULT 0,             -- NEW
    last_login DATETIME,                    -- NEW
    created_at DATETIME,
    updated_at DATETIME
)
```

## 🚀 Quick Start

### **1. Setup Environment**
```bash
# Add to .env
JWT_SECRET_KEY=your-super-secret-jwt-key-here
```

### **2. Run Migration**
```bash
python3 migrate_auth.py
```

### **3. Start Server**
```bash
python3 app.py
```

## 📡 API Endpoints

### **Authentication Routes (`/api/auth/`)**

#### **Register User**
```bash
POST /api/auth/register
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
}

# Response:
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "user": {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "is_active": true,
            "is_admin": false,
            "last_login": null
        },
        "tokens": {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    }
}
```

#### **Login**
```bash
POST /api/auth/login
Content-Type: application/json

{
    "email": "john@example.com",
    "password": "password123"
}

# Response: Same as register
```

#### **Get Profile**
```bash
GET /api/auth/me
Authorization: Bearer <access_token>

# Response:
{
    "success": true,
    "data": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "is_active": true,
        "is_admin": false,
        "last_login": "2025-10-15T15:30:45"
    }
}
```

#### **Update Profile**
```bash
PUT /api/auth/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "name": "John Smith",
    "email": "johnsmith@example.com"
}
```

#### **Change Password**
```bash
PUT /api/auth/change-password
Authorization: Bearer <fresh_access_token>
Content-Type: application/json

{
    "current_password": "password123",
    "new_password": "newpassword456"
}
```

#### **Refresh Token**
```bash
POST /api/auth/refresh
Authorization: Bearer <refresh_token>

# Response:
{
    "success": true,
    "data": {
        "tokens": {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    }
}
```

#### **Logout**
```bash
POST /api/auth/logout
Authorization: Bearer <access_token>
```

## 🛡️ Route Protection

### **Available Decorators:**

#### **1. Basic Authentication**
```python
from utils.auth_decorators import auth_required
from flask_jwt_extended import jwt_required

@route('/protected')
@jwt_required()  # Require valid JWT
def protected_route():
    pass

@route('/optional-auth')
@auth_required(optional=True)  # Optional auth
def optional_auth_route():
    pass
```

#### **2. Admin Required**
```python
from utils.auth_decorators import admin_required

@route('/admin-only')
@admin_required()  # Only admins can access
def admin_route():
    pass
```

#### **3. Active User Required**
```python
from utils.auth_decorators import active_user_required

@route('/active-only')
@active_user_required()  # Only active users
def active_user_route():
    pass
```

#### **4. Owner or Admin**
```python
from utils.auth_decorators import owner_or_admin_required

@route('/users/<int:user_id>/profile')
@owner_or_admin_required(user_id_param='user_id')
def user_profile(user_id):
    # User can only access their own profile, or admin can access any
    pass
```

#### **5. Fresh Token Required**
```python
from utils.auth_decorators import fresh_jwt_required

@route('/sensitive-action')
@fresh_jwt_required()  # Requires recently issued token
def sensitive_action():
    pass
```

## 🔧 Usage in Services

### **Get Current User:**
```python
from flask_jwt_extended import get_jwt_identity
from utils.auth_decorators import get_current_user_helper

# In route
@jwt_required()
def my_route():
    user_id = get_jwt_identity()
    user = get_current_user_helper()
```

### **Check Permissions:**
```python
from utils.auth_decorators import is_current_user_admin

if is_current_user_admin():
    # Admin-only logic
    pass
```

## 🧪 Testing Examples

### **1. Register New User**
```bash
curl -X POST "http://127.0.0.1:8888/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test User",
       "email": "test@example.com",
       "password": "password123"
     }'
```

### **2. Login**
```bash
curl -X POST "http://127.0.0.1:8888/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "password123"
     }'
```

### **3. Access Protected Route**
```bash
# Save token from login response
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

curl -X GET "http://127.0.0.1:8888/api/auth/me" \
     -H "Authorization: Bearer $TOKEN"
```

### **4. Update Profile**
```bash
curl -X PUT "http://127.0.0.1:8888/api/auth/me" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Updated Name"
     }'
```

## 🔐 Security Features

### **Password Security:**
- ✅ Werkzeug password hashing (scrypt)
- ✅ Minimum 6 character requirement
- ✅ Password validation on change

### **JWT Security:**
- ✅ 1 hour access token expiry
- ✅ 30 day refresh token expiry
- ✅ User claims in token payload
- ✅ Fresh token requirement for sensitive operations

### **Access Control:**
- ✅ Role-based permissions (Admin/User)
- ✅ Active user verification
- ✅ Owner-only resource access
- ✅ Comprehensive error handling

## ⚡ Advanced Usage

### **Custom Authentication Logic:**
```python
# In your route
from flask_jwt_extended import get_jwt, get_jwt_identity

@route('/custom-auth')
@jwt_required()
def custom_auth():
    claims = get_jwt()
    user_id = get_jwt_identity()

    if claims.get('is_admin'):
        # Admin logic
        pass
    elif claims.get('is_active'):
        # Regular user logic
        pass
```

### **Token Blacklisting (Future):**
```python
# For logout implementation
blacklisted_tokens = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload['jti'] in blacklisted_tokens
```

## 🚨 Error Handling

### **Common JWT Errors:**
- `401` - Missing/Invalid/Expired token
- `403` - Insufficient privileges
- `404` - User not found
- `409` - Email already exists
- `400` - Validation errors

### **Error Response Format:**
```json
{
    "success": false,
    "message": "Token has expired",
    "error": "token_expired"
}
```

## 📋 Migration Guide

### **From No Auth → JWT Auth:**

1. **Run migration:**
   ```bash
   python3 migrate_auth.py
   ```

2. **Update existing users:**
   - Default password: `defaultpassword123`
   - Users must change passwords

3. **Add auth to routes:**
   ```python
   # Before
   @route('/users')
   def get_users():
       pass

   # After
   @route('/users')
   @jwt_required()  # Add this
   def get_users():
       pass
   ```

## 🎯 Best Practices

### **Route Protection:**
```python
# ✅ Good - Specific permissions
@admin_required()
def admin_endpoint():
    pass

@owner_or_admin_required()
def user_resource(user_id):
    pass

# ❌ Avoid - Generic auth everywhere
@jwt_required()  # Too broad
def public_info():
    pass
```

### **Token Management:**
```python
# ✅ Good - Handle token refresh
def api_call_with_refresh():
    try:
        return make_api_call()
    except TokenExpired:
        refresh_token()
        return make_api_call()

# ✅ Good - Use fresh tokens for sensitive ops
@fresh_jwt_required()
def change_password():
    pass
```

---

🔐 **JWT Authentication system ready for production use!**
