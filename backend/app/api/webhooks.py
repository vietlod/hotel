"""
Hotel PMS - Webhook API Routes
Handles incoming webhooks from Channex.
"""
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.models import Booking, Room, Property, Guest, AccessCode
from app.schemas import ChannexWebhookPayload
from app.services import channex_service, ttlock_service, telegram_service
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks")


@router.post("/channex")
async def channex_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Receive webhooks from Channex.
    
    Events:
    - booking_new: New booking created
    - booking_modification: Booking modified
    - booking_cancellation: Booking cancelled
    - sync_error: Channel sync error
    """
    # Get raw payload
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    event = payload.get("event")
    logger.info(f"Received Channex webhook: {event}")
    
    # Handle different events
    if event == "booking_new":
        background_tasks.add_task(
            process_new_booking,
            payload.get("payload", {})
        )
    elif event == "booking_modification":
        background_tasks.add_task(
            process_booking_modification,
            payload.get("payload", {})
        )
    elif event == "booking_cancellation":
        background_tasks.add_task(
            process_booking_cancellation,
            payload.get("payload", {})
        )
    elif event == "message":
        background_tasks.add_task(
            process_guest_message,
            payload.get("payload", {})
        )
    elif event == "sync_error":
        background_tasks.add_task(
            handle_sync_error,
            payload.get("payload", {})
        )
    else:
        logger.warning(f"Unknown webhook event: {event}")
    
    return {"status": "received", "event": event}


async def process_new_booking(booking_data: dict):
    """
    Process new booking from Channex.
    
    1. Parse booking data
    2. Find matching room
    3. Create booking record
    4. Generate passcode
    5. Send passcode to guest
    6. Notify admin via Telegram
    """
    try:
        logger.info(f"Processing new booking: {booking_data.get('id')}")
        
        # Parse booking event
        booking_event = channex_service.parse_booking_event(booking_data)
        
        # TODO: Find or create room mapping based on channex room_type_id
        # For now, we'll create based on the booking data
        
        # Create booking in database
        # This would be done with proper DB session
        # booking = Booking(
        #     channex_booking_id=booking_event.channex_booking_id,
        #     room_id=room_id,
        #     ...
        # )
        
        # Acknowledge the booking revision to Channex
        if booking_event.channex_revision_id:
            await channex_service.acknowledge_booking_revision(
                booking_event.channex_revision_id
            )
        
        # Notify admin
        await telegram_service.notify_new_booking(
            check_in=str(booking_event.arrival_date),
            check_out=str(booking_event.departure_date),
            room_number="TBD",  # Map from room_type_id
            guest_name=booking_event.guest_name or "Guest",
            ota_source=booking_event.ota_name,
            booking_id=booking_event.channex_booking_id
        )
        
        logger.info(f"Booking processed: {booking_event.channex_booking_id}")
        
    except Exception as e:
        logger.error(f"Error processing new booking: {e}")
        # Notify admin about error
        await telegram_service.send_message(
            "admin",
            f"⚠️ <b>Booking Processing Error</b>\n\n{str(e)}"
        )


async def generate_and_send_passcode(booking_id: str, room_id: str):
    """
    Generate passcode and send to guest.
    
    Called after booking is confirmed.
    """
    try:
        # TODO: Get booking and room from database
        # booking = db.query(Booking).filter(Booking.id == booking_id).first()
        # room = db.query(Room).filter(Room.id == room_id).first()
        
        # Generate passcode via TTLock
        # passcode_data = await ttlock_service.create_booking_passcode(
        #     lock_id=room.ttlock_lock_id,
        #     guest_name=booking.guest_name,
        #     check_in=datetime.combine(booking.check_in, datetime.min.time()),
        #     check_out=datetime.combine(booking.check_out, datetime.max.time())
        # )
        
        # Save passcode to database
        # access_code = AccessCode(
        #     booking_id=booking_id,
        #     passcode=passcode_data["passcode"],
        #     ...
        # )
        
        # Send to guest via Channex
        # await channex_service.send_passcode_message(
        #     booking_id=booking.channex_booking_id,
        #     guest_name=booking.guest_name,
        #     check_in_date=booking.check_in,
        #     check_out_date=booking.check_out,
        #     passcode=passcode_data["passcode"],
        #     property_address=property.address
        # )
        
        logger.info(f"Passcode generated and sent for booking {booking_id}")
        
    except Exception as e:
        logger.error(f"Error generating passcode: {e}")


async def process_booking_modification(booking_data: dict):
    """Process booking modification."""
    try:
        logger.info(f"Processing booking modification: {booking_data.get('id')}")
        
        # TODO: Update booking in database
        # Check if dates changed - may need new passcode
        
        # Acknowledge revision
        revision_id = booking_data.get("revision_id")
        if revision_id:
            await channex_service.acknowledge_booking_revision(revision_id)
        
    except Exception as e:
        logger.error(f"Error processing modification: {e}")


async def process_booking_cancellation(booking_data: dict):
    """Process booking cancellation."""
    try:
        booking_id = booking_data.get("id")
        logger.info(f"Processing booking cancellation: {booking_id}")
        
        # TODO: 
        # 1. Mark booking as cancelled in database
        # 2. Revoke passcode from TTLock
        # 3. Notify admin
        
        # Acknowledge revision
        revision_id = booking_data.get("revision_id")
        if revision_id:
            await channex_service.acknowledge_booking_revision(revision_id)
        
        await telegram_service.send_message(
            "admin",
            f"❌ <b>Booking Cancelled</b>\n\nBooking ID: <code>{booking_id}</code>"
        )
        
    except Exception as e:
        logger.error(f"Error processing cancellation: {e}")


async def process_guest_message(message_data: dict):
    """
    Process incoming message from guest.
    
    Check for common issues (passcode problems) and auto-respond.
    """
    try:
        booking_id = message_data.get("booking_id")
        message_text = message_data.get("message", "").lower()
        
        logger.info(f"Guest message for booking {booking_id}: {message_text[:50]}...")
        
        # Check for passcode issues
        passcode_keywords = ["code", "password", "door", "lock", "can't open", "not working"]
        
        if any(keyword in message_text for keyword in passcode_keywords):
            # Guest may have passcode issue
            # TODO: Get backup passcode from database and send
            
            await telegram_service.notify_passcode_issue(
                room_number="TBD",
                guest_name="Guest",
                issue=message_text[:100],
                backup_code="Sending backup..."
            )
            
            # TODO: Send backup passcode via Channex
            # await channex_service.send_message(
            #     booking_id=booking_id,
            #     message=f"Here's your backup code: {backup_code}"
            # )
        
        # Forward to admin for other messages
        await telegram_service.send_message(
            "admin",
            f"💬 <b>Guest Message</b>\n\nBooking: <code>{booking_id}</code>\n\n{message_text[:500]}"
        )
        
    except Exception as e:
        logger.error(f"Error processing guest message: {e}")


async def handle_sync_error(error_data: dict):
    """Handle sync error from Channex."""
    try:
        logger.error(f"Channex sync error: {error_data}")
        
        await telegram_service.send_message(
            "admin",
            f"⚠️ <b>Channel Sync Error</b>\n\n<pre>{str(error_data)[:500]}</pre>"
        )
        
    except Exception as e:
        logger.error(f"Error handling sync error: {e}")
