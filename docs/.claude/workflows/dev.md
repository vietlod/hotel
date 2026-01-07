# Local Development Workflow for Windows

## Setup (One-time)

### 1. Clone Repository
\`\`\`bash
git clone https://github.com/vietlod/ecodata.git
cd ecodata
\`\`\`

### 2. Python Virtual Environment
\`\`\`bash
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
\`\`\`

### 3. PostgreSQL Setup
\`\`\`bash
docker run -d \\
  --name ecodata-postgres \\
  -e POSTGRES_USER=ecodata_user \\
  -e POSTGRES_PASSWORD=password \\
  -e POSTGRES_DB=ecodata \\
  -p 5432:5432 \\
  postgres:16
\`\`\`

### 4. Database Initialization
\`\`\`bash
alembic upgrade head
\`\`\`

### 5. Environment File (.env)
\`\`\`
DATABASE_URL=postgresql://ecodata_user:password@localhost:5432/ecodata
API_KEY_WORLDBANK=[your-key]
API_KEY_OECD=[your-key]
API_KEY_COMTRADE=[your-key]
FASTAPI_ENV=development
SECRET_KEY=dev-secret-key
\`\`\`

## Daily Development

### 1. Start Services
\`\`\`bash
# Activate virtual environment
.\\venv\\Scripts\\Activate.ps1

# Start backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
\`\`\`

### 2. Make Changes
- Modify code in your IDE
- Hot reload happens automatically
- Check terminal for errors

### 3. Test Changes
\`\`\`bash
pytest tests/                    # Unit tests
pytest tests/integration/ -v     # Integration tests
pytest tests/e2e/                # E2E tests
\`\`\`

## Before Pushing to dev

### Verification Checklist
\`\`\`bash
pytest tests/                    # Unit tests
pytest tests/integration/        # Integration tests
alembic upgrade head             # Check migrations
black . --check                  # Code formatting
mypy . --ignore-missing-imports  # Type checking
\`\`\`

---

*Workflow for Windows local development*