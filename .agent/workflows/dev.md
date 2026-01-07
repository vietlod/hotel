---
description: Local development setup and daily workflow for Windows
---

# Local Development Workflow for Windows

## One-Time Setup

### 1. Clone Repository
```bash
git clone https://github.com/vietlod/hotel.git
cd hotel
```

### 2. Create Python Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### 3. Environment Configuration
```powershell
copy .env.example .env
# Edit .env with your local settings
```

Required `.env` values for development:
```ini
DATABASE_URL=sqlite:///./hotel_pms.db
ENV=development
API_PREFIX=/api/v1
API_VERSION=0.2.0
SECRET_KEY=dev-secret-key-change-in-production
```

### 4. Initialize Database
```powershell
cd backend
python init_db.py
# Creates tables and seeds sample data
```

---

## Daily Development

### 1. Start Development Server
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start backend with auto-reload
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### 2. Access Application
| Resource | URL |
|----------|-----|
| Frontend | Open `frontend/index.html` in browser or http://localhost:8003 |
| API Docs | http://localhost:8002/docs |
| ReDoc | http://localhost:8002/redoc |
| Health | http://localhost:8002/health |

### 3. Make Changes
- Modify code in your IDE (VSCode recommended)
- Backend auto-reloads on file changes
- Frontend: refresh browser to see changes
- Check terminal for errors

### 4. Test Changes
```powershell
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_bookings.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Common Development Tasks

### Add New API Endpoint
1. Define Pydantic schema in `schemas/__init__.py`
2. Create route in `api/[module].py`
3. Implement service logic in `services/`
4. Test with curl or Postman
5. Run tests: `pytest tests/`

### Modify Database Model
1. Update model in `models/__init__.py`
2. Create migration:
   ```powershell
   cd backend
   alembic revision --autogenerate -m "Add field to booking"
   ```
3. Review migration file in `alembic/versions/`
4. Apply migration:
   ```powershell
   alembic upgrade head
   ```
5. Verify with sample data

### Debug API Endpoint
```powershell
# Test endpoint with curl
curl http://localhost:8002/api/v1/crud/bookings

# With query parameters
curl "http://localhost:8002/api/v1/crud/bookings?status=confirmed"

# POST request
curl -X POST http://localhost:8002/api/v1/crud/bookings \
  -H "Content-Type: application/json" \
  -d '{"room_id": "xxx", "check_in": "2026-01-10"}'
```

---

## Before Pushing to Git

### Verification Checklist
```powershell
# Run all tests
pytest tests/ -v

# Check migrations
alembic upgrade head

# Optional: Type checking
mypy app/ --ignore-missing-imports

# Optional: Code formatting
black . --check
```

### Manual Checklist
```
□ All tests pass
□ No print() statements (use logger)
□ Type hints on public functions
□ Docstrings on endpoints
□ README.md updated (if adding feature)
□ CHANGELOG.md updated (if adding feature)
□ No hardcoded secrets
```

### Commit and Push
```powershell
git add .
git status  # Review changes
git commit -m "feat(scope): description"
git push origin dev
```

---

## Troubleshooting

### Virtual Environment Issues
```powershell
# Recreate virtual environment
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### Database Reset
```powershell
cd backend
Remove-Item hotel_pms.db
python init_db.py
```

### Port Already in Use
```powershell
# Find process on port 8002
netstat -ano | findstr :8002

# Kill process
Stop-Process -Id [PID]
```

### Module Not Found
```powershell
# Ensure virtual environment is active
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r backend/requirements.txt
```

---

*Workflow for Windows local development*
