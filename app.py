"""
Main Application Entry Point - Refactored Version
"""
import os

from dotenv import load_dotenv

from app_factory import create_app

# Load environment variables from .env file
load_dotenv()


# Create app using factory pattern
app = create_app()


# Chỉ chạy server khi file được chạy trực tiếp
if __name__ == "__main__":
    print("� Đang khởi động Flask server ...")
    print("🌐 Server đang chạy tại: http://127.0.0.1:8888")
    print("📊 Database file: blog.db")
    print("📁 Cấu trúc: Modular architecture với Blueprints")

    # Set environment if not set
    if not os.environ.get("FLASK_ENV"):
        os.environ["FLASK_ENV"] = "development"

    app.run(debug=app.config.get("DEBUG", True), host="127.0.0.1", port=8888)
else:
    print("Flask app được import như một module")
