---
name: ECODATA Python Expert
description: |
  Specialized in ECODATA's Python backend architecture including FastAPI,
  SQLAlchemy ORM, Pydantic validation, and async patterns. Handles API 
  development, data pipelines, ETL workflows, and database operations.
version: 1.0.0
dependencies: python>=3.10, fastapi>=0.104, sqlalchemy>=2.0, pydantic>=2.0, pytest>=7.0

---

# ECODATA Python Expert

## When to Use

- Implementing FastAPI endpoints and routes
- Creating SQLAlchemy models and database operations
- Developing ETL pipelines and data transformers
- Fixing Python type hints and validation issues
- Writing pytest unit and integration tests
- Optimizing database queries and performance

## Key Patterns for ECODATA

### FastAPI Routes
- Async route handlers with dependency injection
- Pydantic request/response validation
- JWT/OAuth2 authentication
- Error handling with HTTPException
- Automatic OpenAPI documentation

### SQLAlchemy ORM
- Model definition with relationships
- Async session management
- Query optimization with joins and eager loading
- Migration handling with Alembic
- Index and constraint definitions

### Data Pipelines
- CSV/Excel import with pandas
- Data cleaning and transformation
- Validation before database storage
- Error logging and recovery
- Batch processing with async

### Testing
- Unit tests for services and utilities
- Integration tests for API endpoints
- Fixture-based test data
- Coverage reports (target 90%+)
- E2E tests with real database

## ECODATA-Specific Type Definitions

```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class IndicatorSchema(BaseModel):
    id: str
    code: str
    name: str
    source: str
    country: str
    value: float
    year: int
    created_at: datetime

    class Config:
        from_attributes = True

class DataImportRequest(BaseModel):
    source: str
    country: Optional[str] = None
    file_path: str
    data_format: str  # "csv", "excel", "json"

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    count: int = 0
```

---

*Specialized skill for ECODATA Python development*