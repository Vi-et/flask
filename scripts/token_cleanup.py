"""
Token Cleanup Tasks
Scheduled tasks for token maintenance
"""
import time
from datetime import datetime

import schedule

from app_factory import create_app
from models.token_blacklist import TokenBlacklist


def cleanup_expired_tokens():
    """Remove expired tokens from blacklist"""

    app = create_app()

    with app.app_context():
        try:
            print(f"🧹 Starting token cleanup at {datetime.now()}")

            cleaned_count = TokenBlacklist.cleanup_expired_tokens()

            print(f"✅ Cleaned up {cleaned_count} expired tokens")

            return cleaned_count

        except Exception as e:
            print(f"❌ Token cleanup failed: {str(e)}")
            return 0


def schedule_cleanup_jobs():
    """Schedule periodic cleanup tasks"""

    # Clean up expired tokens every day at 2 AM
    schedule.every().day.at("02:00").do(cleanup_expired_tokens)

    # Clean up expired tokens every 6 hours
    schedule.every(6).hours.do(cleanup_expired_tokens)

    print("📅 Cleanup jobs scheduled:")
    print("  - Daily at 2:00 AM")
    print("  - Every 6 hours")


def run_cleanup_scheduler():
    """Run the cleanup scheduler"""

    schedule_cleanup_jobs()

    print("🚀 Token cleanup scheduler started...")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Run cleanup once
        print("🧹 Running one-time token cleanup...")
        cleaned = cleanup_expired_tokens()
        print(f"✅ Cleanup completed: {cleaned} tokens removed")
    else:
        # Run scheduler
        try:
            run_cleanup_scheduler()
        except KeyboardInterrupt:
            print("\n⏹️  Cleanup scheduler stopped")
