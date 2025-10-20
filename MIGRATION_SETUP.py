"""
Quick Start Guide - Database Migration Setup
============================================

Flask-Migrate đã được thêm vào requirements.txt.
Đây là hướng dẫn setup nhanh.
"""

# Step 1: Install dependencies
print("Step 1: Installing dependencies...")
print("pip install -r requirements.txt")
print()

# Step 2: Add to app_factory.py
print("Step 2: Add migration to app_factory.py")
print("─" * 50)
print(
    """
# Thêm import này vào đầu file:
from flask_migrate import Migrate

# Thêm vào function create_app(), sau dòng db.init_app(app):
def create_app(config_name: Optional[str] = None) -> Flask:
    # ... existing code ...

    # Initialize extensions
    db.init_app(app)

    # Add this line:
    migrate = Migrate(app, db)  # <-- Thêm dòng này

    AuthApp.init_app(app)
    # ... rest of code ...
"""
)
print()

# Step 3: Initialize migrations
print("Step 3: Initialize migrations folder")
print("─" * 50)
print("flask db init")
print()
print("Lệnh này sẽ tạo folder 'migrations/' chứa migration files")
print()

# Step 4: Create first migration
print("Step 4: Create initial migration")
print("─" * 50)
print('flask db migrate -m "Initial migration"')
print()
print("Lệnh này sẽ scan models và tạo migration file")
print()

# Step 5: Apply migration
print("Step 5: Apply migration to database")
print("─" * 50)
print("flask db upgrade")
print()
print("Lệnh này sẽ apply migration vào database")
print()

# Common commands
print("=" * 50)
print("COMMON MIGRATION COMMANDS")
print("=" * 50)
print()
print("# Tạo migration mới sau khi sửa models:")
print('flask db migrate -m "Add email_verified column to users"')
print()
print("# Apply migrations:")
print("flask db upgrade")
print()
print("# Rollback migration:")
print("flask db downgrade")
print()
print("# Show current migration:")
print("flask db current")
print()
print("# Show migration history:")
print("flask db history")
print()

# Workflow
print("=" * 50)
print("TYPICAL WORKFLOW")
print("=" * 50)
print(
    """
1. Sửa model (ví dụ: thêm column trong models/user.py)

   class User(BaseModel):
       # ... existing fields ...
       phone = db.Column(db.String(20), nullable=True)  # New field

2. Tạo migration:
   flask db migrate -m "Add phone field to users"

3. Review migration file trong migrations/versions/
   - Check xem auto-generated code có đúng không
   - Chỉnh sửa nếu cần

4. Apply migration:
   flask db upgrade

5. Test với database mới

6. Commit code + migration file vào git:
   git add migrations/versions/xxx_add_phone_field.py
   git commit -m "Add phone field to users"
"""
)

print("=" * 50)
print("IMPORTANT NOTES")
print("=" * 50)
print(
    """
⚠️  Luôn review migration file trước khi apply
⚠️  Backup database trước khi chạy migration trên production
⚠️  Test migration trên dev/staging environment trước
⚠️  Commit migration files vào git
⚠️  Đừng sửa migration files đã được apply
✅  Sử dụng descriptive messages cho migrations
✅  Tạo rollback plan trước khi deploy
"""
)

print()
print("🎉 Ready to setup migrations!")
print()
print("Run these commands:")
print("1. pip install -r requirements.txt")
print("2. Add Migrate to app_factory.py (see above)")
print("3. flask db init")
print('4. flask db migrate -m "Initial migration"')
print("5. flask db upgrade")
