---
description: How to deploy Hotel PMS to VPS
---

# VPS Deployment Workflow (Ubuntu)

## Prerequisites

- SSH access to VPS
- Docker and Docker Compose installed
- Git configured
- Domain DNS configured (hotel.khoviet.com → VPS IP)

## Deployment Steps

### 1. SSH to VPS
```bash
ssh root@[VPS_IP]
cd /opt/hotel-pms
```

### 2. Pull Latest Code
```bash
git checkout dev
git pull origin dev
```

### 3. Build and Start Containers
```bash
# Rebuild with latest code
docker-compose -f docker-compose.production.yml up -d --build

# Or restart without rebuild
docker-compose -f docker-compose.production.yml restart
```

### 4. Apply Database Migrations (if any)
```bash
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head
```

### 5. Health Check
```bash
curl https://hotel.khoviet.com/health
# Expected: {"status":"healthy","version":"0.2.0",...}
```

### 6. Verify Services
```bash
# Check all containers running
docker-compose -f docker-compose.production.yml ps

# Check backend logs
docker-compose -f docker-compose.production.yml logs backend --tail=50
```

---

## If Deployment Fails

### Check Logs
```bash
# Backend application logs
docker-compose -f docker-compose.production.yml logs backend | tail -100

# Nginx logs
docker-compose -f docker-compose.production.yml logs frontend | tail -50

# All containers
docker-compose -f docker-compose.production.yml logs --tail=50
```

### Common Issues

**Database connection failed:**
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.production.yml ps postgres

# Test connection
docker-compose -f docker-compose.production.yml exec postgres psql -U hotel_user -d hotel_pms -c "SELECT 1;"

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

**Port already in use:**
```bash
# Check what's using ports
lsof -i :8002
lsof -i :8003

# Kill if needed
kill -9 [PID]

# Restart
docker-compose -f docker-compose.production.yml up -d
```

**Container won't start:**
```bash
# Check container logs for errors
docker-compose -f docker-compose.production.yml logs backend

# Force rebuild
docker-compose -f docker-compose.production.yml build --no-cache backend
docker-compose -f docker-compose.production.yml up -d
```

**SSL/Certificate issues:**
```bash
# Check Nginx config
nginx -t

# Renew certificates
certbot renew
systemctl reload nginx
```

---

## Rollback Procedure

### Quick Rollback (1 commit)
```bash
git reset --hard HEAD~1
docker-compose -f docker-compose.production.yml up -d --build
curl https://hotel.khoviet.com/health
```

### Rollback to Specific Commit
```bash
git log --oneline -10  # Find commit hash
git reset --hard [commit-hash]
docker-compose -f docker-compose.production.yml up -d --build
```

### Database Rollback (if migration fails)
```bash
docker-compose -f docker-compose.production.yml exec backend alembic downgrade -1
```

---

## Post-Deployment Checklist

```
□ Health check returns 200
□ Frontend loads at https://hotel.khoviet.com
□ Dashboard displays data
□ API docs accessible at /docs
□ No errors in container logs
□ Database migrations applied
□ All services running (docker-compose ps)
```

---

*Workflow for Ubuntu VPS deployment*
