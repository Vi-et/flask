# 🐳 Docker Setup - Quick Reference

## ✅ **Current Status: RUNNING**

All containers are healthy and operational!

```
✅ flask-app    - http://localhost:8888 (healthy)
✅ flask-db     - localhost:5432 (PostgreSQL)
✅ flask-redis  - localhost:6380 (Redis)
```

---

## 🚀 **Quick Commands**

### **Start containers:**
```bash
docker-compose up -d
```

### **Stop containers:**
```bash
docker-compose down
```

### **View logs:**
```bash
# All containers
docker-compose logs -f

# Specific container
docker-compose logs -f flask-app
docker-compose logs -f flask-db
docker-compose logs -f flask-redis
```

### **Rebuild after code changes:**
```bash
docker-compose down
docker-compose up -d --build
```

### **Check status:**
```bash
docker-compose ps
```

### **Execute commands in container:**
```bash
# Flask shell
docker-compose exec flask-app flask shell

# Database migrations
docker-compose exec flask-app flask db upgrade

# List routes
docker-compose exec flask-app flask routes

# Python shell
docker-compose exec flask-app python
```

---

## 🔍 **Test Endpoints**

```bash
# Health check
curl http://localhost:8888/health

# API versions
curl http://localhost:8888/api/versions

# Register user
curl -X POST http://localhost:8888/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!"
  }'

# Login
curl -X POST http://localhost:8888/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!"
  }'
```

---

## 🗄️ **Database Access**

### **Connect to PostgreSQL:**
```bash
# Using docker-compose
docker-compose exec db psql -U postgres -d flaskdb

# Using local psql
psql -h localhost -p 5432 -U postgres -d flaskdb
# Password: password
```

### **Common SQL commands:**
```sql
-- List tables
\dt

-- Describe table
\d users

-- Query
SELECT * FROM users;

-- Exit
\q
```

---

## 📦 **Redis Access**

### **Connect to Redis:**
```bash
# Using docker-compose
docker-compose exec redis redis-cli

# Using local redis-cli
redis-cli -h localhost -p 6380
```

### **Common Redis commands:**
```redis
# List all keys
KEYS *

# Get value
GET key_name

# Delete key
DEL key_name

# Flush all
FLUSHALL

# Exit
exit
```

---

## 🔧 **Configuration**

### **Environment Variables** (`.env`):
```bash
# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database (internal Docker network)
DATABASE_URL=postgresql://postgres:password@db:5432/flaskdb

# Redis (internal Docker network)
REDIS_URL=redis://redis:6379/0
```

### **Port Mappings:**
```
Host    → Container
8888    → 5000     (Flask app)
5432    → 5432     (PostgreSQL)
6380    → 6379     (Redis) ← Changed to avoid conflict
```

---

## 🐛 **Troubleshooting**

### **Port already in use:**
```bash
# Find process using port
lsof -i :6379
lsof -i :5432
lsof -i :8888

# Change port in docker-compose.yml
ports:
  - "6380:6379"  # Map to different host port
```

### **Container won't start:**
```bash
# Check logs
docker-compose logs flask-app

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### **Database connection error:**
```bash
# Check if database is ready
docker-compose exec db pg_isready -U postgres

# Check database logs
docker-compose logs db
```

### **Code changes not reflected:**
```bash
# Option 1: Rebuild
docker-compose down
docker-compose up -d --build

# Option 2: Use volume mount (for development)
# Add to docker-compose.yml:
volumes:
  - .:/app
```

---

## 📊 **Health Checks**

All containers have health checks configured:

```bash
# Check health status
docker-compose ps

# Inspect health
docker inspect flask-app | grep -A 10 Health
```

**Health check intervals:**
- Flask app: Every 30s
- PostgreSQL: Every 10s
- Redis: Every 10s

---

## 🔄 **Development vs Production**

### **Development** (current setup):
- Uses SQLite locally or PostgreSQL in Docker
- Debug mode ON
- Hot reload (if using volume mount)
- Exposed ports for debugging

### **Production** (recommended changes):
1. Use secrets management (not `.env` file)
2. Enable SSL/TLS
3. Use nginx reverse proxy
4. Implement proper logging
5. Use orchestration (Kubernetes/Docker Swarm)
6. Regular backups
7. Monitoring (Prometheus/Grafana)

---

## 📝 **Next Steps**

### **1. Enable Development Mode:**
```yaml
# docker-compose.yml
services:
  flask-app:
    volumes:
      - .:/app  # Mount code for hot reload
    environment:
      - FLASK_ENV=development
```

### **2. Add Nginx:**
Uncomment nginx service in `docker-compose.yml` and create:
```bash
mkdir -p nginx
# Create nginx/nginx.conf
```

### **3. Setup CI/CD:**
```bash
# Already created in .github/workflows/
git add .
git commit -m "Setup Docker"
git push
# → Triggers CI/CD pipeline
```

---

## 🎯 **Current Issues Fixed:**

✅ **Port 6379 conflict** → Changed to 6380
✅ **Missing gunicorn** → Added to requirements.txt
✅ **Missing psycopg2** → Added psycopg2-binary
✅ **Missing /health endpoint** → Added to app.py
✅ **Nginx config missing** → Commented out (optional)

---

## 🌟 **What's Running:**

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Flask App   │  │  PostgreSQL  │  │    Redis     │  │
│  │  :5000       │  │  :5432       │  │    :6379     │  │
│  │  (gunicorn)  │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                 │                  │          │
└─────────┼─────────────────┼──────────────────┼──────────┘
          │                 │                  │
     :8888 │            :5432 │            :6380 │
          ↓                 ↓                  ↓
    [localhost:8888]  [localhost:5432]  [localhost:6380]
```

---

## 🎉 **Success Indicators:**

```bash
$ docker-compose ps
NAME          STATUS
flask-app     Up (healthy) ✅
flask-db      Up (healthy) ✅
flask-redis   Up (healthy) ✅

$ curl http://localhost:8888/health
{"message":"Flask app is running","status":"healthy"} ✅

$ curl http://localhost:8888/api/versions
{"latest":"v1","recommended":"v1",...} ✅
```

---

**Docker setup hoàn tất! 🚀**

For CI/CD deployment, see: `docs/CI_CD_GUIDE.md`
