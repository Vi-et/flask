"""
Demo sử dụng hàm .build() trong Validation Builder Pattern
"""
from validators.validation_builder import validate_field, validate_schema


def demo_build_usage():
    """Demo cách sử dụng hàm .build() có ý nghĩa"""
    
    print("=== Demo .build() Usage ===\n")
    
    # 1. Build validator một lần, sử dụng nhiều lần
    print("1. Build validator một lần, tái sử dụng:")
    
    # Xây dựng validator
    email_validator = (validate_field('email')
                      .required()
                      .email()
                      .max_length(120)
                      .build())  # Build thành FieldValidator object
    
    # Sử dụng validator đã build nhiều lần
    test_emails = [
        "valid@example.com",
        "invalid-email",
        "",
        "very.long.email.address.that.exceeds.the.maximum.length.limit.of.120.characters@extremely-long-domain-name.com"
    ]
    
    for email in test_emails:
        if email_validator.is_valid(email):
            print(f"  ✅ '{email}' - Valid")
        else:
            error = email_validator.get_first_error(email)
            print(f"  ❌ '{email}' - {error}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. Build multiple validators from same builder template  
    print("2. Tạo nhiều validators từ cùng một template:")
    
    def create_name_builder():
        """Template builder cho name validation"""
        return validate_field().required().min_length(2).max_length(50)
    
    # Build validators cho các fields khác nhau từ cùng template
    first_name_validator = create_name_builder().build()
    last_name_validator = create_name_builder().build() 
    username_validator = create_name_builder().build()
    
    test_data = {
        'first_name': 'John',
        'last_name': 'A',  # Too short
        'username': 'john_doe123'
    }
    
    validators = {
        'first_name': first_name_validator,
        'last_name': last_name_validator, 
        'username': username_validator
    }
    
    for field, validator in validators.items():
        value = test_data.get(field, '')
        if validator.is_valid(value, field):
            print(f"  ✅ {field}: '{value}' - Valid")
        else:
            error = validator.get_first_error(value, field)
            print(f"  ❌ {field}: '{value}' - {error}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. Performance benefit - build once, use many times
    print("3. Performance optimization với .build():")
    
    # Builder pattern: Xây dựng rules một lần
    password_builder = (validate_field('password')
                       .required()
                       .min_length(8)
                       .password_strength())
    
    # Build thành validator object để tái sử dụng
    password_validator = password_builder.build()
    
    # Simulate validating nhiều passwords
    passwords_to_test = [
        "StrongPass123!",
        "weak",
        "NoSpecialChar123",
        "AnotherStrong456@"
    ]
    
    print("  Validating multiple passwords với built validator:")
    for pwd in passwords_to_test:
        result = password_validator.is_valid(pwd)
        print(f"    Password '{pwd}': {'✅ Strong' if result else '❌ Weak'}")
    
    print("\n" + "="*50 + "\n")
    
    # 4. Build validators và compose chúng
    print("4. Compose built validators:")
    
    # Build individual field validators
    name_validator = validate_field().required().min_length(2).max_length(50).build()
    email_validator = validate_field().required().email().build() 
    phone_validator = validate_field().matches(r'^\d{10,11}$', 'Invalid phone format').build()
    
    # Tạo composite validator
    class UserValidator:
        def __init__(self, name_val, email_val, phone_val):
            self.name_validator = name_val
            self.email_validator = email_val  
            self.phone_validator = phone_val
        
        def validate_user(self, user_data):
            errors = {}
            
            # Validate từng field với built validators
            if not self.name_validator.is_valid(user_data.get('name'), 'name'):
                errors['name'] = self.name_validator.get_first_error(user_data.get('name'), 'name')
                
            if not self.email_validator.is_valid(user_data.get('email'), 'email'):
                errors['email'] = self.email_validator.get_first_error(user_data.get('email'), 'email')
                
            phone = user_data.get('phone')
            if phone and not self.phone_validator.is_valid(phone, 'phone'):
                errors['phone'] = self.phone_validator.get_first_error(phone, 'phone')
            
            return errors
    
    # Sử dụng composite validator
    user_validator = UserValidator(name_validator, email_validator, phone_validator)
    
    test_user = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '0123456789'
    }
    
    errors = user_validator.validate_user(test_user)
    if not errors:
        print("  ✅ User data is completely valid!")
    else:
        print("  ❌ User validation errors:")
        for field, error in errors.items():
            print(f"    - {field}: {error}")


def demo_build_vs_direct():
    """So sánh giữa sử dụng .build() và direct validation"""
    
    print("\n=== So sánh .build() vs Direct Usage ===\n")
    
    # Method 1: Direct usage (không dùng .build())
    print("Method 1 - Direct validation (hiện tại):")
    builder = validate_field('email').required().email().max_length(120)
    
    result1 = builder.validate("test@example.com")
    print(f"  Direct: {result1}")
    
    # Method 2: Build first, then use (dùng .build())
    print("\nMethod 2 - Build first, then validate:")
    validator = (validate_field('email')
                .required()
                .email() 
                .max_length(120)
                .build())
    
    result2 = validator.validate("test@example.com")
    print(f"  Built: {result2}")
    
    print("\n✨ Lợi ích của .build():")
    print("  - Tách biệt rõ ràng giữa 'building rules' và 'using validator'")
    print("  - Validator object có thể được cache, serialize, hay pass around")
    print("  - Performance tốt hơn khi validate nhiều values với cùng rules")
    print("  - Immutable validator - không thể thay đổi rules sau khi build")


if __name__ == "__main__":
    demo_build_usage()
    demo_build_vs_direct()