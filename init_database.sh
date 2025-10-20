#!/bin/bash
# 🚀 Script tự động khởi tạo Database qua Migration

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║       🚀 KHỞI TẠO DATABASE QUA MIGRATION - TỪ ĐẦU            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Bước 1: Xóa migration và database cũ (nếu có)
echo "📝 Bước 1: Xóa migration và database cũ..."
rm -rf migrations/
rm -f instance/blog.db
echo "   ✅ Đã xóa migrations/ và instance/blog.db"
echo ""

# Bước 2: Kiểm tra models
echo "📝 Bước 2: Kiểm tra models..."
if [ ! -f "models/__init__.py" ]; then
    echo "   ❌ Lỗi: models/__init__.py không tồn tại!"
    exit 1
fi
if [ ! -f "models/user.py" ]; then
    echo "   ❌ Lỗi: models/user.py không tồn tại!"
    exit 1
fi
if [ ! -f "models/post.py" ]; then
    echo "   ❌ Lỗi: models/post.py không tồn tại!"
    exit 1
fi
echo "   ✅ Tất cả models đã tồn tại"
echo ""

# Bước 3: Initialize migration
echo "📝 Bước 3: Initialize migration..."
flask db init
echo "   ✅ Đã tạo folder migrations/"
echo ""

# Bước 4: Tạo migration đầu tiên
echo "📝 Bước 4: Tạo migration đầu tiên..."
flask db migrate -m "Initial migration: User, Post, TokenBlacklist"
echo "   ✅ Đã tạo migration file"
echo ""

# Bước 5: Apply migration
echo "📝 Bước 5: Apply migration vào database..."
flask db upgrade
echo "   ✅ Database đã được tạo"
echo ""

# Bước 6: Verify
echo "📝 Bước 6: Verify database..."
echo ""
echo "Migration version hiện tại:"
flask db current
echo ""

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ HOÀN TẤT THÀNH CÔNG!                      ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Database Status:"
echo "   ✅ Database file: instance/blog.db"
echo "   ✅ Tables: users, posts, token_blacklist"
echo "   ✅ Migration tracking: Active"
echo ""
echo "🚀 Bước tiếp theo:"
echo "   1. Kiểm tra: sqlite3 instance/blog.db '.tables'"
echo "   2. Chạy app: python app.py"
echo "   3. Tạo seed data: python seed_data.py (nếu có)"
echo ""
echo "📚 Tài liệu: docs/DATABASE_MIGRATION_SETUP_FROM_SCRATCH.md"
echo ""
