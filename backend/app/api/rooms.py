"""
Hotel PMS - Rooms API Routes
Room management and smart lock control.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
import logging

from app.schemas import RoomCreate, RoomResponse
from app.services import ttlock_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rooms")


@router.get("", response_model=List[RoomResponse])
async def list_rooms(
    property_id: Optional[str] = Query(None, description="Filter by property"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """
    List all rooms with optional filters.
    """
    # TODO: Query from database
    return []


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str):
    """
    Get room details.
    """
    # TODO: Query from database
    raise HTTPException(status_code=404, detail="Room not found")


@router.post("", response_model=RoomResponse)
async def create_room(room: RoomCreate):
    """
    Create a new room.
    """
    # TODO: Create in database
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.put("/{room_id}/status")
async def update_room_status(room_id: str, status: str):
    """
    Update room status (available, occupied, cleaning, maintenance).
    """
    valid_statuses = ["available", "occupied", "cleaning", "maintenance"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    # TODO: Update in database
    return {"room_id": room_id, "status": status}


# ============== Smart Lock Control ==============

@router.get("/{room_id}/lock/status")
async def get_lock_status(room_id: str):
    """
    Get smart lock status (locked/unlocked, battery, etc).
    """
    # TODO: Get lock_id from room in database
    # For demo, return mock
    raise HTTPException(status_code=501, detail="Get lock_id from database first")


@router.post("/{room_id}/lock/unlock")
async def unlock_room(room_id: str):
    """
    Remotely unlock the room.
    
    Requires TTLock gateway connection.
    """
    # TODO: Get lock_id from database
    # result = await ttlock_service.unlock(lock_id)
    raise HTTPException(status_code=501, detail="Get lock_id from database first")


@router.post("/{room_id}/lock/lock")
async def lock_room(room_id: str):
    """
    Remotely lock the room.
    """
    # TODO: Get lock_id from database
    raise HTTPException(status_code=501, detail="Get lock_id from database first")


@router.get("/{room_id}/passcodes")
async def list_room_passcodes(room_id: str):
    """
    List all passcodes for a room's lock.
    """
    # TODO: Get lock_id from database
    # passcodes = await ttlock_service.get_passcodes(lock_id)
    raise HTTPException(status_code=501, detail="Get lock_id from database first")


# ============== TTLock Management (Admin) ==============

@router.get("/admin/locks")
async def list_all_locks():
    """
    List all locks from TTLock account.
    """
    try:
        locks = await ttlock_service.get_locks()
        return {"locks": locks}
    except Exception as e:
        logger.error(f"Error getting locks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/gateways")
async def list_all_gateways():
    """
    List all gateways from TTLock account.
    """
    try:
        gateways = await ttlock_service.get_gateways()
        return {"gateways": gateways}
    except Exception as e:
        logger.error(f"Error getting gateways: {e}")
        raise HTTPException(status_code=500, detail=str(e))
