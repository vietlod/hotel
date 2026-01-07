# dep

**Specialized in:** Preparing code for deployment, handling releases, and rollbacks

**This command will be available in chat with /dep**

---

## Usage
```
/dep ready for production
```

## Status: Deployment Ready ✅

---

## Pre-Flight Checklist (Local)

### Code Quality (5 min)
```bash
# Run all type checks
python -m mypy backend --strict
tsc --noEmit

# Run linter
pylint backend
npm run lint

# Check for hardcoded secrets
grep -r "password\|key\|token" backend/*.py | grep -v "# env"
```

### Test Suite (10 min)
```bash
# Backend tests
pytest --cov=services --cov=routers --cov-fail-under=90

# Frontend tests
npm run test -- --coverage --watchAll=false
```

### Build Verification (5 min)
```bash
# Backend
python -m pytest  # One final run

# Frontend
npm run build

# Check bundle size
ls -lh dist/
```

**✅ All checks passing? Continue to Phase 1**

---

## Phase 1: Local Pre-Flight (10 min)

### Checklist
- [ ] `pytest` passing with >90% coverage
- [ ] `npm run test` passing in frontend
- [ ] `npm run build` succeeds (zero errors)
- [ ] `tsc --noEmit` returns zero errors
- [ ] No `console.error` in browser
- [ ] No secrets in git diff
- [ ] CHANGELOG.md updated
- [ ] Type hints on all functions

### Verification
```bash
# Run pre-flight script
./scripts/pre-flight-check.sh

# Output should be:
# ✓ Type checking passed
# ✓ Tests passed (coverage: 92%)
# ✓ Build successful (bundle: 1.15MB)
# ✓ No secrets detected
# ✓ Ready for deployment
```

---

## Phase 2: Commit & Push (5 min)

### Git Workflow
```bash
# Ensure clean working directory
git status

# Stage all changes
git add -A

# Commit with conventional format
git commit -m "feat(export): add parquet format support"
# or
git commit -m "fix(api): handle null values in indicator query"

# Verify commit message format
git log --oneline -1
# Expected: feat(scope): description or fix(scope): description

# Push to dev branch
git push origin dev
```

### Commit Message Format
```
type(scope): description

[optional body with more details]

[optional footer with issue reference]
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`

---

## Phase 3: GitHub Actions & Review

### Automated Checks
GitHub Actions will run:
1. Python type checking (`mypy`)
2. Backend test suite (`pytest`)
3. Frontend test suite (`npm test`)
4. Build verification
5. Security scanning

### Review Checklist
- [ ] All checks ✅ passing
- [ ] Code review approved
- [ ] No conflicts with main
- [ ] CHANGELOG.md present
- [ ] Tests passing >90%

**✅ All checks pass? Continue to Phase 4**

---

## Phase 4: VPS Deployment (15 min)

### SSH into VPS
```bash
ssh root@ecodata.khoviet.com
cd /app/ecodata
```

### Deployment Steps

**Step 1: Pull Latest Code**
```bash
git fetch origin
git checkout dev
git pull origin dev
```

**Step 2: Install Dependencies**
```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend && npm ci && cd ..
```

**Step 3: Database Migration (if needed)**
```bash
alembic upgrade head
# Or if using manual migrations
python backend/scripts/run_migrations.py
```

**Step 4: Build Frontend**
```bash
cd frontend && npm run build && cd ..
```

**Step 5: Restart Services**
```bash
docker-compose down
docker-compose -f docker-compose.production.yml up -d

# Verify containers
docker ps
# All 3 containers should show: Up (healthy)
```

---

## Phase 5: Verification & Monitoring (10 min)

### Health Check
```bash
# Test main domain
curl -I https://ecodata.khoviet.com
# Expected: HTTP/1.1 200 OK

# Test API
curl https://ecodata.khoviet.com/api/docs
# Expected: OpenAPI documentation loads

# Test health endpoint
curl https://ecodata.khoviet.com/api/health
# Expected: {"status": "healthy"}
```

### Browser Testing
1. Open https://ecodata.khoviet.com
2. Test main features:
   - [ ] Dashboard loads
   - [ ] Can filter by source
   - [ ] Can export to CSV
   - [ ] API docs work
3. Check browser console for errors
4. Check performance (Network tab)

### Log Monitoring
```bash
# Backend logs
docker logs -f ecodata_backend

# Frontend logs (if any errors)
docker logs ecodata_frontend

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## Phase 6: Rollback (if needed)

### If Deployment Failed

**Quick Rollback:**
```bash
git checkout main
docker-compose down
docker-compose -f docker-compose.production.yml up -d
```

**Detailed Rollback:**
```bash
# 1. Stop current deployment
docker-compose down

# 2. Revert database changes
alembic downgrade -1

# 3. Switch to stable version
git checkout main
git pull origin main

# 4. Rebuild and restart
docker-compose -f docker-compose.production.yml up -d
```

**Post-Rollback:**
1. Verify site is back online
2. Check health endpoints
3. Document what failed in incident report
4. Don't retry until root cause fixed

---

## Deployment Decision Tree

```
Is deployment ready?
├─ Yes: Continue to Phase 1
└─ No:
   ├─ Tests failing? Fix tests, commit, push
   ├─ Build errors? Fix code, commit, push
   ├─ Type errors? Add type hints, commit, push
   └─ Secrets detected? Remove, re-test, push new commit

All pre-flight checks pass?
├─ Yes: Commit → GitHub Actions → VPS Deploy
└─ No: Fix issues locally, re-run checks

Deployment successful?
├─ Yes: 🎉 Production live
└─ No: Rollback (Phase 6) → Investigate

Errors in production?
├─ Minor: Monitor and create bug fix PR
├─ Major: Immediate rollback
└─ Security: Rollback + notify team
```

---

## Typical Deployment Time

| Phase | Time | Action |
|-------|------|--------|
| Pre-Flight | 5 min | Run local checks |
| Code Review | 10-30 min | GitHub checks + review |
| Deployment | 5-10 min | Pull code, rebuild, restart |
| Verification | 5 min | Health checks + testing |
| **Total** | **25-55 min** | Typically 30-40 min |

---

## Quick Checklist Before Deploying

```
Pre-Flight (Local):
□ pytest passing (>90%)
□ npm test passing
□ npm run build succeeds
□ No console errors

Code:
□ Committed with conventional message
□ Pushed to dev branch
□ CHANGELOG.md updated

GitHub:
□ All checks passing ✅
□ Code review approved

VPS:
□ SSH access working
□ git pull succeeds
□ Database up to date
□ Services restarted

Verification:
□ https://ecodata.khoviet.com loads
□ /api/health returns 200
□ /api/docs accessible
□ Browser console clean
```

---

*Last Updated: December 31, 2025*
*Project: ECODATA v2.7.2*
*Deployment: ecodata.khoviet.com*
*Status: Production Ready*
