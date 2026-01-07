"""
Hotel PMS - Telegram Service (Stub for development)
Will use real python-telegram-bot when available.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramServiceStub:
    """Stub Telegram service that logs instead of sending."""
    
    def __init__(self):
        self.enabled = False
        logger.info("TelegramService: Running in stub mode (no actual messages sent)")
    
    async def health_check(self) -> str:
        """
        Lightweight health check for Telegram integration.
        
        Returns:
            str: Simple status string for /health endpoint.
        """
        # In stub mode we always report "stub" but keep the same interface
        # as the real Telegram service.
        logger.debug("TelegramServiceStub.health_check called")
        return "stub"
    
    async def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML"):
        """Log message instead of sending."""
        logger.info(f"[TELEGRAM STUB] Would send to {chat_id}: {text[:100]}...")
        return {"ok": True, "stub": True}
    
    async def send_new_booking_notification(self, *args, **kwargs):
        logger.info("[TELEGRAM STUB] New booking notification")
        return True
    
    async def send_passcode_notification(self, *args, **kwargs):
        logger.info("[TELEGRAM STUB] Passcode notification")
        return True
    
    async def send_checkin_reminder(self, *args, **kwargs):
        logger.info("[TELEGRAM STUB] Check-in reminder")
        return True
    
    async def send_checkout_reminder(self, *args, **kwargs):
        logger.info("[TELEGRAM STUB] Check-out reminder")
        return True
    
    async def send_maintenance_alert(self, *args, **kwargs):
        logger.info("[TELEGRAM STUB] Maintenance alert")
        return True


# Create singleton
telegram_service = TelegramServiceStub()
