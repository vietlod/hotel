# ECODATA Code Quality Standards

## Python Standards

- **Type Hints:** Full type annotations required
- **Docstrings:** Google-style docstrings for all public functions
- **Error Handling:** Custom exception classes
- **Logging:** Structured logging with context
- **Testing:** Pytest with >80% coverage target
- **Format:** Black formatter (line length 88)
- **Linting:** Flake8 or Ruff

## FastAPI Standards

- **Routes:** Clear HTTP method + path
- **Validation:** Pydantic models for request/response
- **Error Handling:** HTTPException with status codes
- **Documentation:** Docstrings for endpoint behavior
- **Authentication:** JWT or OAuth2 where needed
- **CORS:** Configure for frontend origin

## Database Standards

- **Migrations:** Alembic for all schema changes
- **Indexes:** Index frequently queried columns
- **Constraints:** Use database-level validation
- **Documentation:** Comment complex queries
- **Performance:** Avoid N+1 queries

## Testing Standards

- **Unit Tests:** Mock external dependencies
- **Integration Tests:** Use test database
- **Coverage:** Target 80%+ code coverage
- **Fixtures:** Reusable test data
- **Assertions:** Clear failure messages

## React Standards (Frontend)

- **TypeScript:** Strict mode always enabled
- **Components:** Functional components only
- **Hooks:** Custom hooks for shared logic
- **Styling:** Tailwind CSS with scoped styles
- **Testing:** Playwright for E2E tests