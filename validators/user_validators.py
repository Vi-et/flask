"""
User Validators
Validation logic for user management operations
"""
from typing import Dict, Any
from validators import BaseValidator, ValidationResult
from models.user import User


class UserCreateValidator(BaseValidator):
    """Validator for creating users (admin operation)"""
    
    def validate(self) -> ValidationResult:
        """Validate user creation data"""
        
        # Check required fields
        required_fields = ['name', 'email']
        self.validate_required_fields(required_fields)
        
        # If required fields are missing, return early
        if not self.result.is_valid:
            return self.result
        
        # Validate individual fields
        self.validate_name()
        self.validate_email_field()
        self.validate_email_uniqueness()
        
        # Validate optional fields
        if 'password' in self.data:
            self.validate_password_strength('password', min_length=6)
        
        if 'is_admin' in self.data:
            self.validate_boolean('is_admin')
        
        if 'is_active' in self.data:
            self.validate_boolean('is_active')
        
        return self.result
    
    def validate_name(self) -> bool:
        """Validate user name"""
        return self.validate_string_length('name', min_length=2, max_length=100)
    
    def validate_email_field(self) -> bool:
        """Validate email format and length"""
        email_valid = self.validate_email('email')
        length_valid = self.validate_string_length('email', max_length=120)
        return email_valid and length_valid
    
    def validate_email_uniqueness(self) -> bool:
        """Check if email is already registered"""
        if 'email' not in self.data or not self.result.is_valid:
            return True
        
        email = self.data['email'].strip().lower()
        existing_user = User.get_by_email(email)
        
        if existing_user:
            self.result.add_field_error('email', 'Email is already registered')
            return False
        
        return True


class UserUpdateValidator(BaseValidator):
    """Validator for updating users (admin operation)"""
    
    def __init__(self, data: Dict[str, Any], user_id: int = None):
        super().__init__(data)
        self.user_id = user_id
    
    def validate(self) -> ValidationResult:
        """Validate user update data"""
        
        # At least one field must be provided
        updatable_fields = ['name', 'email', 'is_admin', 'is_active', 'password']
        has_update_field = any(field in self.data for field in updatable_fields)
        
        if not has_update_field:
            self.result.add_error('At least one field must be provided for update')
            return self.result
        
        # Validate individual fields if present
        if 'name' in self.data:
            self.validate_name()
        
        if 'email' in self.data:
            self.validate_email_field()
            self.validate_email_uniqueness()
        
        if 'password' in self.data:
            self.validate_password_strength('password', min_length=6)
        
        if 'is_admin' in self.data:
            self.validate_boolean('is_admin')
        
        if 'is_active' in self.data:
            self.validate_boolean('is_active')
        
        return self.result
    
    def validate_name(self) -> bool:
        """Validate name update"""
        if not str(self.data.get('name', '')).strip():
            self.result.add_field_error('name', 'Name cannot be empty')
            return False
        
        return self.validate_string_length('name', min_length=2, max_length=100)
    
    def validate_email_field(self) -> bool:
        """Validate email update"""
        if not str(self.data.get('email', '')).strip():
            self.result.add_field_error('email', 'Email cannot be empty')
            return False
        
        email_valid = self.validate_email('email')
        length_valid = self.validate_string_length('email', max_length=120)
        return email_valid and length_valid
    
    def validate_email_uniqueness(self) -> bool:
        """Check if email is already taken by another user"""
        if 'email' not in self.data or not self.result.is_valid:
            return True
        
        email = self.data['email'].strip().lower()
        existing_user = User.get_by_email(email)
        
        # Email is taken if it exists and belongs to different user
        if existing_user and existing_user.id != self.user_id:
            self.result.add_field_error('email', 'Email is already taken by another user')
            return False
        
        return True


class UserSearchValidator(BaseValidator):
    """Validator for user search parameters"""
    
    def validate(self) -> ValidationResult:
        """Validate search parameters"""
        
        # Validate query if provided
        if 'query' in self.data:
            query = str(self.data.get('query', '')).strip()
            if len(query) < 2:
                self.result.add_field_error('query', 'Search query must be at least 2 characters')
        
        # Validate pagination parameters
        if 'page' in self.data:
            self.validate_integer('page', min_value=1)
        
        if 'per_page' in self.data:
            self.validate_integer('per_page', min_value=1, max_value=100)
        
        # Validate filter parameters
        if 'is_active' in self.data:
            self.validate_boolean('is_active')
        
        if 'is_admin' in self.data:
            self.validate_boolean('is_admin')
        
        return self.result


class UserBulkOperationValidator(BaseValidator):
    """Validator for bulk operations on users"""
    
    def validate(self) -> ValidationResult:
        """Validate bulk operation data"""
        
        # Check required fields
        required_fields = ['user_ids', 'operation']
        self.validate_required_fields(required_fields)
        
        if not self.result.is_valid:
            return self.result
        
        # Validate user_ids
        self.validate_user_ids()
        
        # Validate operation
        allowed_operations = ['activate', 'deactivate', 'delete', 'make_admin', 'remove_admin']
        self.validate_choice('operation', allowed_operations)
        
        return self.result
    
    def validate_user_ids(self) -> bool:
        """Validate user IDs list"""
        user_ids = self.data.get('user_ids', [])
        
        if not isinstance(user_ids, list):
            self.result.add_field_error('user_ids', 'Must be a list of user IDs')
            return False
        
        if not user_ids:
            self.result.add_field_error('user_ids', 'At least one user ID must be provided')
            return False
        
        if len(user_ids) > 50:  # Limit bulk operations
            self.result.add_field_error('user_ids', 'Cannot process more than 50 users at once')
            return False
        
        # Validate each ID is a positive integer
        for i, user_id in enumerate(user_ids):
            try:
                id_val = int(user_id)
                if id_val <= 0:
                    self.result.add_field_error('user_ids', f'Invalid user ID at position {i + 1}')
                    return False
            except (ValueError, TypeError):
                self.result.add_field_error('user_ids', f'Invalid user ID at position {i + 1}')
                return False
        
        return True


# Validator factory functions
def validate_user_create(data: Dict[str, Any]) -> ValidationResult:
    """Validate user creation data"""
    validator = UserCreateValidator(data)
    return validator.validate()


def validate_user_update(data: Dict[str, Any], user_id: int = None) -> ValidationResult:
    """Validate user update data"""
    validator = UserUpdateValidator(data, user_id)
    return validator.validate()


def validate_user_search(data: Dict[str, Any]) -> ValidationResult:
    """Validate user search parameters"""
    validator = UserSearchValidator(data)
    return validator.validate()


def validate_user_bulk_operation(data: Dict[str, Any]) -> ValidationResult:
    """Validate bulk operation data"""
    validator = UserBulkOperationValidator(data)
    return validator.validate()