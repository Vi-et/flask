# Validation Builder Pattern

Hệ thống validation sử dụng Builder Pattern để tạo ra các validation rules một cách linh hoạt, dễ đọc và có thể tái sử dụng.

## 🏗️ Tại sao sử dụng Builder Pattern?

### Trước khi có Builder Pattern:
```python
# Code cũ - khó đọc và maintain
def validate_user_registration(data):
    if not data.get('name') or len(data['name']) < 2:
        return "Name must be at least 2 characters"
    if not data.get('email') or '@' not in data['email']:
        return "Invalid email"
    if not data.get('password') or len(data['password']) < 8:
        return "Password must be at least 8 characters"
    # ... nhiều validation khác
```

### Sau khi có Builder Pattern:
```python
# Code mới - rõ ràng, linh hoạt và tái sử dụng được
schema = validate_schema()
schema.field('name').required().min_length(2).max_length(50)
schema.field('email').required().email().custom(check_uniqueness, "Email already exists")  
schema.field('password').required().min_length(8).password_strength()

errors = schema.validate(data)
```

## 🚀 Các cách sử dụng

### 1. Validation đơn giản cho một field
```python
from validators.validation_builder import validate_field

# Tạo validator cho tên
name_validator = validate_field('name').required().min_length(2).max_length(50)

# Validate
errors = name_validator.validate("John Doe")
is_valid = name_validator.is_valid("John Doe")
```

### 2. Schema validation cho nhiều fields
```python
from validators.validation_builder import validate_schema

# Tạo schema cho user registration
schema = validate_schema()
schema.field('name').required().min_length(2).max_length(50)
schema.field('email').required().email()
schema.field('password').required().min_length(8).password_strength()

# Validate toàn bộ data
user_data = {
    'name': 'John Doe',
    'email': 'john@example.com', 
    'password': 'StrongPass123!'
}

errors = schema.validate(user_data)
if not errors:
    print("✅ All valid!")
else:
    for field, field_errors in errors.items():
        print(f"❌ {field}: {', '.join(field_errors)}")
```

### 3. Custom validation rules
```python
# Thêm custom validation logic
def check_username_unique(username):
    # Logic kiểm tra username đã tồn tại chưa
    return User.query.filter_by(username=username).first() is None

schema.field('username').required().min_length(3).custom(
    check_username_unique,
    "Username already exists"
)
```

### 4. Sử dụng predefined validators
```python
from validators.validation_builder import email_validation, password_validation, name_validation

# Sử dụng các validation đã định nghĩa sẵn
email_errors = email_validation().validate("user@example.com")
password_errors = password_validation().validate("weak")  # Sẽ fail
name_errors = name_validation().validate("Valid Name")
```

## 🔧 Available Validation Rules

### Basic Rules
- `.required(message)` - Field bắt buộc
- `.min_length(length, message)` - Độ dài tối thiểu
- `.max_length(length, message)` - Độ dài tối đa
- `.min_value(value, message)` - Giá trị tối thiểu
- `.max_value(value, message)` - Giá trị tối đa

### Format Rules  
- `.email(message)` - Định dạng email
- `.numeric(message)` - Chỉ chấp nhận số
- `.matches(pattern, message)` - Regex pattern matching

### Advanced Rules
- `.password_strength(message)` - Password mạnh (8+ ký tự, có chữ hoa, thường, số, ký tự đặc biệt)
- `.in_choices(choices, message)` - Giá trị phải nằm trong danh sách cho phép
- `.custom(function, message)` - Custom validation function

## 🎯 Integration với Auth Validators

Các auth validators đã được refactor để sử dụng Builder Pattern:

```python
from validators.auth_validators import validate_user_registration

# Sử dụng như trước, nhưng bên trong đã dùng Builder Pattern
result = validate_user_registration({
    'name': 'John Doe',
    'email': 'john@example.com',
    'password': 'StrongPass123!'
})

if result.is_valid:
    print("✅ Registration data valid!")
else:
    print(f"❌ Error: {result.get_first_error()}")
```

## 📊 Lợi ích của Builder Pattern

### 1. **Fluent Interface** - Dễ đọc và viết
```python
# Rất dễ hiểu ý nghĩa
validator = (validate_field('email')
            .required()
            .email()
            .max_length(120))
```

### 2. **Reusability** - Tái sử dụng cao
```python
# Định nghĩa một lần, dùng nhiều chỗ
email_validator = email_validation()

# Dùng cho registration
registration_schema.field('email').required().email()

# Dùng cho profile update
profile_schema.field('email').email()  # Không bắt buộc cho update
```

### 3. **Flexibility** - Linh hoạt
```python
# Có thể thêm/bớt rules dễ dàng
basic_password = validate_field().required().min_length(6)
strong_password = validate_field().required().min_length(8).password_strength()
```

### 4. **Maintainability** - Dễ maintain
```python
# Thay đổi validation rules không ảnh hưởng đến business logic
# Chỉ cần sửa trong builder definition
```

### 5. **Testability** - Dễ test
```python
# Test từng rule riêng biệt
assert not validate_field().required().is_valid("")
assert validate_field().required().is_valid("valid_value")
```

## 🔄 Migration từ validators cũ

### Trước:
```python
class UserRegistrationValidator(BaseValidator):
    def validate(self):
        if not self.data.get('name'):
            self.result.add_error("Name is required")
        if len(self.data.get('name', '')) < 2:
            self.result.add_error("Name too short")
        # ... nhiều if/else
```

### Sau:
```python  
class UserRegistrationValidator(BaseValidator):
    def __init__(self, data):
        super().__init__(data)
        self.schema = self._build_schema()
    
    def _build_schema(self):
        schema = validate_schema()
        schema.field('name').required().min_length(2).max_length(50)
        return schema
    
    def validate(self):
        errors = self.schema.validate(self.data)
        # Convert errors to ValidationResult format
```

## 🎨 Best Practices

1. **Nhóm các validation rules logic** - Tách riêng business rules và format rules
2. **Sử dụng predefined validators** cho các trường hợp thông dụng
3. **Custom validators cho business logic** phức tạp
4. **Chain validation** một cách hợp lý - từ basic đến complex
5. **Error messages rõ ràng** và user-friendly

Với Builder Pattern, việc tạo và quản lý validation trở nên đơn giản, linh hoạt và professional hơn rất nhiều! 🚀