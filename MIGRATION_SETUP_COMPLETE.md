# ✅ Database Migration Setup Complete!

## 📦 Đã Setup

### **1. Flask-Migrate đã được cấu hình**
- ✅ Thêm `Flask-Migrate==4.0.5` vào `requirements.txt`
- ✅ Import và khởi tạo trong `app_factory.py`
- ✅ Folder `migrations/` đã được tạo

### **2. Migration đầu tiên đã được tạo**
```
migrations/versions/be04e7e1dcef_initial_migration_with_user_post_and_.py
```

Migration này sẽ:
- Xóa các bảng cũ không dùng: `contacts`, `roles`, `user_roles`
- Cập nhật bảng `users`: loại bỏ các cột Flask-Security không dùng
- Giữ nguyên bảng `posts` và `token_blacklist`

---

## 🚀 Bước Tiếp Theo

### **Apply migration vào database:**
```bash
flask db upgrade
```

Sau khi chạy lệnh này:
- Database sẽ được cleanup
- Chỉ giữ lại: `users`, `posts`, `token_blacklist`
- Migration tracking được kích hoạt

---

## 📚 Tài Liệu Đã Tạo

1. **`docs/DATABASE_MIGRATION.md`** - Hướng dẫn chi tiết về migration
   - Khái niệm migration
   - Workflow đầy đủ
   - Use cases thực tế
   - Best practices
   - Troubleshooting

2. **`docs/MIGRATION_QUICK_START.md`** - Quick reference
   - Setup nhanh
   - Các lệnh thường dùng
   - Ví dụ thực hành
   - Troubleshooting nhanh

---

## 🎯 Workflow Migration Sau Này

### **Khi thêm/sửa Model:**

```bash
# 1. Sửa code trong models/
# Ví dụ: Thêm field phone vào User

# 2. Tạo migration
flask db migrate -m "Add phone to User"

# 3. Review migration file
cat migrations/versions/<latest>_*.py

# 4. Apply migration
flask db upgrade

# 5. Commit vào Git
git add migrations/
git commit -m "Migration: add phone field"
```

### **Các lệnh hữu ích:**

```bash
# Xem version hiện tại
flask db current

# Xem lịch sử
flask db history

# Rollback 1 version
flask db downgrade

# Rollback về đầu
flask db downgrade base

# Xem SQL sẽ chạy
flask db upgrade --sql
```

---

## 🔧 Ví Dụ Thực Hành

### **Thêm field `phone` vào User:**

**1. Sửa model:**
```python
# models/user.py
class User(BaseModel):
    # ... existing fields ...
    phone = db.Column(db.String(20), nullable=True)
```

**2. Tạo migration:**
```bash
flask db migrate -m "Add phone to User"
```

**3. Xem migration được tạo:**
```bash
cat migrations/versions/<revision>_add_phone_to_user.py
```

**4. Apply:**
```bash
flask db upgrade
```

**5. Kiểm tra:**
```bash
flask db current
# Output: abc123 (head), Add phone to User
```

---

## ⚠️ Lưu Ý Quan Trọng

1. **Luôn review migration trước khi upgrade**
   ```bash
   cat migrations/versions/<latest>_*.py
   ```

2. **Backup database trước khi migrate production**
   ```bash
   cp instance/app.db instance/app.db.backup
   ```

3. **Commit migration files vào Git**
   ```bash
   git add migrations/
   git commit -m "Migration: <description>"
   ```

4. **Không sửa migration đã apply**
   - Tạo migration mới để fix
   - Hoặc rollback rồi sửa

5. **Test migration trên staging trước production**

---

## 🎓 Tìm Hiểu Thêm

- **Chi tiết:** `docs/DATABASE_MIGRATION.md`
- **Quick ref:** `docs/MIGRATION_QUICK_START.md`
- **Flask-Migrate:** https://flask-migrate.readthedocs.io/
- **Alembic:** https://alembic.sqlalchemy.org/

---

## ✨ Kết Luận

Setup migration đã hoàn tất! Giờ bạn có thể:
- ✅ Quản lý thay đổi database một cách chuyên nghiệp
- ✅ Rollback nếu cần
- ✅ Đồng bộ schema giữa các môi trường
- ✅ Làm việc team dễ dàng hơn

**Next step:** Chạy `flask db upgrade` để apply migration đầu tiên!
