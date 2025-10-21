# 📚 POSTGRESQL COMMANDS - Tra Cứu Nhanh

> **Mục đích:** Danh sách lệnh PostgreSQL thường dùng
> **Đối tượng:** Người mới bắt đầu

---

## 🎯 **LỆNH CƠ BẢN**

### **Kết nối vào PostgreSQL:**

```bash
# Kết nối với database mặc định
psql postgres

# Kết nối với database cụ thể
psql -U username -d database_name

# Ví dụ:
psql -U flask_user -d flask_dev

# Kết nối từ xa
psql -h hostname -U username -d database_name
```

---

## 💾 **DATABASE COMMANDS**

### **Trong Terminal:**

```bash
# Tạo database
createdb database_name

# Xóa database
dropdb database_name

# Ví dụ:
createdb flask_dev
dropdb flask_dev
```

### **Trong psql shell:**

```sql
-- Xem tất cả databases
\l
\list

-- Tạo database
CREATE DATABASE database_name;

-- Xóa database
DROP DATABASE database_name;

-- Kết nối vào database
\c database_name
\connect database_name

-- Xem database hiện tại
SELECT current_database();

-- Xem kích thước database
SELECT pg_size_pretty(pg_database_size('database_name'));

-- Ví dụ:
CREATE DATABASE flask_dev;
\c flask_dev
SELECT pg_size_pretty(pg_database_size('flask_dev'));
```

---

## 👤 **USER COMMANDS**

```sql
-- Tạo user
CREATE USER username WITH PASSWORD 'password';

-- Tạo user với nhiều quyền
CREATE USER username WITH PASSWORD 'password' CREATEDB;

-- Đổi password
ALTER USER username WITH PASSWORD 'new_password';

-- Xóa user
DROP USER username;

-- Xem tất cả users
\du
\du+  -- Chi tiết hơn

-- Grant quyền
GRANT ALL PRIVILEGES ON DATABASE database_name TO username;
GRANT ALL ON SCHEMA public TO username;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO username;

-- Revoke quyền
REVOKE ALL PRIVILEGES ON DATABASE database_name FROM username;

-- Ví dụ:
CREATE USER flask_user WITH PASSWORD 'flask_password_123';
GRANT ALL PRIVILEGES ON DATABASE flask_dev TO flask_user;
\c flask_dev
GRANT ALL ON SCHEMA public TO flask_user;
```

---

## 📋 **TABLE COMMANDS**

```sql
-- Xem tất cả tables
\dt
\dt+  -- Chi tiết hơn

-- Xem cấu trúc table
\d table_name
\d+ table_name  -- Chi tiết hơn

-- Tạo table
CREATE TABLE table_name (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Xóa table
DROP TABLE table_name;

-- Rename table
ALTER TABLE old_name RENAME TO new_name;

-- Thêm column
ALTER TABLE table_name ADD COLUMN column_name VARCHAR(50);

-- Xóa column
ALTER TABLE table_name DROP COLUMN column_name;

-- Xem kích thước table
SELECT pg_size_pretty(pg_total_relation_size('table_name'));

-- Ví dụ:
\dt
\d users
SELECT pg_size_pretty(pg_total_relation_size('users'));
```

---

## 🔍 **QUERY DATA**

```sql
-- Xem tất cả data
SELECT * FROM table_name;

-- Xem 10 rows đầu
SELECT * FROM table_name LIMIT 10;

-- Xem với điều kiện
SELECT * FROM table_name WHERE column_name = 'value';

-- Đếm số rows
SELECT COUNT(*) FROM table_name;

-- Sort
SELECT * FROM table_name ORDER BY column_name DESC;

-- Group by
SELECT column_name, COUNT(*) FROM table_name GROUP BY column_name;

-- Ví dụ:
SELECT * FROM users;
SELECT * FROM users LIMIT 5;
SELECT * FROM users WHERE email = 'test@example.com';
SELECT COUNT(*) FROM users;
SELECT username, email FROM users ORDER BY id DESC;
```

---

## ✏️ **MODIFY DATA**

```sql
-- Insert
INSERT INTO table_name (column1, column2) VALUES ('value1', 'value2');

-- Update
UPDATE table_name SET column_name = 'new_value' WHERE id = 1;

-- Delete
DELETE FROM table_name WHERE id = 1;

-- Delete all (NGUY HIỂM!)
DELETE FROM table_name;

-- Truncate (xóa nhanh hơn)
TRUNCATE TABLE table_name;

-- Ví dụ:
INSERT INTO users (username, email) VALUES ('john', 'john@example.com');
UPDATE users SET email = 'newemail@example.com' WHERE id = 1;
DELETE FROM users WHERE id = 1;
```

---

## 🔗 **INDEX & CONSTRAINTS**

```sql
-- Tạo index
CREATE INDEX index_name ON table_name (column_name);

-- Xem indexes
\di

-- Xóa index
DROP INDEX index_name;

-- Thêm primary key
ALTER TABLE table_name ADD PRIMARY KEY (column_name);

-- Thêm foreign key
ALTER TABLE table_name
ADD CONSTRAINT fk_name
FOREIGN KEY (column_name)
REFERENCES other_table(id);

-- Thêm unique constraint
ALTER TABLE table_name ADD CONSTRAINT unique_name UNIQUE (column_name);

-- Ví dụ:
CREATE INDEX idx_users_email ON users (email);
\di
```

---

## 📊 **INFORMATION COMMANDS**

```sql
-- Xem version PostgreSQL
SELECT version();

-- Xem current user
SELECT current_user;

-- Xem current database
SELECT current_database();

-- Xem tất cả schemas
\dn

-- Xem tất cả functions
\df

-- Xem tất cả views
\dv

-- Xem running queries
SELECT * FROM pg_stat_activity;

-- Kill query
SELECT pg_terminate_backend(pid);

-- Xem database size
SELECT
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;

-- Xem table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 💾 **BACKUP & RESTORE**

### **Backup:**

```bash
# Backup 1 database
pg_dump -U username database_name > backup.sql

# Backup with custom format (nén)
pg_dump -U username -Fc database_name > backup.dump

# Backup chỉ schema (không có data)
pg_dump -U username -s database_name > schema.sql

# Backup chỉ data (không có schema)
pg_dump -U username -a database_name > data.sql

# Ví dụ:
pg_dump -U flask_user flask_dev > flask_dev_backup.sql
pg_dump -U flask_user -Fc flask_dev > flask_dev_backup.dump
```

### **Restore:**

```bash
# Restore từ .sql file
psql -U username database_name < backup.sql

# Restore từ .dump file
pg_restore -U username -d database_name backup.dump

# Restore và drop existing objects
pg_restore -U username -d database_name -c backup.dump

# Ví dụ:
psql -U flask_user flask_dev < flask_dev_backup.sql
pg_restore -U flask_user -d flask_dev flask_dev_backup.dump
```

---

## 🛠️ **PSQL META-COMMANDS**

```sql
-- Help
\?        -- Xem tất cả commands
\h        -- SQL help
\h SELECT -- Help cho SELECT

-- Navigation
\l        -- List databases
\c dbname -- Connect to database
\dt       -- List tables
\d table  -- Describe table
\du       -- List users
\dn       -- List schemas
\df       -- List functions
\dv       -- List views
\di       -- List indexes

-- Output
\x        -- Toggle expanded output
\x auto   -- Auto expanded output

-- Timing
\timing   -- Toggle query timing

-- Edit
\e        -- Open editor
\ef       -- Edit function

-- File operations
\i file.sql      -- Execute SQL from file
\o output.txt    -- Write output to file
\o               -- Stop writing to file

-- Quit
\q        -- Quit psql

-- Ví dụ:
\?
\timing
SELECT * FROM users;
\x
SELECT * FROM users;
\q
```

---

## 🎨 **FORMATTING OUTPUT**

```sql
-- Toggle expanded display
\x

-- Before:
 id | username | email
----+----------+-------
  1 | john     | j@e.c

-- After (\x):
-[ RECORD 1 ]
id       | 1
username | john
email    | j@e.c

-- Format options
\pset format aligned
\pset format unaligned
\pset format wrapped
\pset format html
\pset format csv

-- Borders
\pset border 0
\pset border 1
\pset border 2

-- Show null values
\pset null '(NULL)'

-- Ví dụ:
\x auto
\pset null '(null)'
\pset border 2
SELECT * FROM users;
```

---

## 📈 **PERFORMANCE QUERIES**

```sql
-- Xem slow queries
SELECT
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- Xem table statistics
SELECT
    schemaname,
    tablename,
    n_tup_ins AS inserts,
    n_tup_upd AS updates,
    n_tup_del AS deletes
FROM pg_stat_user_tables;

-- Xem index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes;

-- Xem cache hit ratio
SELECT
    sum(heap_blks_read) AS heap_read,
    sum(heap_blks_hit) AS heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS ratio
FROM pg_statio_user_tables;
```

---

## 🚨 **TROUBLESHOOTING**

```sql
-- Xem connections
SELECT * FROM pg_stat_activity;

-- Kill connections to database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'database_name'
  AND pid <> pg_backend_pid();

-- Vacuum (clean up)
VACUUM;
VACUUM FULL;
VACUUM ANALYZE;

-- Reindex
REINDEX TABLE table_name;
REINDEX DATABASE database_name;

-- Check table bloat
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 📝 **TRANSACTIONS**

```sql
-- Start transaction
BEGIN;

-- Do some work
INSERT INTO users (username, email) VALUES ('test', 'test@example.com');
UPDATE users SET email = 'new@example.com' WHERE username = 'test';

-- Commit (save changes)
COMMIT;

-- Rollback (undo changes)
ROLLBACK;

-- Ví dụ:
BEGIN;
DELETE FROM users WHERE id = 999;
SELECT * FROM users WHERE id = 999; -- Check
ROLLBACK; -- Undo delete
SELECT * FROM users WHERE id = 999; -- Still there!
```

---

## 🔐 **SECURITY**

```sql
-- Đổi password
ALTER USER username WITH PASSWORD 'new_password';

-- Grant specific permissions
GRANT SELECT ON table_name TO username;
GRANT INSERT, UPDATE ON table_name TO username;

-- Revoke permissions
REVOKE ALL ON table_name FROM username;

-- Xem permissions
\dp table_name
\z table_name

-- Create read-only user
CREATE USER readonly WITH PASSWORD 'password';
GRANT CONNECT ON DATABASE database_name TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

---

## 📚 **DATA TYPES**

### **Numeric:**
```sql
SMALLINT          -- -32768 to 32767
INTEGER           -- -2147483648 to 2147483647
BIGINT            -- Very large numbers
SERIAL            -- Auto-increment integer
DECIMAL(p,s)      -- Exact decimal
NUMERIC(p,s)      -- Same as DECIMAL
REAL              -- Float
DOUBLE PRECISION  -- Double float
```

### **Text:**
```sql
CHAR(n)           -- Fixed length
VARCHAR(n)        -- Variable length
TEXT              -- Unlimited length
```

### **Date/Time:**
```sql
DATE              -- Date only
TIME              -- Time only
TIMESTAMP         -- Date + Time
TIMESTAMPTZ       -- Timestamp with timezone
INTERVAL          -- Time interval
```

### **Boolean:**
```sql
BOOLEAN           -- TRUE/FALSE
```

### **Other:**
```sql
JSON              -- JSON data
JSONB             -- Binary JSON (faster)
ARRAY             -- Array
UUID              -- Unique identifier
```

---

## 🎯 **COMMON PATTERNS**

### **Auto-increment ID:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL
);
```

### **Timestamps:**
```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **Foreign Key:**
```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200)
);
```

### **Unique Constraint:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL
);
```

---

## 🆘 **QUICK REFERENCE**

| Task | Command |
|------|---------|
| Connect | `psql -U user -d dbname` |
| List databases | `\l` |
| Switch database | `\c dbname` |
| List tables | `\dt` |
| Describe table | `\d tablename` |
| List users | `\du` |
| Run SQL file | `\i file.sql` |
| Quit | `\q` |
| Help | `\?` |
| SQL help | `\h SELECT` |

---

## 💡 **TIPS**

1. **Auto-complete:** Press `Tab` trong psql
2. **History:** Press `↑` để xem lệnh cũ
3. **Multi-line:** Lệnh chưa có `;` thì chưa execute
4. **Cancel:** `Ctrl+C` để cancel query đang chạy
5. **Clear screen:** `Ctrl+L` hoặc `\! clear`

---

## 📖 **Ví Dụ Workflow**

```bash
# 1. Connect
psql -U flask_user -d flask_dev

# 2. Explore
\dt                    # Xem tables
\d users              # Xem cấu trúc users table

# 3. Query
SELECT * FROM users LIMIT 5;
SELECT COUNT(*) FROM posts;

# 4. Modify
INSERT INTO users (username, email) VALUES ('newuser', 'new@example.com');
UPDATE users SET email = 'updated@example.com' WHERE id = 1;

# 5. Check
SELECT * FROM users WHERE id = 1;

# 6. Exit
\q
```

---

**Lưu file này để tra cứu nhanh! 📚✨**
