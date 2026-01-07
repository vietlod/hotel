# VPS Deployment Workflow (Ubuntu)

## Deployment Steps

### 1. SSH to VPS
\`\`\`bash
ssh root@212.85.24.158
cd /opt/ecodata
\`\`\`

### 2. Pull Latest Code
\`\`\`bash
git checkout dev
git pull origin dev
\`\`\`

### 3. Install & Build
\`\`\`bash
pip install -r requirements.txt
alembic upgrade head
\`\`\`

### 4. Restart Application
\`\`\`bash
pm2 restart ecodata
pm2 logs ecodata
\`\`\`

### 5. Health Check
\`\`\`bash
curl https://ecodata.khoviet.com/health
\`\`\`

## If Deployment Fails

### Check Logs
\`\`\`bash
pm2 logs ecodata | tail -100
pm2 logs ecodata --err
\`\`\`

### Common Issues

**Database connection failed:**
\`\`\`bash
psql postgresql://ecodata_user@localhost/ecodata
alembic upgrade head
\`\`\`

**Port already in use:**
\`\`\`bash
lsof -i :8001
kill -9 [PID]
pm2 restart ecodata
\`\`\`

**Module not found:**
\`\`\`bash
pip install -r requirements.txt
pm2 restart ecodata
\`\`\`

### Rollback
\`\`\`bash
git reset --hard HEAD~1
pm2 restart ecodata
curl https://ecodata.khoviet.com/health
\`\`\`

---

*Workflow for Ubuntu VPS deployment*