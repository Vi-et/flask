"""
Example usage of Validation Builder Pattern
Demo các cách sử dụng Builder Pattern cho validation
"""
from validators.validation_builder import (
    ValidationBuilder,
    ValidationSchema,
    validate_field,
    validate_schema,
    email_validation,
    password_validation,
    name_validation
)


def demo_simple_validation():
    """Demo basic field validation using Builder Pattern"""
    print("=== Demo Simple Validation ===")
    
    # Validate a single field using builder
    name_validator = validate_field('name').required().min_length(2).max_length(50)
    
    # Test cases
    test_cases = ["John", "A", "", "This is a very long name that exceeds the maximum length limit"]
    
    for test_name in test_cases:
        errors = name_validator.validate(test_name)
        print(f"Name '{test_name}': {'✅ Valid' if not errors else '❌ ' + ', '.join(errors)}")
    print()


def demo_schema_validation():
    """Demo schema validation using Builder Pattern"""
    print("=== Demo Schema Validation ===")
    
    # Build a user registration schema
    schema = validate_schema()
    schema.field('name').required().min_length(2).max_length(50)
    schema.field('email').required().email()
    schema.field('password').required().min_length(8).password_strength()
    schema.field('age').numeric().min_value(18).max_value(100)
    
    # Test data
    test_users = [
        {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'StrongPass123!',
            'age': 25
        },
        {
            'name': 'A',  # Too short
            'email': 'invalid-email',  # Invalid format
            'password': '123',  # Too weak
            'age': 15  # Too young
        },
        {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'password': 'AnotherStrong456@'
            # age missing - should be ok since not required
        }
    ]
    
    for i, user_data in enumerate(test_users, 1):
        print(f"User {i} validation:")
        errors = schema.validate(user_data)
        
        if not errors:
            print("  ✅ All fields valid")
        else:
            for field, field_errors in errors.items():
                for error in field_errors:
                    print(f"  ❌ {error}")
        print()


def demo_complex_validation():
    """Demo complex custom validation using Builder Pattern"""
    print("=== Demo Complex Validation ===")
    
    def check_username_format(username):
        """Custom validator: username must be alphanumeric with underscores"""
        import re
        return re.match(r'^[a-zA-Z0-9_]+$', username) is not None
    
    def check_confirm_password(confirm_password, original_data):
        """Custom validator: confirm password must match password"""
        return confirm_password == original_data.get('password', '')
    
    # Build complex schema with custom validations
    schema = validate_schema()
    schema.field('username').required().min_length(3).max_length(20).custom(
        check_username_format,
        "Username must contain only letters, numbers and underscores"
    )
    schema.field('password').required().min_length(8).password_strength()
    schema.field('confirm_password').required().custom(
        lambda x: check_confirm_password(x, {}),  # This is simplified for demo
        "Confirm password must match password"
    )
    schema.field('role').in_choices(['admin', 'user', 'moderator'])
    
    # Test data
    test_data = {
        'username': 'john_doe123',
        'password': 'StrongPass123!',
        'confirm_password': 'StrongPass123!',
        'role': 'admin'
    }
    
    print("Complex validation test:")
    errors = schema.validate(test_data)
    
    if not errors:
        print("  ✅ All validations passed")
    else:
        for field, field_errors in errors.items():
            for error in field_errors:
                print(f"  ❌ {error}")
    print()


def demo_predefined_validators():
    """Demo using predefined validation builders"""
    print("=== Demo Predefined Validators ===")
    
    # Using predefined validators
    test_data = {
        'email': 'user@example.com',
        'password': 'WeakPass',  # This should fail strength test
        'name': 'Valid Name'
    }
    
    # Test email validation
    email_errors = email_validation().validate(test_data['email'])
    print(f"Email validation: {'✅ Valid' if not email_errors else '❌ ' + ', '.join(email_errors)}")
    
    # Test password validation (strong)
    password_errors = password_validation().validate(test_data['password'])
    print(f"Password validation: {'✅ Valid' if not password_errors else '❌ ' + ', '.join(password_errors)}")
    
    # Test name validation
    name_errors = name_validation().validate(test_data['name'])
    print(f"Name validation: {'✅ Valid' if not name_errors else '❌ ' + ', '.join(name_errors)}")
    print()


def demo_fluent_api():
    """Demo fluent API style validation building"""
    print("=== Demo Fluent API ===")
    
    # Build validation chain fluently
    product_validator = (validate_field('product')
                        .required("Product name is required")
                        .min_length(3, "Product name must be at least 3 characters")
                        .max_length(100, "Product name must not exceed 100 characters")
                        .matches(r'^[a-zA-Z0-9\s\-_]+$', "Product name contains invalid characters"))
    
    price_validator = (validate_field('price')
                      .required("Price is required")
                      .numeric("Price must be a number")
                      .min_value(0.01, "Price must be greater than 0")
                      .max_value(99999.99, "Price cannot exceed $99,999.99"))
    
    # Test cases
    test_products = [
        {'name': 'iPhone 15 Pro', 'price': 999.99},
        {'name': 'A', 'price': -10},  # Invalid
        {'name': 'Valid Product Name', 'price': 49.99}
    ]
    
    for product in test_products:
        print(f"Product: {product}")
        
        name_errors = product_validator.validate(product.get('name'))
        if name_errors:
            print(f"  ❌ Name: {', '.join(name_errors)}")
        else:
            print(f"  ✅ Name: Valid")
            
        price_errors = price_validator.validate(product.get('price'))
        if price_errors:
            print(f"  ❌ Price: {', '.join(price_errors)}")
        else:
            print(f"  ✅ Price: Valid")
        print()


if __name__ == "__main__":
    demo_simple_validation()
    demo_schema_validation()
    demo_complex_validation()
    demo_predefined_validators()
    demo_fluent_api()