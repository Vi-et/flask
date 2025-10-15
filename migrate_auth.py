"""
Database Migration Script for Authentication
Add authentication fields to existing User table
"""
from config.database import db
from models.user import User
from app_factory import create_app
from sqlalchemy import text

def migrate_user_table():
    """Add authentication fields to User table"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starting database migration for authentication...")
            
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            
            migrations = []
            
            # Add password_hash column
            if 'password_hash' not in existing_columns:
                migrations.append("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")
                print("   ➕ Adding password_hash column")
            
            # Add is_active column
            if 'is_active' not in existing_columns:
                migrations.append("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
                print("   ➕ Adding is_active column")
            
            # Add is_admin column
            if 'is_admin' not in existing_columns:
                migrations.append("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
                print("   ➕ Adding is_admin column")
            
            # Add last_login column
            if 'last_login' not in existing_columns:
                migrations.append("ALTER TABLE users ADD COLUMN last_login DATETIME")
                print("   ➕ Adding last_login column")
            
            # Execute migrations
            if migrations:
                for migration in migrations:
                    db.session.execute(text(migration))
                
                db.session.commit()
                print("✅ Database migration completed successfully!")
                
                # Update existing users with default password
                update_existing_users()
                
            else:
                print("ℹ️  All authentication columns already exist")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise

def update_existing_users():
    """Update existing users with default authentication values"""
    try:
        print("🔄 Updating existing users...")
        
        # Get users without password_hash
        users_without_password = User.query.filter_by(password_hash=None).all()
        
        if users_without_password:
            print(f"   🔧 Found {len(users_without_password)} users without passwords")
            
            for user in users_without_password:
                # Set default password (users should change this)
                user.set_password('defaultpassword123')
                user.is_active = True
                user.is_admin = False
                
                print(f"   👤 Updated user: {user.email}")
            
            db.session.commit()
            print("✅ Existing users updated with default authentication values")
            print("⚠️  IMPORTANT: Users should change their passwords from 'defaultpassword123'")
        else:
            print("ℹ️  All users already have authentication data")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to update existing users: {str(e)}")
        raise

def create_admin_user():
    """Create default admin user"""
    try:
        print("🔄 Creating default admin user...")
        
        admin_email = "admin@example.com"
        existing_admin = User.get_by_email(admin_email)
        
        if not existing_admin:
            admin_user = User(
                name="Administrator",
                email=admin_email,
                is_admin=True,
                is_active=True
            )
            admin_user.set_password("admin123456")  # Change this!
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"✅ Admin user created: {admin_email}")
            print("⚠️  IMPORTANT: Change admin password from 'admin123456'")
        else:
            print("ℹ️  Admin user already exists")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to create admin user: {str(e)}")

def run_migration():
    """Run the complete migration"""
    print("🚀 Starting Authentication Migration")
    print("=" * 50)
    
    migrate_user_table()
    create_admin_user()
    
    print("=" * 50)
    print("🎉 Authentication migration completed!")
    print("\n📋 Next Steps:")
    print("1. Update existing user passwords")
    print("2. Change admin password from default")
    print("3. Test authentication endpoints")

if __name__ == "__main__":
    run_migration()