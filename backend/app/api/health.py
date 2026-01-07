"""
Hotel PMS - Health Check API
System health and connectivity status.
"""
from fastapi import APIRouter
import logging

from app.config import settings
from app.schemas import HealthCheck
from app.services import channex_service, ttlock_service, telegram_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Check system health and external service connectivity.
    """
    # Check database
    db_status = "connected"  # TODO: Actually check DB connection
    
    # Check external services
    channex_status = await channex_service.health_check()
    ttlock_status = await ttlock_service.health_check()
    telegram_status = await telegram_service.health_check()
    
    return HealthCheck(
        status="healthy",
        version=settings.api_version,
        environment=settings.env,
        database=db_status,
        channex=channex_status,
        ttlock=ttlock_status,
        telegram=telegram_status
    )


@router.get("/health/channex")
async def channex_health():
    """Test Channex connectivity."""
    try:
        properties = await channex_service.get_properties()
        return {
            "status": "connected",
            "properties_count": len(properties),
            "properties": [p.get("name") for p in properties[:5]]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/health/ttlock")
async def ttlock_health():
    """Test TTLock connectivity."""
    try:
        locks = await ttlock_service.get_locks()
        gateways = await ttlock_service.get_gateways()
        return {
            "status": "connected",
            "locks_count": len(locks),
            "gateways_count": len(gateways)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/health/telegram")
async def telegram_health():
    """Test Telegram bot connectivity."""
    status = await telegram_service.health_check()
    return {"status": status}


@router.post("/health/telegram/test")
async def telegram_test_message():
    """Send a test message to admin Telegram."""
    try:
        success = await telegram_service.send_message(
            "admin",
            "🧪 <b>Test Message</b>\n\nHotel PMS is working correctly!"
        )
        return {"sent": success}
    except Exception as e:
        return {"sent": False, "error": str(e)}
