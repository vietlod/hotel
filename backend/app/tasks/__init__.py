"""
Hotel PMS - Celery Tasks
Async background tasks for booking processing, XNC export, etc.
"""
from celery import Celery
from datetime import date, datetime, timedelta
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "hotel_pms",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
)

# Celery Beat schedule (periodic tasks)
celery_app.conf.beat_schedule = {
    # Sync bookings from Channex every 5 minutes
    "sync-channex-bookings": {
        "task": "app.tasks.sync_channex_bookings",
        "schedule": 300.0,  # 5 minutes
    },
    
    # Generate daily XNC report at 10 PM
    "generate-daily-xnc-report": {
        "task": "app.tasks.generate_daily_xnc_report",
        "schedule": {
            "hour": 22,
            "minute": 0
        }
    },
    
    # Send check-in reminders 24h before
    "send-checkin-reminders": {
        "task": "app.tasks.send_checkin_reminders",
        "schedule": 3600.0,  # Every hour
    },
    
    # Clean up old passcodes
    "cleanup-expired-passcodes": {
        "task": "app.tasks.cleanup_expired_passcodes",
        "schedule": 86400.0,  # Daily
    },
}


# ============== Booking Tasks ==============

@celery_app.task(name="app.tasks.sync_channex_bookings")
def sync_channex_bookings():
    """
    Periodic task to sync bookings from Channex.
    
    Fetches new/modified bookings from Channex feed
    and updates local database.
    """
    import asyncio
    from app.services import channex_service
    
    async def _sync():
        try:
            # Get feed of new/modified bookings
            feed = await channex_service.get_feed()
            
            for booking_data in feed:
                # TODO: Process each booking
                # - Create/update in database
                # - Generate passcode if new
                # - Acknowledge revision
                
                revision_id = booking_data.get("revision_id")
                if revision_id:
                    await channex_service.acknowledge_booking_revision(revision_id)
            
            logger.info(f"Synced {len(feed)} bookings from Channex")
            return len(feed)
            
        except Exception as e:
            logger.error(f"Error syncing Channex bookings: {e}")
            raise
    
    return asyncio.get_event_loop().run_until_complete(_sync())


@celery_app.task(name="app.tasks.process_new_booking")
def process_new_booking(booking_id: str):
    """
    Process a new booking:
    1. Create in database
    2. Generate passcode
    3. Send to guest
    4. Notify admin
    """
    import asyncio
    from app.services import ttlock_service, channex_service, telegram_service
    
    async def _process():
        try:
            # TODO: Get booking from database
            # booking = db.query(Booking).filter(Booking.id == booking_id).first()
            
            # Generate passcode
            # passcode_data = await ttlock_service.create_booking_passcode(...)
            
            # Send to guest
            # await channex_service.send_passcode_message(...)
            
            # Notify admin
            # await telegram_service.notify_new_booking(...)
            
            logger.info(f"Processed booking {booking_id}")
            
        except Exception as e:
            logger.error(f"Error processing booking {booking_id}: {e}")
            raise
    
    return asyncio.get_event_loop().run_until_complete(_process())


# ============== Passcode Tasks ==============

@celery_app.task(name="app.tasks.generate_passcode")
def generate_passcode(booking_id: str):
    """
    Generate passcode for a booking.
    """
    import asyncio
    from app.services import ttlock_service
    
    async def _generate():
        try:
            # TODO: Get booking and room from database
            # Generate passcode via TTLock
            logger.info(f"Generated passcode for booking {booking_id}")
        except Exception as e:
            logger.error(f"Error generating passcode: {e}")
            raise
    
    return asyncio.get_event_loop().run_until_complete(_generate())


@celery_app.task(name="app.tasks.send_checkin_reminders")
def send_checkin_reminders():
    """
    Send check-in reminders with passcode to guests
    checking in within 24 hours.
    """
    import asyncio
    from app.services import channex_service
    
    async def _send_reminders():
        try:
            tomorrow = date.today() + timedelta(days=1)
            
            # TODO: Query bookings checking in tomorrow
            # that haven't received passcode yet
            
            # For each booking, send reminder with passcode
            
            logger.info("Sent check-in reminders")
            
        except Exception as e:
            logger.error(f"Error sending reminders: {e}")
    
    return asyncio.get_event_loop().run_until_complete(_send_reminders())


@celery_app.task(name="app.tasks.cleanup_expired_passcodes")
def cleanup_expired_passcodes():
    """
    Delete expired passcodes from TTLock.
    """
    import asyncio
    from app.services import ttlock_service
    
    async def _cleanup():
        try:
            # TODO: Get expired access codes from database
            # Delete from TTLock
            # Mark as deleted in database
            
            logger.info("Cleaned up expired passcodes")
            
        except Exception as e:
            logger.error(f"Error cleaning up passcodes: {e}")
    
    return asyncio.get_event_loop().run_until_complete(_cleanup())


# ============== XNC Tasks ==============

@celery_app.task(name="app.tasks.generate_daily_xnc_report")
def generate_daily_xnc_report():
    """
    Generate daily XNC report for all foreign guests
    who checked in today.
    """
    import asyncio
    from app.services import xnc_service, telegram_service
    
    async def _generate():
        try:
            today = date.today()
            
            # TODO: Query foreign guests checked in today
            # guests = ...
            
            # Generate XML report
            # file_path = xnc_service.generate_xml(guests, ...)
            
            # Notify admin
            # await telegram_service.notify_xnc_report(...)
            
            logger.info(f"Generated XNC report for {today}")
            
        except Exception as e:
            logger.error(f"Error generating XNC report: {e}")
    
    return asyncio.get_event_loop().run_until_complete(_generate())


@celery_app.task(name="app.tasks.generate_xnc_report")
def generate_xnc_report(report_date: str, property_id: str = None):
    """
    Generate XNC report for a specific date.
    Can be triggered manually.
    """
    import asyncio
    from app.services import xnc_service, telegram_service
    
    async def _generate():
        try:
            target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
            
            # TODO: Query and generate report
            
            logger.info(f"Generated XNC report for {target_date}")
            
        except Exception as e:
            logger.error(f"Error generating XNC report: {e}")
    
    return asyncio.get_event_loop().run_until_complete(_generate())


# ============== Notification Tasks ==============

@celery_app.task(name="app.tasks.send_telegram_notification")
def send_telegram_notification(channel: str, message: str):
    """
    Send a Telegram notification.
    Useful for async notification sending.
    """
    import asyncio
    from app.services import telegram_service
    
    async def _send():
        await telegram_service.send_message(channel, message)
    
    return asyncio.get_event_loop().run_until_complete(_send())


# ============== Housekeeping Tasks ==============

@celery_app.task(name="app.tasks.mark_rooms_for_cleaning")
def mark_rooms_for_cleaning():
    """
    Automatically mark rooms as dirty after checkout.
    Run hourly.
    """
    import asyncio
    from app.services import telegram_service
    
    async def _mark():
        try:
            # TODO: Query bookings that just checked out
            # Mark rooms as dirty
            # Notify housekeeping
            
            logger.info("Marked rooms for cleaning")
            
        except Exception as e:
            logger.error(f"Error marking rooms: {e}")
    
    return asyncio.get_event_loop().run_until_complete(_mark())
