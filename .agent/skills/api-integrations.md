---
name: Hotel PMS API Integration Expert
description: |
  Specialized in integrating external APIs for Hotel PMS including Channex
  (Channel Manager), TTLock (Smart Lock), and Telegram (Notifications).
  Handles OAuth authentication, webhook processing, and API fallback patterns.
version: 1.0.0
dependencies: httpx>=0.24, python-telegram-bot>=20.0

---

# Hotel PMS API Integration Expert

## When to Use

- Integrating Channex booking sync
- Implementing TTLock passcode generation
- Setting up Telegram notifications
- Debugging API connection issues
- Implementing webhook handlers
- Creating mock services for testing

## External APIs Overview

### Channex (Channel Manager)
- **Purpose:** Sync bookings from OTAs (Airbnb, Booking.com, Agoda, Trip.com)
- **Auth:** API Key in header (`user-api-key`)
- **Base URL:** `https://staging.channex.io/api/v1` or `https://api.channex.io/api/v1`
- **Key Endpoints:**
  - `GET /properties` - List properties
  - `GET /bookings` - List bookings with filters
  - `GET /feed` - New/modified bookings feed
  - `POST /messages` - Send message to guest
- **Webhook Events:** `booking_created`, `booking_modified`, `booking_cancelled`

### TTLock (Smart Lock)
- **Purpose:** Generate timed passcodes for guests
- **Auth:** OAuth2 with access token
- **Base URL:** `https://euopen.ttlock.com/v3`
- **Key Endpoints:**
  - `POST /oauth2/token` - Get access token
  - `GET /lock/list` - List all locks
  - `POST /keyboardPwd/add` - Create passcode
  - `POST /keyboardPwd/delete` - Delete passcode
- **Passcode Types:**
  - 1: Permanent
  - 2: Timed (for bookings)
  - 3: One-time

### Telegram (Notifications)
- **Purpose:** Send real-time alerts to staff
- **Auth:** Bot Token
- **Library:** `python-telegram-bot`
- **Key Methods:**
  - `send_message()` - Text notification
  - `send_photo()` - Image with caption

## Integration Patterns

### API Client with Retry
```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class APIClient:
    def __init__(self, base_url: str, headers: dict):
        self.base_url = base_url
        self.headers = headers
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def request(self, method: str, endpoint: str, **kwargs):
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
```

### Webhook Handler
```python
@router.post("/webhooks/channex")
async def handle_channex_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Process Channex webhook events."""
    payload = await request.json()
    event_type = payload.get("event")
    
    if event_type == "booking_created":
        background_tasks.add_task(
            process_new_booking,
            db,
            payload["booking"]
        )
    elif event_type == "booking_modified":
        background_tasks.add_task(
            update_booking,
            db,
            payload["booking"]
        )
    elif event_type == "booking_cancelled":
        background_tasks.add_task(
            cancel_booking,
            db,
            payload["booking_id"]
        )
    
    return {"status": "received"}
```

### Service with Mock Fallback
```python
# services/__init__.py
from app.config import settings

def get_channex_service():
    if settings.channex_api_key and settings.channex_api_key != "your_channex_api_key":
        from .channex_service import ChannexService
        return ChannexService()
    else:
        from .mock_services import MockChannexService
        return MockChannexService()

channex_service = get_channex_service()
```

## Channex Integration

### Booking Sync Flow
```
1. Poll /feed endpoint (every 5 minutes)
2. For each new booking:
   - Parse booking data
   - Create/update in database
   - Generate passcode (TTLock)
   - Send passcode to guest (via Channex messaging)
   - Acknowledge revision
3. Handle errors with retry
```

### Parsing Booking Event
```python
def parse_channex_booking(data: dict) -> BookingFromChannex:
    guest = data.get("guest", {}) or {}
    
    return BookingFromChannex(
        channex_booking_id=data["id"],
        channex_revision_id=data.get("revision_id"),
        property_id=data["property_id"],
        arrival_date=datetime.strptime(data["arrival_date"], "%Y-%m-%d").date(),
        departure_date=datetime.strptime(data["departure_date"], "%Y-%m-%d").date(),
        status=data["status"],
        ota_name=data.get("ota_name", "direct"),
        guest_name=guest.get("name"),
        guest_email=guest.get("email"),
        guest_nationality=guest.get("nationality")
    )
```

## TTLock Integration

### Passcode Generation Flow
```
1. Get access token (cached, refresh on expiry)
2. Find lock ID for room
3. Calculate valid time range (check-in 3PM to check-out 11AM)
4. Create primary passcode
5. Create backup passcode
6. Store in database
7. Return passcodes to caller
```

### OAuth Token Management
```python
async def get_access_token(self) -> str:
    # Check if cached token is valid
    if self._access_token and self._token_expires_at:
        if time.time() < self._token_expires_at - 300:  # 5 min buffer
            return self._access_token
    
    # Get new token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{self.base_url}/oauth2/token",
            data={
                "clientId": self.client_id,
                "clientSecret": self.client_secret,
                "username": self.username,
                "password": self.password_md5
            }
        )
        data = response.json()
        
        self._access_token = data["access_token"]
        self._token_expires_at = time.time() + data["expires_in"]
        
        return self._access_token
```

## Telegram Integration

### Notification Templates
```python
async def send_new_booking_notification(self, booking: Booking):
    message = f"""
🏨 <b>New Booking</b>

Guest: {booking.guest_name}
Room: {booking.room.room_number}
Check-in: {booking.check_in.strftime('%d %b %Y')}
Check-out: {booking.check_out.strftime('%d %b %Y')}
OTA: {booking.ota_source}

<i>Passcode will be generated automatically</i>
"""
    await self.send_message(message)

async def send_maintenance_alert(self, issue: MaintenanceIssue):
    message = f"""
⚠️ <b>Maintenance Issue</b>

Room: {issue.room.room_number}
Issue: {issue.description}
Severity: {issue.severity.upper()}
Reported by: {issue.reporter}

<i>Please address ASAP</i>
"""
    await self.send_message(message)
```

---

*Specialized skill for Hotel PMS API integrations*
