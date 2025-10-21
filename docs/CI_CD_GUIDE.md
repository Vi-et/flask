# 🚀 CI/CD Setup Guide

Complete CI/CD pipeline for Flask application using GitHub Actions.

## 📋 Table of Contents
- [Overview](#overview)
- [Workflows](#workflows)
- [Setup Instructions](#setup-instructions)
- [GitHub Secrets](#github-secrets)
- [Deployment Environments](#deployment-environments)
- [Docker Setup](#docker-setup)
- [Monitoring](#monitoring)

---

## 🎯 Overview

### **CI/CD Pipeline Features:**
- ✅ **Continuous Integration (CI)**
  - Code linting (Flake8, Black, isort)
  - Security scanning (Safety, Bandit)
  - Unit testing (Pytest) across Python 3.9, 3.10, 3.11
  - Code coverage reporting (Codecov)
  - Dependency review
  - CodeQL analysis
  - Docker build

- 🚀 **Continuous Deployment (CD)**
  - Automatic staging deployment on `master` push
  - Production deployment on tags (`v*.*.*`)
  - Manual deployment trigger
  - Database migrations
  - Health checks
  - Rollback support
  - Slack notifications

- 🐳 **Docker**
  - Multi-platform builds (amd64, arm64)
  - GitHub Container Registry
  - Docker Hub
  - Vulnerability scanning (Trivy)

---

## 📁 Workflows

### **1. CI Workflow** (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `master` or `develop`
- Pull requests to `master` or `develop`

**Jobs:**
1. **🔍 Lint & Code Quality**
   - Flake8 (code style)
   - Black (formatting)
   - isort (import sorting)

2. **🔒 Security Scan**
   - Safety (dependency vulnerabilities)
   - Bandit (security issues)

3. **🧪 Testing**
   - Run tests with pytest
   - Generate coverage reports
   - Upload to Codecov

4. **🏗️ Build**
   - Build Docker image
   - Push to registries (master only)

5. **📦 Dependency Review**
   - Review dependency changes (PRs only)

6. **🔬 CodeQL Analysis**
   - Static code analysis

---

### **2. CD Workflow** (`.github/workflows/cd.yml`)

**Triggers:**
- Push to `master` → Staging
- Tags `v*.*.*` → Production
- Manual dispatch

**Jobs:**
1. **🚀 Deploy to Staging**
   - Install dependencies
   - Run migrations
   - Deploy via SSH
   - Health check
   - Slack notification

2. **🏭 Deploy to Production**
   - Backup database
   - Run migrations
   - Deploy via SSH
   - Health check
   - Create GitHub release
   - Slack notification

3. **⏮️ Rollback**
   - Manual trigger only
   - Revert to previous version
   - Rollback migrations

---

### **3. Docker Workflow** (`.github/workflows/docker.yml`)

**Triggers:**
- Push to `master` or `develop`
- Tags `v*.*.*`
- Pull requests

**Features:**
- Multi-platform builds (AMD64, ARM64)
- Push to GitHub Container Registry
- Push to Docker Hub
- Trivy vulnerability scanning
- Upload security results

---

### **4. Cleanup Workflow** (`.github/workflows/cleanup.yml`)

**Triggers:**
- Weekly (Sunday 2 AM UTC)
- Manual dispatch

**Actions:**
- Delete artifacts older than 30 days
- Keep 5 most recent artifacts
- Delete old Docker images

---

## ⚙️ Setup Instructions

### **Step 1: Initial Setup**

1. **Fork/Clone repository:**
   ```bash
   git clone https://github.com/Vi-et/flask.git
   cd flask
   ```

2. **Create required directories:**
   ```bash
   mkdir -p logs nginx/ssl instance
   ```

3. **Copy environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

---

### **Step 2: GitHub Secrets**

Go to **Settings → Secrets and variables → Actions → New repository secret**

#### **Required Secrets:**

**Docker Hub:**
```
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-token
```

**Staging Environment:**
```
STAGING_HOST=staging.your-domain.com
STAGING_USERNAME=deploy-user
STAGING_SSH_KEY=<your-private-ssh-key>
STAGING_DATABASE_URL=postgresql://user:pass@host:5432/db
STAGING_SECRET_KEY=<random-secret-key>
```

**Production Environment:**
```
PRODUCTION_HOST=your-domain.com
PRODUCTION_USERNAME=deploy-user
PRODUCTION_SSH_KEY=<your-private-ssh-key>
PRODUCTION_DATABASE_URL=postgresql://user:pass@host:5432/db
PRODUCTION_SECRET_KEY=<random-secret-key>
```

**Notifications:**
```
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Optional:**
```
CODECOV_TOKEN=your-codecov-token
```

---

### **Step 3: Generate SSH Keys**

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github-actions

# Copy public key to server
ssh-copy-id -i ~/.ssh/github-actions.pub user@your-server.com

# Copy private key content
cat ~/.ssh/github-actions
# → Paste into GitHub Secret (STAGING_SSH_KEY / PRODUCTION_SSH_KEY)
```

---

### **Step 4: Server Setup**

**On your staging/production server:**

```bash
# Create application directory
sudo mkdir -p /var/www/flask-app
sudo chown $USER:$USER /var/www/flask-app
cd /var/www/flask-app

# Clone repository
git clone https://github.com/Vi-et/flask.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
flask db upgrade

# Create systemd service
sudo nano /etc/systemd/system/flask-app.service
```

**`/etc/systemd/system/flask-app.service`:**
```ini
[Unit]
Description=Flask Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/flask-app
Environment="PATH=/var/www/flask-app/venv/bin"
EnvironmentFile=/var/www/flask-app/.env
ExecStart=/var/www/flask-app/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable flask-app
sudo systemctl start flask-app
sudo systemctl status flask-app
```

---

### **Step 5: Environment Configuration**

**GitHub → Settings → Environments**

Create two environments:
1. **staging**
   - Protection rules: None
   - Secrets: STAGING_*

2. **production**
   - Protection rules:
     - ✅ Required reviewers (1-2 people)
     - ✅ Wait timer (5 minutes)
   - Secrets: PRODUCTION_*

---

## 🐳 Docker Setup

### **Local Development:**

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f flask-app

# Run migrations
docker-compose exec flask-app flask db upgrade

# Stop
docker-compose down
```

### **Production Docker:**

```bash
# Build image
docker build -t flask-app:latest .

# Run container
docker run -d \
  -p 5000:5000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=... \
  --name flask-app \
  flask-app:latest

# Check health
curl http://localhost:5000/health
```

---

## 📊 Monitoring

### **CI/CD Status Badges**

Add to `README.md`:
```markdown
![CI](https://github.com/Vi-et/flask/workflows/CI/badge.svg)
![CD](https://github.com/Vi-et/flask/workflows/CD/badge.svg)
![Docker](https://github.com/Vi-et/flask/workflows/Docker/badge.svg)
[![codecov](https://codecov.io/gh/Vi-et/flask/branch/master/graph/badge.svg)](https://codecov.io/gh/Vi-et/flask)
```

### **Slack Notifications**

Configure webhook in `#deployments` channel:
- ✅ Successful deployments
- ❌ Failed deployments
- ⏮️ Rollbacks

---

## 🚦 Deployment Workflow

### **Development → Staging:**
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes
# ...

# 3. Commit and push
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# 4. Create PR to master
# GitHub → Pull Requests → New PR

# 5. CI runs automatically
# ✅ Lint, test, security scan

# 6. Merge PR
# Auto-deploy to staging
```

### **Staging → Production:**
```bash
# 1. Create version tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 2. CD workflow triggers
# - Deploy to staging
# - Wait for approval
# - Deploy to production
# - Create GitHub release
```

### **Manual Deployment:**
```bash
# Go to Actions → CD → Run workflow
# Select environment: staging or production
```

### **Rollback:**
```bash
# Go to Actions → CD → Run workflow → Rollback
# Requires manual approval
```

---

## 🔧 Customization

### **Add New Environment:**

1. Create workflow environment:
   ```yaml
   deploy-dev:
     environment:
       name: development
       url: https://dev.your-app.com
   ```

2. Add secrets:
   - `DEV_HOST`
   - `DEV_SSH_KEY`
   - `DEV_DATABASE_URL`

### **Add Tests:**

```python
# tests/test_api.py
def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
```

### **Custom Deployment Script:**

```yaml
- name: Deploy
  run: |
    chmod +x scripts/deploy.sh
    ./scripts/deploy.sh ${{ secrets.SERVER }}
```

---

## 🆘 Troubleshooting

### **CI Failures:**

**Lint errors:**
```bash
# Run locally
black .
isort .
flake8 .
```

**Test failures:**
```bash
pytest tests/ -v
```

### **CD Failures:**

**SSH connection failed:**
- Check SSH key in secrets
- Verify server firewall
- Test manual SSH: `ssh -i key.pem user@host`

**Migration failed:**
```bash
# On server
cd /var/www/flask-app
source venv/bin/activate
flask db upgrade
```

**Health check failed:**
```bash
# Check application logs
sudo journalctl -u flask-app -n 50

# Check if running
sudo systemctl status flask-app
```

---

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Flask Deployment](https://flask.palletsprojects.com/en/latest/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

## ✅ Checklist

Before going to production:

- [ ] All tests passing
- [ ] Security scan clean
- [ ] Secrets configured
- [ ] SSH access verified
- [ ] Database backup configured
- [ ] Monitoring setup (logs, metrics)
- [ ] Rollback tested
- [ ] Documentation updated
- [ ] Team trained on CI/CD process
- [ ] Slack notifications working

---

🎉 **Your CI/CD pipeline is ready!** Push to trigger workflows.
