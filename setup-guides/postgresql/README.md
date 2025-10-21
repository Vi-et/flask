# 🐘 PostgreSQL Setup - Hướng Dẫn Hoàn Chỉnh

> **Thư mục này chứa:** Mọi thứ bạn cần để setup PostgreSQL cho Flask app

---

## 📂 **CẤU TRÚC THƯ MỤC**

```
setup-guides/postgresql/
├── README.md                      ← BẠN ĐANG Ở ĐÂY
├── SETUP_POSTGRESQL_LOCAL.md      ← Setup PostgreSQL trên máy
├── POSTGRES_COMMANDS.md           ← Tra cứu commands
├── POSTGRES_TIPS.md               ← Tips & tricks
├── .env.local.example             ← Template config file
└── scripts/
    ├── setup_postgres.sh          ← Auto setup script
    ├── backup_db.sh               ← Backup database
    └── reset_db.sh                ← Reset database
```

---

## 🎯 **BẮT ĐẦU TỪ ĐÂY**

### **1️⃣ Bạn chưa bao giờ dùng PostgreSQL?**

👉 **Đọc:** `SETUP_POSTGRESQL_LOCAL.md`

**Nội dung:**
- PostgreSQL là gì? (Giải thích siêu đơn giản)
- Tại sao dùng PostgreSQL thay vì SQLite?
- Hướng dẫn cài đặt từng bước (macOS)
- Tạo database & user
- Kết nối Flask với PostgreSQL
- Troubleshooting

**Thời gian:** 15-20 phút
**Độ khó:** ⭐⭐ Trung bình

---

### **2️⃣ Bạn đã cài PostgreSQL, cần tra commands?**

👉 **Đọc:** `POSTGRES_COMMANDS.md`

**Nội dung:**
- Tất cả commands cơ bản
- Quản lý database, tables, users
- Query data
- Backup & restore
- Meta-commands (\dt, \l, \d...)

**Dùng khi:** Cần tra cứu nhanh syntax

---

### **3️⃣ Muốn học tips nâng cao?**

👉 **Đọc:** `POSTGRES_TIPS.md`

**Nội dung:**
- Productivity tips (psql config, aliases)
- Performance optimization
- Security best practices
- Backup strategies
- Monitoring

**Level:** Beginner → Intermediate

---

## 🚀 **QUICK START**

### **Option 1: Manual Setup (Recommended cho học tập)**

```bash
# 1. Cài PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# 2. Tạo database
psql postgres
CREATE USER flask_user WITH PASSWORD 'flask_password_123';
CREATE DATABASE flask_dev;
GRANT ALL PRIVILEGES ON DATABASE flask_dev TO flask_user;
\c flask_dev
GRANT ALL ON SCHEMA public TO flask_user;
\q

# 3. Configure Flask
cp .env.local.example .env.local
# Edit DATABASE_URL trong .env.local

# 4. Run migrations
export $(cat .env.local | xargs)
flask db upgrade

# 5. Start app
python app.py
```

---

### **Option 2: Auto Setup Script (Nhanh hơn)**

```bash
# Chạy script tự động
cd /Users/apple/Downloads/project/flask/setup-guides/postgresql
chmod +x scripts/setup_postgres.sh
./scripts/setup_postgres.sh

# Script sẽ:
# ✅ Check PostgreSQL đã cài chưa
# ✅ Tạo database & user
# ✅ Grant permissions
# ✅ Tạo .env.local
# ✅ Run migrations
# ✅ Test connection
```

---

## 📖 **LEARNING PATH**

### **Level 1: Beginner** 🌱

```
1. Đọc: SETUP_POSTGRESQL_LOCAL.md (sections 1-4)
2. Practice: Cài PostgreSQL, tạo database
3. Đọc: POSTGRES_COMMANDS.md (Basic commands)
4. Practice: Chạy các commands cơ bản
```

**Mục tiêu:**
- ✅ Hiểu PostgreSQL là gì
- ✅ Cài đặt thành công
- ✅ Kết nối Flask với PostgreSQL
- ✅ Biết commands cơ bản (\dt, \l, SELECT...)

---

### **Level 2: Intermediate** 🚀

```
1. Đọc: SETUP_POSTGRESQL_LOCAL.md (sections 5-7)
2. Đọc: POSTGRES_TIPS.md (Performance & Security)
3. Practice: Tạo indexes, optimize queries
4. Practice: Setup backup script
```

**Mục tiêu:**
- ✅ Test & troubleshoot
- ✅ Hiểu indexes
- ✅ Query optimization
- ✅ Backup/restore

---

### **Level 3: Advanced** 💪

```
1. Đọc: POSTGRES_TIPS.md (Monitoring)
2. Practice: Setup monitoring
3. Practice: Performance tuning
4. Deploy: Production setup
```

**Mục tiêu:**
- ✅ Monitor database
- ✅ Performance tuning
- ✅ Production-ready setup

---

## 🛠️ **SCRIPTS**

### **setup_postgres.sh**

```bash
# Auto setup PostgreSQL
./scripts/setup_postgres.sh

# Tùy chọn:
./scripts/setup_postgres.sh --db-name flask_dev --user flask_user
```

**Chức năng:**
- Check PostgreSQL installed
- Create database & user
- Grant permissions
- Create .env.local
- Run migrations
- Test connection

---

### **backup_db.sh**

```bash
# Backup database
./scripts/backup_db.sh

# Kết quả:
# backups/flask_dev_20241021_143000.sql.gz
```

**Chức năng:**
- Create timestamped backup
- Compress với gzip
- Delete old backups (> 7 days)

---

### **reset_db.sh**

```bash
# Reset database (DANGER!)
./scripts/reset_db.sh

# Hỏi xác nhận trước khi xóa
```

**Chức năng:**
- Drop database
- Recreate database
- Grant permissions
- Run migrations
- Seed test data (optional)

---

## 🔍 **TROUBLESHOOTING**

### **Lỗi: "psql: command not found"**

```bash
# Fix: Cài PostgreSQL
brew install postgresql@15

# Or add to PATH
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```

---

### **Lỗi: "could not connect to server"**

```bash
# Fix: Start PostgreSQL
brew services start postgresql@15

# Check status
brew services list | grep postgresql
```

---

### **Lỗi: "password authentication failed"**

```bash
# Fix: Reset password
psql postgres
ALTER USER flask_user WITH PASSWORD 'new_password';
\q

# Update .env.local
```

---

### **Lỗi: "database does not exist"**

```bash
# Fix: Create database
psql postgres
CREATE DATABASE flask_dev;
GRANT ALL PRIVILEGES ON DATABASE flask_dev TO flask_user;
\q
```

---

## 📊 **CHEAT SHEET**

### **Daily Commands:**

```bash
# Start PostgreSQL
brew services start postgresql@15

# Connect to database
psql -U flask_user -d flask_dev

# Run Flask with PostgreSQL
export $(cat .env.local | xargs)
python app.py

# Backup database
./scripts/backup_db.sh
```

---

### **Psql Commands:**

```sql
\l              -- List databases
\c dbname       -- Connect to database
\dt             -- List tables
\d tablename    -- Describe table
\du             -- List users
\q              -- Quit
```

---

### **SQL Commands:**

```sql
-- View data
SELECT * FROM users LIMIT 10;

-- Count rows
SELECT COUNT(*) FROM users;

-- Insert data
INSERT INTO users (username, email) VALUES ('test', 'test@example.com');

-- Update data
UPDATE users SET email = 'new@example.com' WHERE id = 1;

-- Delete data
DELETE FROM users WHERE id = 1;
```

---

## 📚 **TÀI LIỆU THAM KHẢO**

| File | Nội dung | Khi nào dùng |
|------|----------|--------------|
| `SETUP_POSTGRESQL_LOCAL.md` | Setup từ A-Z | Lần đầu setup |
| `POSTGRES_COMMANDS.md` | Tra cứu commands | Cần syntax |
| `POSTGRES_TIPS.md` | Tips & tricks | Tối ưu |
| `.env.local.example` | Config template | Setup mới |

---

## ✅ **CHECKLIST**

### **Setup:**
```
□ PostgreSQL đã cài
□ Service đang chạy
□ Database đã tạo
□ User đã tạo
□ Permissions đã grant
□ .env.local đã config
□ Migrations đã chạy
□ Flask app connect OK
```

### **Learning:**
```
□ Đã đọc SETUP_POSTGRESQL_LOCAL.md
□ Đã đọc POSTGRES_COMMANDS.md
□ Đã practice basic commands
□ Đã tạo được database
□ Đã insert/select data
□ Hiểu indexes
□ Biết backup/restore
```

---

## 🎯 **NEXT STEPS**

Sau khi setup PostgreSQL local:

1. **Testing:**
   - Test tất cả API endpoints
   - Verify data lưu vào PostgreSQL
   - Check performance

2. **Optimization:**
   - Add indexes
   - Optimize queries
   - Monitor performance

3. **Production:**
   - Setup PostgreSQL trên server
   - Configure connection pooling
   - Setup automated backups
   - Deploy app

4. **Learning:**
   - Đọc POSTGRES_TIPS.md
   - Practice advanced queries
   - Learn transactions
   - Explore extensions

---

## 🆘 **HỖ TRỢ**

### **Cần giúp đỡ?**

1. **Check Troubleshooting sections** trong mỗi file
2. **Run test script:**
   ```bash
   ./scripts/test_connection.sh
   ```
3. **View PostgreSQL logs:**
   ```bash
   tail -f /opt/homebrew/var/log/postgresql@15.log
   ```

---

## 💡 **TIPS**

1. **Bookmark file này** để tra cứu nhanh
2. **Practice daily** với PostgreSQL commands
3. **Read logs** khi có lỗi
4. **Backup regularly** (chạy backup_db.sh)
5. **Monitor performance** (xem POSTGRES_TIPS.md)

---

## 📈 **PROGRESS TRACKING**

```
Level 1 (Beginner):
✅ PostgreSQL installed
✅ Database created
✅ Flask connected
✅ Basic commands

Level 2 (Intermediate):
□ Indexes created
□ Queries optimized
□ Backup setup
□ Monitoring setup

Level 3 (Advanced):
□ Production deployed
□ Performance tuned
□ Advanced queries
□ Extensions used
```

---

**Happy PostgreSQL Learning! 🐘✨**

**Bắt đầu với:** `SETUP_POSTGRESQL_LOCAL.md`
