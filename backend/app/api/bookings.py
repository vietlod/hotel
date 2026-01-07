"""
Hotel PMS - Bookings API Routes
CRUD operations for bookings.
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, HTTPException, Query
import logging

from app.schemas import (
    BookingCreate, 
    BookingResponse, 
    BookingDetail,
    AccessCodeResponse
)
from app.services import channex_service, ttlock_service, telegram_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings")


@router.get("", response_model=List[BookingResponse])
async def list_bookings(
    status: Optional[str] = Query(None, description="Filter by status"),
    from_date: Optional[date] = Query(None, description="Check-in from date"),
    to_date: Optional[date] = Query(None, description="Check-in to date"),
    ota_source: Optional[str] = Query(None, description="Filter by OTA source")
):
    """
    List all bookings with optional filters.
    """
    # TODO: Query from database with filters
    # For now, return empty list
    return []


@router.get("/{booking_id}", response_model=BookingDetail)
async def get_booking(booking_id: str):
    """
    Get booking details including guests and access codes.
    """
    # TODO: Query from database
    raise HTTPException(status_code=404, detail="Booking not found")


@router.post("", response_model=BookingResponse)
async def create_booking(booking: BookingCreate):
    """
    Create a manual booking (not from OTA).
    """
    # TODO: Create booking in database
    # Generate passcode, etc.
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/{booking_id}/sync")
async def sync_booking_from_channex(booking_id: str):
    """
    Force sync a specific booking from Channex.
    """
    try:
        booking_data = await channex_service.get_booking(booking_id)
        
        if not booking_data:
            raise HTTPException(status_code=404, detail="Booking not found in Channex")
        
        # TODO: Update or create booking in local database
        
        return {"status": "synced", "booking": booking_data}
        
    except Exception as e:
        logger.error(f"Error syncing booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{booking_id}/generate-passcode", response_model=AccessCodeResponse)
async def generate_passcode(booking_id: str):
    """
    Generate new passcode for a booking.
    
    This will create a TTLock passcode and optionally send to guest.
    """
    # TODO: Get booking from database
    # booking = ...
    # room = ...
    
    # For demo, return mock data
    raise HTTPException(status_code=501, detail="Booking not found - implement database query")


@router.post("/{booking_id}/send-passcode")
async def send_passcode_to_guest(booking_id: str):
    """
    Send existing passcode to guest via Channex messaging.
    """
    # TODO: Get passcode from database and send via Channex
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/{booking_id}/send-backup-passcode")
async def send_backup_passcode(booking_id: str):
    """
    Send backup passcode to guest (when primary doesn't work).
    """
    # TODO: Get backup passcode and send
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{booking_id}/confirm")
async def confirm_booking(booking_id: str):
    """
    Confirm a pending booking.
    """
    try:
        result = await channex_service.confirm_booking(booking_id)
        return {"status": "confirmed", "booking": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{booking_id}/cancel")
async def cancel_booking(booking_id: str, reason: Optional[str] = None):
    """
    Cancel a booking.
    """
    try:
        # Cancel on Channex
        result = await channex_service.cancel_booking(booking_id, reason)
        
        # TODO: Revoke passcode from TTLock
        
        return {"status": "cancelled", "booking": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{booking_id}/messages")
async def get_booking_messages(booking_id: str):
    """
    Get all messages for a booking.
    """
    try:
        messages = await channex_service.get_messages(booking_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{booking_id}/messages")
async def send_message_to_guest(booking_id: str, message: str):
    """
    Send a message to guest via Channex.
    """
    try:
        result = await channex_service.send_message(booking_id, message)
        return {"status": "sent", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
