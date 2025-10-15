"""
Base Validator
Core validation framework with common patterns
"""
import re
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod


class ValidationResult:
    """Container for validation results"""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None, field_errors: Dict[str, List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.field_errors = field_errors or {}
    
    def add_error(self, error: str):
        """Add general error"""
        self.is_valid = False
        self.errors.append(error)
    
    def add_field_error(self, field: str, error: str):
        """Add field-specific error"""
        self.is_valid = False
        if field not in self.field_errors:
            self.field_errors[field] = []
        self.field_errors[field].append(error)
    
    def get_all_errors(self) -> List[str]:
        """Get all errors as flat list"""
        all_errors = self.errors.copy()
        for field, field_errs in self.field_errors.items():
            for err in field_errs:
                all_errors.append(f"{field}: {err}")
        return all_errors
    
    def get_first_error(self) -> Optional[str]:
        """Get first error message"""
        if self.errors:
            return self.errors[0]
        for field, field_errs in self.field_errors.items():
            if field_errs:
                return f"{field}: {field_errs[0]}"
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'is_valid': self.is_valid,
            'errors': self.errors,
            'field_errors': self.field_errors
        }


class BaseValidator(ABC):
    """Base validator class with common validation methods"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.result = ValidationResult()
    
    @abstractmethod
    def validate(self) -> ValidationResult:
        """Main validation method - must be implemented by subclasses"""
        pass
    
    # Common validation methods
    def validate_required_fields(self, fields: List[str]) -> bool:
        """Validate that required fields are present and not empty"""
        all_valid = True
        for field in fields:
            if field not in self.data:
                self.result.add_field_error(field, "This field is required")
                all_valid = False
            elif not str(self.data[field]).strip():
                self.result.add_field_error(field, "This field cannot be empty")
                all_valid = False
        return all_valid
    
    def validate_string_length(self, field: str, min_length: int = None, max_length: int = None) -> bool:
        """Validate string length"""
        if field not in self.data:
            return True  # Field validation should be handled by required_fields
        
        value = str(self.data[field]).strip()
        
        if min_length and len(value) < min_length:
            self.result.add_field_error(field, f"Must be at least {min_length} characters long")
            return False
        
        if max_length and len(value) > max_length:
            self.result.add_field_error(field, f"Must not exceed {max_length} characters")
            return False
        
        return True
    
    def validate_email(self, field: str = 'email') -> bool:
        """Validate email format"""
        if field not in self.data:
            return True
        
        email = str(self.data[field]).strip().lower()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            self.result.add_field_error(field, "Invalid email format")
            return False
        
        return True
    
    def validate_password_strength(self, field: str = 'password', min_length: int = 6) -> bool:
        """Validate password strength"""
        if field not in self.data:
            return True
        
        password = str(self.data[field])
        
        if len(password) < min_length:
            self.result.add_field_error(field, f"Password must be at least {min_length} characters long")
            return False
        
        # Additional password rules can be added here
        # Example: require uppercase, lowercase, numbers, special chars
        
        return True
    
    def validate_numeric(self, field: str, min_value: float = None, max_value: float = None) -> bool:
        """Validate numeric values"""
        if field not in self.data:
            return True
        
        try:
            value = float(self.data[field])
            
            if min_value is not None and value < min_value:
                self.result.add_field_error(field, f"Must be at least {min_value}")
                return False
            
            if max_value is not None and value > max_value:
                self.result.add_field_error(field, f"Must not exceed {max_value}")
                return False
            
            return True
            
        except (ValueError, TypeError):
            self.result.add_field_error(field, "Must be a valid number")
            return False
    
    def validate_integer(self, field: str, min_value: int = None, max_value: int = None) -> bool:
        """Validate integer values"""
        if field not in self.data:
            return True
        
        try:
            value = int(self.data[field])
            
            if min_value is not None and value < min_value:
                self.result.add_field_error(field, f"Must be at least {min_value}")
                return False
            
            if max_value is not None and value > max_value:
                self.result.add_field_error(field, f"Must not exceed {max_value}")
                return False
            
            return True
            
        except (ValueError, TypeError):
            self.result.add_field_error(field, "Must be a valid integer")
            return False
    
    def validate_choice(self, field: str, choices: List[Any]) -> bool:
        """Validate that field value is in allowed choices"""
        if field not in self.data:
            return True
        
        value = self.data[field]
        if value not in choices:
            self.result.add_field_error(field, f"Must be one of: {', '.join(map(str, choices))}")
            return False
        
        return True
    
    def validate_boolean(self, field: str) -> bool:
        """Validate boolean field"""
        if field not in self.data:
            return True
        
        value = self.data[field]
        if not isinstance(value, bool):
            try:
                # Try to convert string to boolean
                if isinstance(value, str):
                    lower_val = value.lower()
                    if lower_val in ['true', '1', 'yes', 'on']:
                        self.data[field] = True
                        return True
                    elif lower_val in ['false', '0', 'no', 'off']:
                        self.data[field] = False
                        return True
                
                self.result.add_field_error(field, "Must be a boolean value (true/false)")
                return False
                
            except (ValueError, TypeError):
                self.result.add_field_error(field, "Must be a boolean value (true/false)")
                return False
        
        return True
    
    def validate_url(self, field: str) -> bool:
        """Validate URL format"""
        if field not in self.data:
            return True
        
        url = str(self.data[field]).strip()
        url_pattern = r'^https?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w\/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        
        if not re.match(url_pattern, url):
            self.result.add_field_error(field, "Invalid URL format")
            return False
        
        return True
    
    def validate_phone(self, field: str) -> bool:
        """Validate phone number format (basic)"""
        if field not in self.data:
            return True
        
        phone = str(self.data[field]).strip()
        # Basic phone validation - digits, spaces, dashes, parentheses, plus sign
        phone_pattern = r'^[\+]?[\d\s\-\(\)]{10,15}$'
        
        if not re.match(phone_pattern, phone):
            self.result.add_field_error(field, "Invalid phone number format")
            return False
        
        return True
    
    def validate_date_string(self, field: str, date_format: str = '%Y-%m-%d') -> bool:
        """Validate date string format"""
        if field not in self.data:
            return True
        
        from datetime import datetime
        
        date_str = str(self.data[field]).strip()
        try:
            datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            self.result.add_field_error(field, f"Invalid date format. Expected: {date_format}")
            return False
    
    def validate_custom(self, field: str, validator_func: callable, error_message: str) -> bool:
        """Run custom validation function"""
        if field not in self.data:
            return True
        
        try:
            if not validator_func(self.data[field]):
                self.result.add_field_error(field, error_message)
                return False
            return True
        except Exception:
            self.result.add_field_error(field, "Validation error occurred")
            return False


class ValidationHelper:
    """Helper class for common validation tasks"""
    
    @staticmethod
    def validate_data(validator_class, data: Dict[str, Any]) -> ValidationResult:
        """Convenience method to validate data with a validator class"""
        validator = validator_class(data)
        return validator.validate()
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if email is valid"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email.strip().lower()))
    
    @staticmethod
    def is_strong_password(password: str, min_length: int = 6) -> bool:
        """Check if password meets strength requirements"""
        return len(password) >= min_length
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value)
        return value.strip()
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize email input"""
        if not isinstance(email, str):
            return str(email)
        return email.strip().lower()