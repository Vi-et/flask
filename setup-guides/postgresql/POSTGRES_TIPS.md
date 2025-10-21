# 💡 POSTGRESQL TIPS & TRICKS

> **Mục đích:** Các mẹo hay, thủ thuật thực tế khi dùng PostgreSQL
> **Level:** Beginner → Intermediate

---

## 🎯 **PRODUCTIVITY TIPS**

### **1. Psql Configuration File**

Tạo file `~/.psqlrc` để tự động config mỗi khi mở psql:

```sql
-- ~/.psqlrc

-- Timing queries
\timing on

-- Null display
\pset null '(null)'

-- Borders
\pset border 2

-- Auto expanded for wide results
\x auto

-- Better prompts
\set PROMPT1 '%n@%/%R%# '

-- History
\set HISTSIZE 10000

-- Autocomplete (case-insensitive)
\set COMP_KEYWORD_CASE upper
```

**Kết quả:** Mỗi lần chạy `psql`, settings này tự động apply! ✨

---

### **2. Aliases trong psql**

```sql
-- Thêm vào ~/.psqlrc

-- Show table sizes
\set show_sizes 'SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||''.''||tablename)) AS size FROM pg_tables WHERE schemaname = ''public'' ORDER BY pg_total_relation_size(schemaname||''.''||tablename) DESC;'

-- Show active connections
\set show_connections 'SELECT datname, usename, COUNT(*) FROM pg_stat_activity GROUP BY datname, usename;'

-- Show slow queries
\set show_slow 'SELECT pid, now() - query_start AS duration, query FROM pg_stat_activity WHERE state = ''active'' AND now() - query_start > interval ''1 second'' ORDER BY duration DESC;'
```

**Sử dụng:**
```sql
:show_sizes
:show_connections
:show_slow
```

---

### **3. Better History**

```bash
# Trong ~/.zshrc hoặc ~/.bashrc

# PostgreSQL history per database
export PSQL_HISTORY="~/.psql_history_$(date +%Y%m)"

# Unlimited history
export HISTSIZE=10000
export SAVEHIST=10000
```

---

## 🚀 **PERFORMANCE TIPS**

### **1. EXPLAIN Query Plans**

```sql
-- Xem query plan
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- Xem detailed plan + actual execution
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Xem costs
EXPLAIN (COSTS TRUE, BUFFERS TRUE) SELECT * FROM users;
```

**Đọc kết quả:**
```
Seq Scan on users  (cost=0.00..15.50 rows=1 width=100)
  ↓           ↓        ↓         ↓      ↓       ↓
Method     Table   Start    Total  Rows   Width
                   Cost     Cost
```

- `Seq Scan` = Quét toàn bộ table (chậm)
- `Index Scan` = Dùng index (nhanh)
- `cost=0.00..15.50` = Chi phí ước tính
- `rows=1` = Số rows ước tính

**Tip:** Nếu thấy `Seq Scan`, thêm index!

---

### **2. Index Strategy**

```sql
-- ❌ BAD: Không có index
SELECT * FROM users WHERE email = 'test@example.com';
-- → Seq Scan (chậm)

-- ✅ GOOD: Thêm index
CREATE INDEX idx_users_email ON users(email);
-- → Index Scan (nhanh)

-- ✅ BETTER: Unique index (nếu email unique)
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Index cho multiple columns
CREATE INDEX idx_users_name_email ON users(username, email);

-- Partial index (chỉ index rows thỏa điều kiện)
CREATE INDEX idx_active_users ON users(email) WHERE is_active = TRUE;

-- Xem indexes
\di
```

**Khi nào cần index:**
- ✅ Columns trong `WHERE` clause
- ✅ Columns trong `JOIN` conditions
- ✅ Columns trong `ORDER BY`
- ✅ Foreign keys
- ❌ Columns ít được query
- ❌ Tables nhỏ (< 1000 rows)

---

### **3. Query Optimization**

```sql
-- ❌ BAD: SELECT *
SELECT * FROM users;

-- ✅ GOOD: Chỉ select columns cần thiết
SELECT id, username, email FROM users;

-- ❌ BAD: Không limit
SELECT * FROM posts ORDER BY created_at DESC;

-- ✅ GOOD: Có limit
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10;

-- ❌ BAD: Multiple queries
SELECT * FROM users WHERE id = 1;
SELECT * FROM posts WHERE user_id = 1;

-- ✅ GOOD: JOIN
SELECT u.*, p.*
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
WHERE u.id = 1;
```

---

### **4. Vacuum & Analyze**

```sql
-- Vacuum (clean up dead rows)
VACUUM users;
VACUUM;  -- All tables

-- Analyze (update statistics)
ANALYZE users;
ANALYZE;  -- All tables

-- Vacuum + Analyze
VACUUM ANALYZE;

-- Auto vacuum (tự động, recommended)
-- Đã bật mặc định trong PostgreSQL modern
```

**Khi nào chạy:**
- Sau khi DELETE nhiều rows
- Sau khi UPDATE nhiều rows
- Sau khi BULK INSERT
- Nếu queries chậm bất thường

---

## 🛡️ **SECURITY TIPS**

### **1. Principle of Least Privilege**

```sql
-- ❌ BAD: Full privileges
GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;

-- ✅ GOOD: Chỉ quyền cần thiết
GRANT CONNECT ON DATABASE mydb TO myuser;
GRANT SELECT, INSERT, UPDATE ON users TO myuser;
GRANT SELECT ON posts TO myuser;  -- Read-only

-- Read-only user
CREATE USER readonly WITH PASSWORD 'password';
GRANT CONNECT ON DATABASE mydb TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

---

### **2. Connection Security**

```sql
-- Force SSL connections
ALTER USER myuser SET ssl TO on;

-- Limit connections
ALTER USER myuser CONNECTION LIMIT 10;

-- Set statement timeout (prevent long-running queries)
ALTER USER myuser SET statement_timeout = '30s';
```

---

### **3. Password Policy**

```bash
# Strong passwords
CREATE USER myuser WITH PASSWORD 'aB3$xY9#mN2@pQ5';

# Change passwords regularly
ALTER USER myuser WITH PASSWORD 'new_strong_password';

# Disable user
ALTER USER myuser WITH NOLOGIN;

# Enable user
ALTER USER myuser WITH LOGIN;
```

---

## 📊 **DATA MANAGEMENT TIPS**

### **1. Bulk Insert**

```sql
-- ❌ BAD: Multiple INSERT
INSERT INTO users (username) VALUES ('user1');
INSERT INTO users (username) VALUES ('user2');
-- ... 1000 times

-- ✅ GOOD: Batch INSERT
INSERT INTO users (username) VALUES
('user1'),
('user2'),
('user3'),
-- ...
('user1000');

-- ✅ BETTER: COPY (fastest)
COPY users (username, email) FROM '/path/to/file.csv' WITH CSV HEADER;
```

**Speed comparison:**
- Single INSERTs: 100 rows/sec
- Batch INSERT: 1,000 rows/sec
- COPY: 10,000+ rows/sec

---

### **2. Update trong Transaction**

```sql
-- ❌ DANGEROUS: No transaction
UPDATE users SET is_active = FALSE WHERE last_login < '2024-01-01';

-- ✅ SAFE: With transaction
BEGIN;
UPDATE users SET is_active = FALSE WHERE last_login < '2024-01-01';
SELECT COUNT(*) FROM users WHERE is_active = FALSE;  -- Check
-- Nếu OK: COMMIT
-- Nếu sai: ROLLBACK
COMMIT;
```

---

### **3. Soft Delete**

```sql
-- ❌ BAD: Hard delete (mất data vĩnh viễn)
DELETE FROM users WHERE id = 1;

-- ✅ GOOD: Soft delete (giữ data)
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP;

UPDATE users SET deleted_at = NOW() WHERE id = 1;

-- Query (chỉ lấy users chưa xóa)
SELECT * FROM users WHERE deleted_at IS NULL;

-- Index cho performance
CREATE INDEX idx_users_deleted ON users(deleted_at);
```

---

## 🔍 **DEBUGGING TIPS**

### **1. Log Slow Queries**

```sql
-- Trong postgresql.conf
log_min_duration_statement = 1000  -- Log queries > 1s

-- Hoặc set per session
SET log_min_duration_statement = 1000;
```

---

### **2. Check Locks**

```sql
-- Xem locks
SELECT
    relation::regclass AS table,
    mode,
    granted
FROM pg_locks
WHERE relation IS NOT NULL;

-- Xem blocking queries
SELECT
    blocked_locks.pid AS blocked_pid,
    blocking_locks.pid AS blocking_pid,
    blocked_activity.query AS blocked_query,
    blocking_activity.query AS blocking_query
FROM pg_locks blocked_locks
JOIN pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

---

### **3. Monitor Connections**

```sql
-- Current connections
SELECT
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query
FROM pg_stat_activity
WHERE datname = 'flask_dev';

-- Count connections by database
SELECT
    datname,
    COUNT(*) as connections
FROM pg_stat_activity
GROUP BY datname
ORDER BY connections DESC;

-- Max connections
SHOW max_connections;

-- Current connections vs max
SELECT
    (SELECT COUNT(*) FROM pg_stat_activity) AS current,
    (SELECT setting::int FROM pg_settings WHERE name='max_connections') AS max;
```

---

## 💾 **BACKUP STRATEGIES**

### **1. Automated Daily Backup**

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgresql"
DB_NAME="flask_dev"

# Create backup
pg_dump -U postgres $DB_NAME > "$BACKUP_DIR/backup_$DATE.sql"

# Compress
gzip "$BACKUP_DIR/backup_$DATE.sql"

# Delete backups older than 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

**Cron job (chạy mỗi ngày 2am):**
```bash
0 2 * * * /path/to/backup.sh
```

---

### **2. Point-in-Time Recovery**

```bash
# Enable WAL archiving (trong postgresql.conf)
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archives/%f'

# Base backup
pg_basebackup -D /backups/base -Ft -z -P

# Restore to specific time
pg_restore --target-time='2024-10-21 14:30:00'
```

---

## 🎨 **DEVELOPMENT TIPS**

### **1. Multiple Environments**

```bash
# Development
export DATABASE_URL="postgresql://localhost/flask_dev"

# Staging
export DATABASE_URL="postgresql://localhost/flask_staging"

# Production
export DATABASE_URL="postgresql://server/flask_prod"

# Test
export DATABASE_URL="postgresql://localhost/flask_test"
```

**Quick switch:**
```bash
# .env.development
DATABASE_URL=postgresql://localhost/flask_dev

# .env.production
DATABASE_URL=postgresql://server/flask_prod

# Load
export $(cat .env.development | xargs)
```

---

### **2. Test Data Generation**

```sql
-- Generate test users
INSERT INTO users (username, email)
SELECT
    'user' || generate_series AS username,
    'user' || generate_series || '@example.com' AS email
FROM generate_series(1, 1000);

-- Generate random data
INSERT INTO posts (user_id, title, content)
SELECT
    (random() * 100)::int + 1,
    'Post ' || generate_series,
    md5(random()::text)
FROM generate_series(1, 10000);
```

---

### **3. Database Reset Script**

```bash
#!/bin/bash
# reset_db.sh

DB_NAME="flask_dev"
DB_USER="flask_user"

echo "⚠️  Dropping database..."
dropdb $DB_NAME

echo "✅ Creating database..."
createdb $DB_NAME

echo "🔐 Granting permissions..."
psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

echo "🚀 Running migrations..."
flask db upgrade

echo "📊 Seeding data..."
python seed.py

echo "✨ Database reset complete!"
```

---

## 📈 **MONITORING**

### **1. Key Metrics to Monitor**

```sql
-- Database size
SELECT
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname))
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Connection count
SELECT COUNT(*) FROM pg_stat_activity;

-- Cache hit ratio (should be > 99%)
SELECT
    sum(heap_blks_read) AS heap_read,
    sum(heap_blks_hit) AS heap_hit,
    round(sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100, 2) AS cache_hit_ratio
FROM pg_statio_user_tables;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY idx_tup_read DESC;
```

---

## 🎓 **BEST PRACTICES**

### **✅ DO:**

1. **Always use transactions for multiple operations**
   ```sql
   BEGIN;
   -- operations
   COMMIT;
   ```

2. **Add indexes on foreign keys**
   ```sql
   CREATE INDEX idx_posts_user_id ON posts(user_id);
   ```

3. **Use prepared statements (prevents SQL injection)**
   ```python
   # Python example
   cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
   ```

4. **Regular VACUUM ANALYZE**
   ```sql
   VACUUM ANALYZE;
   ```

5. **Monitor slow queries**
   ```sql
   SET log_min_duration_statement = 1000;
   ```

### **❌ DON'T:**

1. **SELECT * in production**
   ```sql
   -- ❌ SELECT * FROM users;
   -- ✅ SELECT id, username FROM users;
   ```

2. **Store passwords in plain text**
   ```sql
   -- ❌ password VARCHAR
   -- ✅ password_hash VARCHAR
   ```

3. **Hard delete important data**
   ```sql
   -- ❌ DELETE FROM users WHERE id = 1;
   -- ✅ UPDATE users SET deleted_at = NOW() WHERE id = 1;
   ```

4. **Grant ALL PRIVILEGES unnecessarily**
   ```sql
   -- ❌ GRANT ALL PRIVILEGES
   -- ✅ GRANT SELECT, INSERT, UPDATE
   ```

---

## 🔧 **USEFUL EXTENSIONS**

```sql
-- UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Crypto functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- List installed extensions
\dx
```

---

## 📚 **LEARNING RESOURCES**

1. **Official Docs:** https://www.postgresql.org/docs/
2. **Tutorial:** https://www.postgresqltutorial.com/
3. **Exercises:** https://pgexercises.com/
4. **Performance:** https://wiki.postgresql.org/wiki/Performance_Optimization

---

**Save these tips! Bạn sẽ dùng chúng THƯỜNG XUYÊN! 💪✨**
