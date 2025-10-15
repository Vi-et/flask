"""
Demo sử dụng Simplified Builder Pattern theo ý tưởng của bạn
"""
import sys
sys.path.append('/Users/apple/Downloads/project/flask')

from validators.validation_builder import ValidationBuilder, BaseValidation
from validators.auth_validators import SignUpValidator, LoginValidator


def demo_simple_builder_pattern():
    """Demo pattern đơn giản mà bạn đề xuất"""
    
    print("=== Demo Simple Builder Pattern ===\n")
    
    # Test SignUp validation
    print("1. Testing SignUp Validation:")
    
    # Valid signup data
    valid_signup = {'data': {'email': 'user@example.com', 'password': 'password123'}}
    result = SignUpValidator.validate(**valid_signup)
    
    print(f"Valid signup: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
    if not result.is_valid:
        for error in result.errors:
            print(f"  - {error}")
    
    # Invalid signup data
    invalid_signup = {'data': {'email': 'invalid-email', 'password': '123'}}
    result = SignUpValidator.validate(**invalid_signup)
    
    print(f"Invalid signup: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
    if not result.is_valid:
        for error in result.errors:
            print(f"  - {error}")
    
    print("\n" + "="*50 + "\n")
    
    # Test Login validation
    print("2. Testing Login Validation:")
    
    # Valid login data
    valid_login = {'data': {'email': 'user@example.com', 'password': 'password123'}}
    result = LoginValidator.validate(**valid_login)
    
    print(f"Valid login: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
    
    # Invalid login data (missing fields)
    invalid_login = {'data': {'email': '', 'password': ''}}
    result = LoginValidator.validate(**invalid_login)
    
    print(f"Invalid login: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
    if not result.is_valid:
        for error in result.errors:
            print(f"  - {error}")


def demo_create_custom_validator():
    """Demo tạo validator mới theo pattern này"""
    
    print("\n=== Demo Custom Validator ===\n")
    
    class ProductValidationBuilder(ValidationBuilder):
        def require_product_data(self):
            def validate(context):
                result = context['result']
                data = context.get('data', {})
                
                if not data.get('name') or len(data['name']) < 3:
                    result.add_error("Product name must be at least 3 characters")
                
                price = data.get('price')
                if not price or not isinstance(price, (int, float)) or price <= 0:
                    result.add_error("Price must be a positive number")
                    
            self.rules.append(validate)
            return self
    
    class ProductValidator(BaseValidation):
        @classmethod
        def get_validator(cls):
            return ProductValidationBuilder().require_product_data().build()
    
    # Test product validation
    print("Testing Product Validation:")
    
    # Valid product
    valid_product = {'data': {'name': 'iPhone 15', 'price': 999.99}}
    result = ProductValidator.validate(**valid_product)
    print(f"Valid product: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
    
    # Invalid product
    invalid_product = {'data': {'name': 'A', 'price': -10}}
    result = ProductValidator.validate(**invalid_product)
    print(f"Invalid product: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
    if not result.is_valid:
        for error in result.errors:
            print(f"  - {error}")


def demo_chaining_rules():
    """Demo chaining multiple validation rules"""
    
    print("\n=== Demo Chaining Rules ===\n")
    
    class UserValidationBuilder(ValidationBuilder):
        def require_basic_info(self):
            def validate(context):
                result = context['result']
                data = context.get('data', {})
                
                if not data.get('name') or len(data['name']) < 2:
                    result.add_error("Name must be at least 2 characters")
                    
            self.rules.append(validate)
            return self
            
        def require_contact_info(self):
            def validate(context):
                result = context['result']
                data = context.get('data', {})
                
                if not data.get('email') or '@' not in data['email']:
                    result.add_error("Invalid email format")
                if not data.get('phone') or len(data['phone']) < 10:
                    result.add_error("Phone number must be at least 10 digits")
                    
            self.rules.append(validate)
            return self
    
    class CompleteUserValidator(BaseValidation):
        @classmethod
        def get_validator(cls):
            return (UserValidationBuilder()
                   .require_basic_info()
                   .require_contact_info()
                   .build())
    
    # Test chained validation
    print("Testing Chained Validation:")
    
    # Complete valid data
    complete_data = {
        'data': {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '0123456789'
        }
    }
    result = CompleteUserValidator.validate(**complete_data)
    print(f"Complete data: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
    
    # Incomplete data
    incomplete_data = {
        'data': {
            'name': 'A',  # Too short
            'email': 'invalid',  # Invalid format
            'phone': '123'  # Too short
        }
    }
    result = CompleteUserValidator.validate(**incomplete_data)
    print(f"Incomplete data: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
    if not result.is_valid:
        print("  Errors:")
        for error in result.errors:
            print(f"    - {error}")


if __name__ == "__main__":
    demo_simple_builder_pattern()
    demo_create_custom_validator() 
    demo_chaining_rules()