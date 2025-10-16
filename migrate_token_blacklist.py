"""
Token Blacklist Migration
Create token_blacklist table for JWT token management
"""
from datetime import datetime

from config.database import db
from models.token_blacklist import TokenBlacklist


def migrate_token_blacklist():
    """Create token_blacklist table and indexes"""

    print("🔧 Creating token_blacklist table...")

    try:
        # Create the table
        db.create_all()

        print("✅ token_blacklist table created successfully!")

        # Create additional indexes for performance
        print("🔧 Creating database indexes...")

        # Use text() for raw SQL execution in newer SQLAlchemy
        from sqlalchemy import text

        # Index on user_id and token_type
        db.session.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_token_blacklist_user_type
            ON token_blacklist(user_id, token_type);
        """
            )
        )

        # Index on expires_at for cleanup
        db.session.execute(
            text(
                """
            CREATE INDEX IF NOT EXISTS idx_token_blacklist_expires
            ON token_blacklist(expires_at);
        """
            )
        )

        db.session.commit()

        print("✅ Database indexes created successfully!")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False


def rollback_token_blacklist():
    """Drop token_blacklist table"""

    print("🗑️  Rolling back token_blacklist migration...")

    try:
        # Drop the table
        TokenBlacklist.__table__.drop(db.engine, checkfirst=True)

        print("✅ token_blacklist table dropped successfully!")
        return True

    except Exception as e:
        print(f"❌ Rollback failed: {str(e)}")
        return False


if __name__ == "__main__":
    from app_factory import create_app

    # Create app context
    app = create_app()

    with app.app_context():
        print("🚀 Starting Token Blacklist Migration...")

        if migrate_token_blacklist():
            print("🎉 Token Blacklist Migration completed successfully!")
            print("\n📋 Next steps:")
            print("1. Restart your Flask application")
            print("2. Test logout functionality: POST /api/auth/logout")
            print("3. Check token info: GET /api/tokens/info")
            print("4. Monitor blacklisted tokens: GET /api/tokens/blacklist")
        else:
            print("💥 Migration failed! Check the error messages above.")
