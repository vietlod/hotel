"""
Hotel PMS - API CRUD Routes
Database-backed CRUD operations for Dashboard integration.
Matches actual SQLAlchemy models with string UUIDs.
"""
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
import logging

from app.database import get_db
from app.models import Property, Room, Booking, Guest, AccessCode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crud")


# ============== Dashboard Stats ==============

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    today = date.today()
    
    # Total active bookings
    total_bookings = db.query(Booking).filter(
        Booking.status.in_(["confirmed", "checked_in"])
    ).count()
    
    # Today check-ins
    today_checkins = db.query(Booking).filter(
        Booking.check_in == today,
        Booking.status == "confirmed"
    ).count()
    
    # Today check-outs
    today_checkouts = db.query(Booking).filter(
        Booking.check_out == today,
        Booking.status == "checked_in"
    ).count()
    
    # Occupancy rate
    total_rooms = db.query(Room).count()
    occupied_rooms = db.query(Room).filter(Room.status == "occupied").count()
    occupancy_rate = round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0)
    
    return {
        "totalBookings": total_bookings,
        "todayCheckins": today_checkins,
        "todayCheckouts": today_checkouts,
        "occupancyRate": occupancy_rate,
        "totalRooms": total_rooms,
        "occupiedRooms": occupied_rooms
    }


# ============== Properties ==============

@router.get("/properties")
def list_properties(db: Session = Depends(get_db)):
    """List all properties."""
    properties = db.query(Property).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "address": p.address,
            "city": p.city,
            "roomsCount": len(p.rooms) if p.rooms else 0
        }
        for p in properties
    ]


# ============== Rooms ==============

@router.get("/rooms")
def list_rooms(
    property_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all rooms with optional filters."""
    query = db.query(Room)
    
    if property_id:
        query = query.filter(Room.property_id == property_id)
    if status:
        query = query.filter(Room.status == status)
    
    rooms = query.all()
    
    return [
        {
            "id": r.id,
            "number": r.room_number,
            "name": r.room_type,  # Use room_type as name
            "type": r.room_type,
            "status": r.status,
            "lockId": r.ttlock_lock_id
        }
        for r in rooms
    ]


@router.put("/rooms/{room_id}/status")
def update_room_status(
    room_id: str, 
    status: str = Query(...),
    db: Session = Depends(get_db)
):
    """Update room status."""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    valid_statuses = ["available", "occupied", "cleaning", "maintenance"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    room.status = status
    db.commit()
    
    return {"id": room.id, "status": room.status}


# ============== Bookings ==============

@router.get("/bookings")
def list_bookings(
    status: Optional[str] = Query(None),
    ota: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """List all bookings with filters."""
    query = db.query(Booking).options(
        joinedload(Booking.room)
    )
    
    if status:
        query = query.filter(Booking.status == status)
    if ota:
        query = query.filter(Booking.ota_source == ota)
    if from_date:
        query = query.filter(Booking.check_in >= from_date)
    if to_date:
        query = query.filter(Booking.check_in <= to_date)
    
    bookings = query.order_by(Booking.check_in.desc()).all()
    
    result = []
    for b in bookings:
        # Get access code
        access_code = db.query(AccessCode).filter(
            AccessCode.booking_id == b.id
        ).first()
        
        result.append({
            "id": b.id,
            "intId": hash(b.id) % 10000,  # For UI display
            "channexId": b.channex_booking_id,
            "guest": b.guest_name or "Unknown",
            "nationality": b.guest_nationality or "",
            "room": b.room.room_number if b.room else "",
            "checkin": b.check_in.isoformat(),
            "checkout": b.check_out.isoformat(),
            "ota": b.ota_source,
            "status": b.status,
            "passcode": access_code.passcode if access_code else None,
            "totalAmount": 0
        })
    
    return result


@router.get("/bookings/today")
def get_today_bookings(db: Session = Depends(get_db)):
    """Get bookings for today."""
    today = date.today()
    
    query = db.query(Booking).options(
        joinedload(Booking.room)
    ).filter(
        or_(
            Booking.check_in == today,
            Booking.check_out == today,
            Booking.status == "checked_in"
        )
    )
    
    bookings = query.all()
    
    result = []
    for b in bookings:
        access_code = db.query(AccessCode).filter(
            AccessCode.booking_id == b.id
        ).first()
        
        result.append({
            "id": b.id,
            "intId": hash(b.id) % 10000,
            "guest": b.guest_name or "Unknown",
            "nationality": b.guest_nationality or "",
            "room": b.room.room_number if b.room else "",
            "ota": b.ota_source,
            "status": b.status,
            "passcode": access_code.passcode if access_code else None
        })
    
    return result


@router.get("/bookings/{booking_id}")
def get_booking(booking_id: str, db: Session = Depends(get_db)):
    """Get single booking with full details."""
    booking = db.query(Booking).options(
        joinedload(Booking.room)
    ).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    access_code = db.query(AccessCode).filter(
        AccessCode.booking_id == booking.id
    ).first()
    
    # Get guest record
    guest = db.query(Guest).filter(Guest.booking_id == booking.id).first()
    
    return {
        "id": booking.id,
        "channexId": booking.channex_booking_id,
        "room": booking.room.room_number if booking.room else "",
        "roomName": booking.room.room_type if booking.room else "",
        "checkin": booking.check_in.isoformat(),
        "checkout": booking.check_out.isoformat(),
        "status": booking.status,
        "ota": booking.ota_source,
        "otaCode": booking.ota_reservation_code,
        "guestsCount": booking.guests_count,
        "guest": {
            "name": booking.guest_name,
            "nationality": booking.guest_nationality,
            "passport": guest.passport_number if guest else "",
            "email": booking.guest_email,
            "phone": booking.guest_phone
        },
        "passcode": access_code.passcode if access_code else None,
        "backupPasscode": access_code.backup_passcode if access_code else None
    }


@router.post("/bookings/{booking_id}/generate-passcode")
def generate_booking_passcode(booking_id: str, db: Session = Depends(get_db)):
    """Generate passcode for a booking."""
    import random
    
    booking = db.query(Booking).options(
        joinedload(Booking.room)
    ).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if passcode already exists
    existing = db.query(AccessCode).filter(
        AccessCode.booking_id == booking_id
    ).first()
    
    if existing:
        return {
            "passcode": existing.passcode,
            "backupPasscode": existing.backup_passcode,
            "message": "Passcode already exists"
        }
    
    # Generate new passcode
    passcode = str(random.randint(100000, 999999))
    backup = str(random.randint(100000, 999999))
    
    access_code = AccessCode(
        booking_id=booking_id,
        passcode=passcode,
        backup_passcode=backup,
        valid_from=datetime.combine(booking.check_in, datetime.min.time().replace(hour=15)),
        valid_to=datetime.combine(booking.check_out, datetime.min.time().replace(hour=11))
    )
    db.add(access_code)
    db.commit()
    
    return {
        "passcode": passcode,
        "backupPasscode": backup,
        "validFrom": access_code.valid_from.isoformat(),
        "validTo": access_code.valid_to.isoformat(),
        "message": "Passcode generated successfully"
    }


@router.put("/bookings/{booking_id}/status")
def update_booking_status(
    booking_id: str, 
    status: str = Query(...),
    db: Session = Depends(get_db)
):
    """Update booking status."""
    booking = db.query(Booking).options(
        joinedload(Booking.room)
    ).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    valid_statuses = ["confirmed", "checked_in", "checked_out", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    old_status = booking.status
    booking.status = status
    
    # Update room status
    if booking.room:
        if status == "checked_in":
            booking.room.status = "occupied"
        elif status in ["checked_out", "cancelled"]:
            booking.room.status = "cleaning"
    
    db.commit()
    
    return {
        "id": booking.id,
        "oldStatus": old_status,
        "newStatus": status,
        "roomStatus": booking.room.status if booking.room else None
    }


# ============== Guests ==============

@router.get("/guests")
def list_guests(
    nationality: Optional[str] = Query(None),
    xnc_status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all guests."""
    query = db.query(Guest).options(joinedload(Guest.booking))
    
    if nationality:
        query = query.filter(Guest.nationality == nationality)
    if xnc_status == "exported":
        query = query.filter(Guest.xnc_exported == True)
    elif xnc_status == "pending":
        query = query.filter(Guest.xnc_exported == False)
    
    guests = query.all()
    
    return [
        {
            "id": g.id,
            "name": g.full_name,
            "nationality": g.nationality,
            "passport": g.passport_number,
            "bookingId": g.booking_id,
            "xncExported": g.xnc_exported
        }
        for g in guests
    ]


@router.get("/guests/pending-xnc")
def get_pending_xnc_guests(db: Session = Depends(get_db)):
    """Get guests pending XNC export."""
    guests = db.query(Guest).options(
        joinedload(Guest.booking)
    ).filter(
        Guest.xnc_exported == False,
        Guest.nationality != "Vietnam"
    ).all()
    
    return [
        {
            "id": g.id,
            "name": g.full_name,
            "nationality": g.nationality,
            "passport": g.passport_number,
            "checkin": g.booking.check_in.isoformat() if g.booking else None,
            "bookingId": g.booking_id
        }
        for g in guests
    ]


@router.post("/guests/mark-exported")
def mark_guests_exported(guest_ids: List[str], db: Session = Depends(get_db)):
    """Mark guests as exported to XNC."""
    updated = db.query(Guest).filter(Guest.id.in_(guest_ids)).update(
        {Guest.xnc_exported: True, Guest.xnc_exported_at: datetime.now()},
        synchronize_session=False
    )
    db.commit()
    
    return {"markedCount": updated}


# ============== Locks ==============

@router.get("/locks")
def list_locks(db: Session = Depends(get_db)):
    """List all locks from rooms."""
    rooms = db.query(Room).filter(Room.ttlock_lock_id.isnot(None)).all()
    
    # Mock lock data - in production this would come from TTLock API
    locks = []
    for idx, r in enumerate(rooms):
        locks.append({
            "id": int(r.ttlock_lock_id) if r.ttlock_lock_id else idx + 10001,
            "name": f"Room {r.room_number} - {r.room_type}",
            "roomId": r.id,
            "battery": 85 - (idx * 5) % 30,
            "online": idx % 3 != 0
        })
    
    return locks
