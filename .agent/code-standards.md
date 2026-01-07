# Hotel PMS Code Quality Standards

## Python Standards

- **Type Hints:** Full type annotations required for all functions
- **Docstrings:** Google-style docstrings for all public functions
- **Error Handling:** Custom exception classes with specific error types
- **Logging:** Structured logging with context (use `logger`, not `print`)
- **Testing:** Pytest with >80% coverage target
- **Format:** PEP 8 compliant (use Black formatter)
- **Linting:** Flake8 or Ruff for code quality

## FastAPI Standards

- **Routes:** Clear HTTP method + path with response models
- **Validation:** Pydantic models for all request/response bodies
- **Error Handling:** HTTPException with appropriate status codes
- **Documentation:** Docstrings for endpoint behavior (renders in /docs)
- **Authentication:** JWT or API key where needed (future)
- **CORS:** Configured for frontend origin

### Endpoint Template
```python
@router.get(
    "/{id}",
    response_model=ResponseSchema,
    summary="Brief description",
    tags=["Category"]
)
async def get_item(
    id: str,
    db: Session = Depends(get_db)
) -> ResponseSchema:
    """
    Detailed description of what this endpoint does.
    
    - **id**: Parameter description
    
    Returns description of response.
    """
    try:
        result = service.get(id)
        if not result:
            raise HTTPException(status_code=404, detail="Not found")
        return result
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error")
```

## Database Standards

- **Migrations:** Alembic for all schema changes (never modify tables directly)
- **Indexes:** Index frequently queried columns (FK, status, dates)
- **Constraints:** Use database-level validation (UNIQUE, NOT NULL, CHECK)
- **Documentation:** Comment complex queries
- **Performance:** Avoid N+1 queries, use eager loading when appropriate

### Model Template
```python
class ModelName(Base):
    """Description of what this model represents."""
    __tablename__ = "table_name"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    foreign_id: Mapped[str] = mapped_column(String(36), ForeignKey("other.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    related: Mapped["OtherModel"] = relationship("OtherModel", back_populates="this")
```

## Testing Standards

- **Unit Tests:** Mock external dependencies (APIs, services)
- **Integration Tests:** Use test database (SQLite in memory)
- **Coverage:** Target 80%+ code coverage
- **Fixtures:** Reusable test data in conftest.py
- **Assertions:** Clear failure messages

### Test Template
```python
def test_create_booking_success(db_session, sample_room):
    """Test successful booking creation."""
    booking_data = {
        "room_id": sample_room.id,
        "check_in": date.today(),
        "check_out": date.today() + timedelta(days=3),
        "guest_name": "Test Guest"
    }
    
    result = booking_service.create(db_session, booking_data)
    
    assert result.id is not None
    assert result.guest_name == "Test Guest"
    assert result.status == "confirmed"

def test_get_booking_not_found(db_session):
    """Test 404 when booking doesn't exist."""
    with pytest.raises(HTTPException) as exc:
        booking_service.get(db_session, "non-existent-id")
    
    assert exc.value.status_code == 404
```

## Frontend Standards (Vanilla JS)

- **Modularity:** Separate functions for each feature
- **DOM Ready:** Use `DOMContentLoaded` event
- **API Calls:** Use `fetch` with async/await
- **Error Handling:** Try-catch with user-friendly messages
- **Toast Notifications:** Use `showToast()` for feedback
- **Responsive:** Mobile-first CSS approach

### JavaScript Template
```javascript
async function loadBookings() {
    try {
        const bookings = await fetchBookings(filters);
        const tbody = document.getElementById('all-bookings');
        
        tbody.innerHTML = bookings.map(b => `
            <tr>
                <td>${b.guest_name}</td>
                <td>${formatDate(b.check_in)}</td>
                <td><span class="status-badge ${b.status}">${formatStatus(b.status)}</span></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Failed to load bookings:', error);
        showToast('Failed to load bookings', 'error');
    }
}
```

---

*Code standards for Hotel PMS development*
