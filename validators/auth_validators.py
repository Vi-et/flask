from validators.validation_builder import BaseValidation, ValidationBuilder
from models.user import User
class AuthValidationBuilder(ValidationBuilder):
    def require_signup_data(self):
        def validate(builder, **kwargs):
            email = kwargs.get('email', '').strip()
            password = kwargs.get('password', '')
            name = kwargs.get('name', '').strip()
            
            # Push errors if validation fails
            if not email:
                builder.push_error("Email is required")
            elif '@' not in email or '.' not in email.split('@')[-1]:
                builder.push_error("Invalid email format")
            
            user_by_email = User.get_by_email(email)
            if user_by_email:
                builder.push_error("Email is already registered")
                
            if not password:
                builder.push_error("Password is required")
            elif len(password) < 6:
                builder.push_error("Password must be at least 6 characters long")
                
            if not name:
                builder.push_error("Name is required")
            elif len(name) < 2:
                builder.push_error("Name must be at least 2 characters long")
                
        self.rules.append(validate)
        return self
    
    def require_login_data(self):
        def validate(builder, **kwargs):
            data = kwargs.get('data', {})
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            # Push errors if validation fails
            if not email:
                builder.push_error("Email is required")
            elif '@' not in email:
                builder.push_error("Invalid email format")
                
            if not password:
                builder.push_error("Password is required")
                
        self.rules.append(validate)
        return self


class SignUpValidator(BaseValidation):
    @classmethod
    def get_builder(cls):
        return AuthValidationBuilder().require_signup_data()


class LoginValidator(BaseValidation):
    @classmethod
    def get_builder(cls):
        return AuthValidationBuilder().require_login_data()


class ProfileUpdateValidator(BaseValidation):
    @classmethod
    def get_builder(cls):
        return AuthValidationBuilder()  # Add profile validation rules later


class PasswordChangeValidator(BaseValidation):
    @classmethod
    def get_builder(cls):
        return AuthValidationBuilder()  # Add password change validation rules later


class UserCredentialsValidator(BaseValidation):
    @classmethod
    def get_builder(cls):
        return AuthValidationBuilder().require_login_data()