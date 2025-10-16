#!/usr/bin/env python3
"""
Test Flask-Security setup and database creation
"""
from app_factory import create_app
from config.database import db


def main():
    print("🔧 Testing Flask-Security setup...")

    # Create app
    app = create_app()

    with app.app_context():
        print("✅ App created successfully")

        # Create all tables
        print("📦 Creating database tables...")
        db.create_all()

        # Check User table schema
        from sqlalchemy import inspect

        inspector = inspect(db.engine)

        # Verify tables were created
        tables = inspector.get_table_names()
        print(f"🗂️ Tables created: {tables}")

        if "users" in tables:
            user_columns = [col["name"] for col in inspector.get_columns("users")]
            print(f"👤 User table columns: {user_columns}")

            # Check if required Flask-Security fields exist
            required_fields = ["email", "password", "active", "fs_uniquifier"]
            missing_fields = [
                field for field in required_fields if field not in user_columns
            ]

            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
            else:
                print("✅ All required Flask-Security fields present!")
        else:
            print("❌ Users table not created")

        print("✅ Database setup completed successfully!")


if __name__ == "__main__":
    main()
