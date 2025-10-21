# 📦 Deployment - CI/CD & Docker

> **Thư mục này chứa TẤT CẢ file liên quan đến CI/CD và Docker**

---

## 📁 **Cấu trúc thư mục**

```
deployment/
├── README.md                              ← File này (Index)
├── YOU_ARE_HERE.md                       ← 🎯 BẠN Ở ĐÂY - Sẵn sàng deploy!
├── DEPLOY_CHECKLIST.md                   ← ⚡ Quick checklist (5 phút)
├── DEPLOY_GUIDE.md                       ← 📖 Full deploy guide (3 platforms)
├── README_EXPLAINED_FOR_BEGINNERS.md     ← 📖 Giải thích CHI TIẾT cho người mới
├── PACKAGES_EXPLAINED.md                 ← 📦 Gunicorn & Psycopg2
├── START_HERE.md                         ← 🗺️ Hướng dẫn đọc
├── SUMMARY.md                            ← 📝 Tóm tắt toàn bộ
│
├── docker/                                ← 🐳 Docker configuration
│   ├── Dockerfile                        ← Build Docker image
│   ├── docker-compose.yml                ← Multi-container setup
│   └── .dockerignore                     ← Files không copy vào image
│
└── github-actions/                        ← 🤖 CI/CD workflows
    ├── ci.yml                            ← Continuous Integration
    ├── cd.yml                            ← Continuous Deployment
    ├── docker.yml                        ← Docker build & push
    └── cleanup.yml                       ← Cleanup old artifacts
```

---

## 🎯 **Mục đích**

### **1. Docker** (Thư mục `docker/`)
- **Dockerfile**: Hướng dẫn build Docker image
- **docker-compose.yml**: Chạy Flask + PostgreSQL + Redis cùng lúc
- **`.dockerignore`**: Tối ưu Docker build (không copy file thừa)

### **2. GitHub Actions** (Thư mục `github-actions/`)
- **ci.yml**: Tự động test mỗi khi push code
- **cd.yml**: Tự động deploy lên staging/production
- **docker.yml**: Build và push Docker image
- **cleanup.yml**: Dọn dẹp artifacts cũ hàng tuần

---

## 📚 **Đọc gì trước?**

### **🔰 Người mới bắt đầu (không biết code):**
```
1. README_EXPLAINED_FOR_BEGINNERS.md  ← BẮT ĐẦU TỪ ĐÂY!
   - Giải thích mọi thứ bằng ngôn ngữ đơn giản
   - Có hình ảnh, ví dụ thực tế
   - Giải thích Gunicorn, Psycopg2, Docker...
```

### **💻 Developer có kinh nghiệm:**
```
1. docker/README.md                   ← Docker quick reference
2. ../../docs/CI_CD_GUIDE.md         ← CI/CD setup guide
3. ../../docs/DOCKER_QUICK_REFERENCE.md
```

---

## 🚀 **Quick Start**

### **Chạy Docker local:**
```bash
cd deployment/docker
docker-compose up -d
```

### **Test endpoints:**
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
```

### **Xem logs:**
```bash
docker-compose logs -f flask-app
```

### **Stop containers:**
```bash
docker-compose down
```

---

## 🔑 **Key Files**

### **1. Dockerfile**
```dockerfile
# Multi-stage build cho optimization
FROM python:3.11-slim as builder
# ... build dependencies ...

FROM python:3.11-slim
# ... runtime image ...
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

**Tại sao?**
- ✅ Image size nhỏ (multi-stage)
- ✅ Security (non-root user)
- ✅ Production-ready (gunicorn)

### **2. docker-compose.yml**
```yaml
services:
  flask-app:   # Flask application
  db:          # PostgreSQL database
  redis:       # Redis cache
```

**Tại sao?**
- ✅ Chạy nhiều services cùng lúc
- ✅ Networking tự động
- ✅ Health checks

### **3. ci.yml (GitHub Actions)**
```yaml
on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  lint:    # Code quality
  test:    # Run tests
  build:   # Build Docker
```

**Tại sao?**
- ✅ Tự động test mỗi khi push
- ✅ Phát hiện bug sớm
- ✅ Code quality đảm bảo

### **4. cd.yml (Continuous Deployment)**
```yaml
jobs:
  deploy-staging:     # Auto deploy to staging
  deploy-production:  # Deploy to production (manual approval)
```

**Tại sao?**
- ✅ Tự động deploy
- ✅ Giảm human error
- ✅ Nhanh chóng

---

## 📦 **Packages đã thêm**

### **1. Gunicorn** (`gunicorn==21.2.0`)

**Là gì?**
- Production WSGI server cho Flask

**Tại sao cần?**
- Flask dev server: Chậm, không an toàn, 1 request/lần
- Gunicorn: Nhanh, an toàn, nhiều workers

**Trong Dockerfile:**
```dockerfile
CMD ["gunicorn", "--workers", "4", "app:app"]
#                 ↑ 4 workers = 4 requests cùng lúc
```

---

### **2. Psycopg2-binary** (`psycopg2-binary==2.9.9`)

**Là gì?**
- PostgreSQL adapter cho Python

**Tại sao cần?**
- SQLAlchemy cần driver để nói chuyện với PostgreSQL
- Không có = không connect được database

**Luồng:**
```
Flask → SQLAlchemy → Psycopg2 → PostgreSQL
```

---

## 🎓 **Học thêm**

### **Tài liệu chi tiết:**
```
deployment/
├── README_EXPLAINED_FOR_BEGINNERS.md    ← Giải thích mọi thứ
│
../../docs/
├── CI_CD_GUIDE.md                       ← Setup CI/CD từ A-Z
├── DOCKER_QUICK_REFERENCE.md            ← Docker commands
└── SWAGGER_COMPARISON.md                ← API docs
```

### **Online resources:**
- [Docker Tutorial](https://docs.docker.com/get-started/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Gunicorn Docs](https://docs.gunicorn.org/)
- [Psycopg2 Docs](https://www.psycopg.org/)

---

## ✅ **Checklist**

### **Development:**
- [x] Docker Compose setup
- [x] Health check endpoint
- [x] Multi-container networking
- [x] Volume persistence

### **CI/CD:**
- [x] Lint workflow
- [x] Test workflow
- [x] Security scan
- [x] Docker build & push
- [x] Deploy staging
- [x] Deploy production
- [ ] Setup GitHub Secrets (cần làm manual)

### **Documentation:**
- [x] Beginner-friendly guide
- [x] Docker quick reference
- [x] CI/CD guide
- [x] Swagger documentation

---

## 🆘 **Troubleshooting**

### **Port conflict:**
```bash
# Error: port already allocated
# Fix: Đổi port trong docker-compose.yml
ports:
  - "6380:6379"  # Thay vì 6379:6379
```

### **Image không update:**
```bash
# Fix: Rebuild
docker-compose down
docker-compose up -d --build
```

### **Health check fail:**
```bash
# Check logs
docker-compose logs flask-app

# Test manually
curl http://localhost:8888/health
```

---

## 🎯 **Next Steps**

1. **Đọc file giải thích:**
   ```bash
   cat README_EXPLAINED_FOR_BEGINNERS.md
   ```

2. **Test Docker local:**
   ```bash
   cd docker
   docker-compose up -d
   curl http://localhost:8888/health
   ```

3. **Setup CI/CD:**
   ```bash
   # Copy workflows to .github/
   cp -r github-actions/* ../.github/workflows/

   # Setup GitHub Secrets
   # (xem CI_CD_GUIDE.md)
   ```

4. **Push và deploy:**
   ```bash
   git add .
   git commit -m "Setup CI/CD & Docker"
   git push origin master
   # → CI/CD tự động chạy!
   ```

---

## 📞 **Support**

**Câu hỏi?**
- 📖 Đọc: `README_EXPLAINED_FOR_BEGINNERS.md`
- 📚 Xem: `../../docs/CI_CD_GUIDE.md`
- 🐛 Issues: GitHub Issues

---

**Happy Deploying! 🚀**
