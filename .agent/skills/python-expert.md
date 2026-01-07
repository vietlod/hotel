---
name: Hotel PMS Python Expert
description: |
  Specialized in Hotel PMS's Python backend architecture including FastAPI,
  SQLAlchemy ORM, Pydantic validation, and async patterns. Handles API 
  development, service implementations, and database operations.
version: 1.0.0
dependencies: python>=3.11, fastapi>=0.104, sqlalchemy>=2.0, pydantic>=2.0, pytest>=7.0

---

# Hotel PMS Python Expert

## When to Use

- Implementing FastAPI endpoints and routes
- Creating SQLAlchemy models and database operations
- Developing service classes for external APIs
- Fixing Python type hints and validation issues
- Writing pytest unit and integration tests
- Optimizing database queries and performance

## Key Patterns for Hotel PMS

### FastAPI Routes
- Async route handlers with dependency injection
- Pydantic request/response validation
- Error handling with HTTPException
- Automatic OpenAPI documentation
- CORS middleware for frontend

### SQLAlchemy ORM
- Model definition with relationships (1:N, N:N)
- Session management with Depends(get_db)
- Query optimization with eager loading
- Migration handling with Alembic
- UUID primary keys

### External API Services
- Channex (booking sync)
- TTLock (passcode generation)
- Telegram (notifications)
- Mock implementations for testing

### Testing
- Unit tests for services
- Integration tests for API endpoints
- Fixture-based test data (conftest.py)
- Coverage reports (target 80%+)

## Hotel PMS Type Definitions

```python
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"


class RoomStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"


class BookingCreate(BaseModel):
    room_id: str
    check_in: date
    check_out: date
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    ota_source: str = "direct"
    guests_count: int = 1


class BookingResponse(BaseModel):
    id: str
    room_id: str
    channex_booking_id: Optional[str]
    ota_source: str
    check_in: date
    check_out: date
    nights: int
    guests_count: int
    guest_name: Optional[str]
    status: BookingStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class PasscodeCreate(BaseModel):
    booking_id: str
    valid_from: datetime
    valid_to: datetime


class PasscodeResponse(BaseModel):
    passcode: str
    backup_passcode: Optional[str]
    valid_from: datetime
    valid_to: datetime
    source: str  # "ttlock" or "mock"


class XNCGuestData(BaseModel):
    full_name: str
    gender: str
    date_of_birth: date
    nationality: str
    passport_number: str
    temporary_address: str
    arrival_date: date
    departure_date: date
```

## Service Patterns

### Booking Service
```python
class BookingService:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, data: BookingCreate) -> Booking:
        """Create new booking."""
        booking = Booking(**data.dict())
        booking.nights = (data.check_out - data.check_in).days
        self.db.add(booking)
        self.db.commit()
        return booking
    
    def get_by_id(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID."""
        return self.db.query(Booking).filter(
            Booking.id == booking_id
        ).first()
    
    def update_status(self, booking_id: str, status: BookingStatus) -> Booking:
        """Update booking status."""
        booking = self.get_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking not found: {booking_id}")
        booking.status = status
        self.db.commit()
        return booking
```

### Passcode Generation
```python
async def generate_booking_passcode(
    booking: Booking,
    ttlock_service: TTLockService
) -> PasscodeResponse:
    """Generate passcode for booking."""
    room = booking.room
    if not room.ttlock_lock_id:
        raise ValueError(f"Room {room.room_number} has no lock configured")
    
    check_in_time = datetime.combine(booking.check_in, time(15, 0))
    check_out_time = datetime.combine(booking.check_out, time(11, 0))
    
    result = await ttlock_service.create_booking_passcode(
        lock_id=int(room.ttlock_lock_id),
        guest_name=booking.guest_name or "Guest",
        check_in=check_in_time,
        check_out=check_out_time
    )
    
    return PasscodeResponse(**result, source="ttlock")
```

---

*Specialized skill for Hotel PMS Python development*
