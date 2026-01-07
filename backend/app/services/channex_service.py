"""
Hotel PMS - Channex Service
Integration with Channex.io Channel Manager API.
"""
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import logging

from app.config import settings
from app.schemas import BookingFromChannex, ChannexBookingEvent

logger = logging.getLogger(__name__)


class ChannexService:
    """
    Channex.io API Integration Service.
    
    Handles booking synchronization, messaging, and webhook verification.
    API Docs: https://docs.channex.io
    """
    
    def __init__(self):
        self.base_url = settings.channex_base_url
        self.api_key = settings.channex_api_key
        self.headers = {
            "Content-Type": "application/json",
            "user-api-key": self.api_key
        }
        
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> dict:
        """Make HTTP request to Channex API."""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Channex API error: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Channex request error: {str(e)}")
                raise
    
    # ============== Property Management ==============
    
    async def get_properties(self) -> List[dict]:
        """Get all properties linked to this account."""
        response = await self._request("GET", "/properties")
        return response.get("data", [])
    
    async def get_property(self, property_id: str) -> dict:
        """Get single property details."""
        response = await self._request("GET", f"/properties/{property_id}")
        return response.get("data", {})
    
    # ============== Booking Sync ==============
    
    async def get_bookings(
        self, 
        property_id: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        status: Optional[str] = None
    ) -> List[dict]:
        """
        Get bookings from Channex.
        
        Args:
            property_id: Filter by property
            from_date: Arrival date from
            to_date: Arrival date to
            status: Booking status filter
        """
        params = {}
        if property_id:
            params["filter[property_id]"] = property_id
        if from_date:
            params["filter[arrival_date][gte]"] = from_date.isoformat()
        if to_date:
            params["filter[arrival_date][lte]"] = to_date.isoformat()
        if status:
            params["filter[status]"] = status
            
        response = await self._request("GET", "/bookings", params=params)
        return response.get("data", [])
    
    async def get_booking(self, booking_id: str) -> dict:
        """Get single booking details."""
        response = await self._request("GET", f"/bookings/{booking_id}")
        return response.get("data", {})
    
    async def get_feed(self) -> List[dict]:
        """
        Get booking feed (new/modified bookings).
        
        This is the recommended way to poll for new bookings.
        After processing, call acknowledge_booking_revision().
        """
        response = await self._request("GET", "/feed")
        return response.get("data", [])
    
    async def acknowledge_booking_revision(self, revision_id: str) -> bool:
        """
        Acknowledge a booking revision as processed.
        
        This prevents the revision from appearing in future feed calls.
        """
        try:
            await self._request("POST", f"/ack_booking_revision/{revision_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to acknowledge revision {revision_id}: {e}")
            return False
    
    # ============== Booking Operations ==============
    
    async def confirm_booking(self, booking_id: str) -> dict:
        """Confirm a pending booking."""
        response = await self._request(
            "PUT", 
            f"/bookings/{booking_id}",
            data={"status": "confirmed"}
        )
        return response.get("data", {})
    
    async def cancel_booking(
        self, 
        booking_id: str, 
        reason: Optional[str] = None
    ) -> dict:
        """Cancel a booking."""
        data = {"status": "cancelled"}
        if reason:
            data["cancellation_reason"] = reason
            
        response = await self._request("PUT", f"/bookings/{booking_id}", data=data)
        return response.get("data", {})
    
    # ============== Guest Messaging ==============
    
    async def get_messages(self, booking_id: str) -> List[dict]:
        """Get messages for a booking."""
        response = await self._request(
            "GET", 
            "/messages",
            params={"filter[booking_id]": booking_id}
        )
        return response.get("data", [])
    
    async def send_message(
        self, 
        booking_id: str, 
        message: str,
        message_type: str = "guest"
    ) -> dict:
        """
        Send a message to guest via OTA.
        
        Args:
            booking_id: The booking ID
            message: Message text
            message_type: "guest" for guest messages
        """
        data = {
            "booking_id": booking_id,
            "message": message,
            "message_type": message_type
        }
        response = await self._request("POST", "/messages", data=data)
        return response.get("data", {})
    
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
        """
        Send check-in instructions with passcode to guest.
        
        Returns the sent message data.
        """
        message = f"""
Hello {guest_name}! 🏠

Welcome! Here are your check-in instructions:

📅 Check-in: {check_in_date.strftime('%B %d, %Y')} (from 3:00 PM)
📅 Check-out: {check_out_date.strftime('%B %d, %Y')} (by 11:00 AM)

📍 Address: {property_address}

🔐 Door Access Code: {passcode}
(Valid from check-in to check-out)

"""
        if wifi_name and wifi_password:
            message += f"""
📶 WiFi Network: {wifi_name}
🔑 WiFi Password: {wifi_password}

"""
        
        message += """
If you have any issues with the door code, please reply to this message and we'll send you a backup code.

Enjoy your stay! 🎉
"""
        
        return await self.send_message(booking_id, message.strip())
    
    # ============== Webhook Verification ==============
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from Channex.
        
        Note: Channex uses a simple API key verification in headers.
        """
        # For now, just verify the webhook secret matches
        return signature == settings.channex_webhook_secret
    
    def parse_booking_event(self, event_data: dict) -> BookingFromChannex:
        """Parse raw Channex booking event into typed object."""
        guest = event_data.get("guest", {}) or {}
        
        return BookingFromChannex(
            channex_booking_id=event_data["id"],
            channex_revision_id=event_data.get("revision_id"),
            property_id=event_data["property_id"],
            room_type_id=event_data.get("room_type_id"),
            arrival_date=datetime.strptime(event_data["arrival_date"], "%Y-%m-%d").date(),
            departure_date=datetime.strptime(event_data["departure_date"], "%Y-%m-%d").date(),
            status=event_data["status"],
            ota_name=event_data.get("ota_name", "direct"),
            ota_reservation_code=event_data.get("ota_reservation_code"),
            guest_name=guest.get("name"),
            guest_email=guest.get("email"),
            guest_phone=guest.get("phone"),
            guest_nationality=guest.get("nationality"),
            guests_count=event_data.get("guests", 1)
        )
    
    # ============== Health Check ==============
    
    async def health_check(self) -> str:
        """Check Channex API connectivity."""
        try:
            await self.get_properties()
            return "connected"
        except Exception as e:
            logger.warning(f"Channex health check failed: {e}")
            return "disconnected"


# Singleton instance
channex_service = ChannexService()
