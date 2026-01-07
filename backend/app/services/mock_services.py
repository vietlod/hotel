"""
Hotel PMS - Mock Services
Mock implementations for testing without real API credentials.
"""
import random
import string
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MockChannexService:
    """
    Mock Channex service for testing without real API.
    
    Simulates booking sync, messaging, and webhook events.
    """
    
    def __init__(self):
        self._bookings: Dict[str, dict] = {}
        self._messages: Dict[str, List[dict]] = {}
        self._revision_counter = 0
        
        # Pre-populate with sample bookings
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Create sample bookings for testing."""
        sample_bookings = [
            {
                "id": "channex_booking_001",
                "property_id": "prop_sunrise_apt",
                "room_type_id": "room_type_studio",
                "arrival_date": (date.today() + timedelta(days=1)).isoformat(),
                "departure_date": (date.today() + timedelta(days=4)).isoformat(),
                "status": "confirmed",
                "ota_name": "Airbnb",
                "ota_reservation_code": "HMABCDEF123",
                "guest": {
                    "name": "John Smith",
                    "email": "john.smith@example.com",
                    "phone": "+1234567890",
                    "nationality": "United States"
                },
                "guests_count": 2,
                "revision_id": "rev_001"
            },
            {
                "id": "channex_booking_002",
                "property_id": "prop_sunrise_apt",
                "room_type_id": "room_type_1br",
                "arrival_date": (date.today() + timedelta(days=2)).isoformat(),
                "departure_date": (date.today() + timedelta(days=5)).isoformat(),
                "status": "confirmed",
                "ota_name": "Booking.com",
                "ota_reservation_code": "4567890123",
                "guest": {
                    "name": "Marie Dupont",
                    "email": "marie.dupont@example.fr",
                    "phone": "+33612345678",
                    "nationality": "France"
                },
                "guests_count": 1,
                "revision_id": "rev_002"
            },
            {
                "id": "channex_booking_003",
                "property_id": "prop_sunrise_apt",
                "room_type_id": "room_type_studio",
                "arrival_date": date.today().isoformat(),
                "departure_date": (date.today() + timedelta(days=3)).isoformat(),
                "status": "confirmed",
                "ota_name": "Agoda",
                "ota_reservation_code": "AGD789012",
                "guest": {
                    "name": "Tanaka Yuki",
                    "email": "tanaka.yuki@example.jp",
                    "phone": "+81901234567",
                    "nationality": "Japan"
                },
                "guests_count": 1,
                "revision_id": "rev_003"
            }
        ]
        
        for booking in sample_bookings:
            self._bookings[booking["id"]] = booking
    
    async def get_properties(self) -> List[dict]:
        """Get mock properties."""
        return [
            {
                "id": "prop_sunrise_apt",
                "name": "Sunrise Apartment",
                "address": "123 Nguyen Hue, District 1, Ho Chi Minh City"
            }
        ]
    
    async def get_bookings(
        self,
        property_id: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        status: Optional[str] = None
    ) -> List[dict]:
        """Get mock bookings with filters."""
        results = list(self._bookings.values())
        
        if property_id:
            results = [b for b in results if b["property_id"] == property_id]
        if status:
            results = [b for b in results if b["status"] == status]
        
        return results
    
    async def get_booking(self, booking_id: str) -> dict:
        """Get single booking."""
        return self._bookings.get(booking_id, {})
    
    async def get_feed(self) -> List[dict]:
        """Get unacknowledged bookings (simulated feed)."""
        # Return bookings that haven't been acknowledged
        return [
            b for b in self._bookings.values() 
            if not b.get("acknowledged", False)
        ]
    
    async def acknowledge_booking_revision(self, revision_id: str) -> bool:
        """Mark booking as acknowledged."""
        for booking in self._bookings.values():
            if booking.get("revision_id") == revision_id:
                booking["acknowledged"] = True
                logger.info(f"[MOCK] Acknowledged revision: {revision_id}")
                return True
        return False
    
    async def send_message(self, booking_id: str, message: str) -> dict:
        """Send message to guest (mock)."""
        if booking_id not in self._messages:
            self._messages[booking_id] = []
        
        msg = {
            "id": f"msg_{len(self._messages[booking_id]) + 1}",
            "booking_id": booking_id,
            "message": message,
            "direction": "outgoing",
            "sent_at": datetime.now().isoformat()
        }
        self._messages[booking_id].append(msg)
        
        logger.info(f"[MOCK] Sent message to booking {booking_id}: {message[:50]}...")
        return msg
    
    async def send_passcode_message(
        self,
        booking_id: str,
        guest_name: str,
        check_in_date: date,
        check_out_date: date,
        passcode: str,
        property_address: str,
        wifi_name: Optional[str] = None,
        wifi_password: Optional[str] = None
    ) -> dict:
        """Send passcode message to guest."""
        message = f"""
🏠 Welcome {guest_name}!

📅 Check-in: {check_in_date.strftime('%B %d, %Y')} (from 3:00 PM)
📅 Check-out: {check_out_date.strftime('%B %d, %Y')} (by 11:00 AM)

📍 Address: {property_address}

🔐 Door Access Code: {passcode}
"""
        if wifi_name:
            message += f"\n📶 WiFi: {wifi_name} / Password: {wifi_password}"
        
        return await self.send_message(booking_id, message)
    
    async def get_messages(self, booking_id: str) -> List[dict]:
        """Get messages for a booking."""
        return self._messages.get(booking_id, [])
    
    async def confirm_booking(self, booking_id: str) -> dict:
        """Confirm a booking."""
        if booking_id in self._bookings:
            self._bookings[booking_id]["status"] = "confirmed"
            logger.info(f"[MOCK] Confirmed booking: {booking_id}")
        return self._bookings.get(booking_id, {})
    
    async def cancel_booking(self, booking_id: str, reason: Optional[str] = None) -> dict:
        """Cancel a booking."""
        if booking_id in self._bookings:
            self._bookings[booking_id]["status"] = "cancelled"
            logger.info(f"[MOCK] Cancelled booking: {booking_id}")
        return self._bookings.get(booking_id, {})
    
    async def health_check(self) -> str:
        """Health check."""
        return "connected (mock)"
    
    def simulate_new_booking(self) -> dict:
        """Simulate a new booking event (for webhook testing)."""
        self._revision_counter += 1
        booking_id = f"channex_booking_{self._revision_counter + 100:03d}"
        
        ota_options = ["Airbnb", "Booking.com", "Agoda", "Trip.com"]
        nationality_options = ["United States", "France", "Germany", "Japan", "Korea", "Australia", "United Kingdom"]
        
        new_booking = {
            "id": booking_id,
            "property_id": "prop_sunrise_apt",
            "room_type_id": "room_type_studio",
            "arrival_date": (date.today() + timedelta(days=random.randint(1, 14))).isoformat(),
            "departure_date": (date.today() + timedelta(days=random.randint(15, 21))).isoformat(),
            "status": "confirmed",
            "ota_name": random.choice(ota_options),
            "ota_reservation_code": ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
            "guest": {
                "name": f"Guest {self._revision_counter}",
                "email": f"guest{self._revision_counter}@example.com",
                "phone": f"+{random.randint(1000000000, 9999999999)}",
                "nationality": random.choice(nationality_options)
            },
            "guests_count": random.randint(1, 3),
            "revision_id": f"rev_{self._revision_counter + 100:03d}"
        }
        
        self._bookings[booking_id] = new_booking
        logger.info(f"[MOCK] Simulated new booking: {booking_id}")
        
        return new_booking


class MockTTLockService:
    """
    Mock TTLock service for testing without real hardware.
    
    Simulates passcode generation and lock control.
    """
    
    def __init__(self):
        self._locks: Dict[int, dict] = {}
        self._passcodes: Dict[int, List[dict]] = {}
        self._passcode_counter = 1000
        
        # Pre-populate with sample locks
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Create sample locks."""
        sample_locks = [
            {
                "lockId": 10001,
                "lockName": "Room 101 - Studio A",
                "lockMac": "AA:BB:CC:DD:EE:01",
                "gatewayId": 20001,
                "electricQuantity": 85,
                "lockData": "mock_lock_data_101"
            },
            {
                "lockId": 10002,
                "lockName": "Room 102 - Studio B",
                "lockMac": "AA:BB:CC:DD:EE:02",
                "gatewayId": 20001,
                "electricQuantity": 90,
                "lockData": "mock_lock_data_102"
            },
            {
                "lockId": 10003,
                "lockName": "Room 201 - 1BR",
                "lockMac": "AA:BB:CC:DD:EE:03",
                "gatewayId": 20001,
                "electricQuantity": 75,
                "lockData": "mock_lock_data_201"
            }
        ]
        
        for lock in sample_locks:
            self._locks[lock["lockId"]] = lock
            self._passcodes[lock["lockId"]] = []
    
    async def get_locks(self, page_no: int = 1, page_size: int = 100) -> List[dict]:
        """Get all locks."""
        return list(self._locks.values())
    
    async def get_lock_detail(self, lock_id: int) -> dict:
        """Get lock details."""
        return self._locks.get(lock_id, {})
    
    async def get_gateways(self) -> List[dict]:
        """Get gateways."""
        return [
            {
                "gatewayId": 20001,
                "gatewayName": "Gateway Floor 1-2",
                "gatewayMac": "11:22:33:44:55:66",
                "isOnline": True
            }
        ]
    
    def _generate_passcode(self, length: int = 6) -> str:
        """Generate random passcode."""
        return ''.join(random.choices(string.digits, k=length))
    
    async def create_passcode(
        self,
        lock_id: int,
        passcode_name: str,
        passcode_type: int = 2,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        passcode: Optional[str] = None
    ) -> dict:
        """Create a new passcode."""
        self._passcode_counter += 1
        
        code = passcode or self._generate_passcode()
        
        passcode_data = {
            "keyboardPwdId": self._passcode_counter,
            "keyboardPwd": code,
            "keyboardPwdName": passcode_name,
            "keyboardPwdType": passcode_type,
            "startDate": start_date.isoformat() if start_date else None,
            "endDate": end_date.isoformat() if end_date else None,
            "lockId": lock_id,
            "status": "active"
        }
        
        if lock_id not in self._passcodes:
            self._passcodes[lock_id] = []
        self._passcodes[lock_id].append(passcode_data)
        
        logger.info(f"[MOCK] Created passcode {code} for lock {lock_id}")
        
        return {
            "passcode_id": self._passcode_counter,
            "passcode": code,
            "valid_from": start_date,
            "valid_to": end_date
        }
    
    async def create_booking_passcode(
        self,
        lock_id: int,
        guest_name: str,
        check_in: datetime,
        check_out: datetime
    ) -> dict:
        """Create passcode for a booking."""
        # Primary passcode
        primary = await self.create_passcode(
            lock_id=lock_id,
            passcode_name=f"Guest: {guest_name}",
            passcode_type=2,
            start_date=check_in,
            end_date=check_out
        )
        
        # Backup passcode
        backup = await self.create_passcode(
            lock_id=lock_id,
            passcode_name=f"Backup: {guest_name}",
            passcode_type=2,
            start_date=check_in,
            end_date=check_out
        )
        
        return {
            "passcode": primary["passcode"],
            "passcode_id": primary["passcode_id"],
            "backup_passcode": backup["passcode"],
            "backup_passcode_id": backup["passcode_id"],
            "valid_from": check_in,
            "valid_to": check_out
        }
    
    async def delete_passcode(self, lock_id: int, passcode_id: int) -> bool:
        """Delete a passcode."""
        if lock_id in self._passcodes:
            self._passcodes[lock_id] = [
                p for p in self._passcodes[lock_id] 
                if p["keyboardPwdId"] != passcode_id
            ]
            logger.info(f"[MOCK] Deleted passcode {passcode_id} from lock {lock_id}")
            return True
        return False
    
    async def get_passcodes(self, lock_id: int) -> List[dict]:
        """Get all passcodes for a lock."""
        return self._passcodes.get(lock_id, [])
    
    async def unlock(self, lock_id: int) -> bool:
        """Unlock remotely."""
        logger.info(f"[MOCK] Unlocked lock {lock_id}")
        return True
    
    async def lock(self, lock_id: int) -> bool:
        """Lock remotely."""
        logger.info(f"[MOCK] Locked lock {lock_id}")
        return True
    
    async def health_check(self) -> str:
        """Health check."""
        return "connected (mock)"


# Singleton mock instances
mock_channex_service = MockChannexService()
mock_ttlock_service = MockTTLockService()
