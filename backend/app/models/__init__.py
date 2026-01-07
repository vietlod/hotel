"""
Hotel PMS - Database Models
SQLAlchemy ORM models for all entities.
"""
import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    String, Text, Boolean, Integer, BigInteger, Date, DateTime,
    ForeignKey, JSON, LargeBinary, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


def generate_uuid() -> str:
    """Generate UUID string."""
    return str(uuid.uuid4())


class Property(Base):
    """Property/Building entity."""
    __tablename__ = "properties"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    district: Mapped[Optional[str]] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100), default="Ho Chi Minh")
    
    # Channel Manager Integration
    channex_property_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    
    # Immigration Registration
    xnc_registration_code: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    rooms: Mapped[List["Room"]] = relationship("Room", back_populates="property")


class Room(Base):
    """Room entity."""
    __tablename__ = "rooms"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    property_id: Mapped[str] = mapped_column(String(36), ForeignKey("properties.id"))
    room_number: Mapped[str] = mapped_column(String(50), nullable=False)
    room_type: Mapped[Optional[str]] = mapped_column(String(100))  # Studio, 1BR, 2BR, etc.
    
    # TTLock Integration
    ttlock_lock_id: Mapped[Optional[str]] = mapped_column(String(100))
    ttlock_gateway_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Status: available, occupied, cleaning, maintenance
    status: Mapped[str] = mapped_column(String(20), default="available")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    property: Mapped["Property"] = relationship("Property", back_populates="rooms")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="room")


class Booking(Base):
    """Booking entity from Channel Manager."""
    __tablename__ = "bookings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    room_id: Mapped[str] = mapped_column(String(36), ForeignKey("rooms.id"))
    
    # Channex Integration
    channex_booking_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    channex_revision_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # OTA Source
    ota_source: Mapped[str] = mapped_column(String(50), nullable=False)  # airbnb, booking, agoda, trip
    ota_reservation_code: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Booking Details
    check_in: Mapped[date] = mapped_column(Date, nullable=False)
    check_out: Mapped[date] = mapped_column(Date, nullable=False)
    nights: Mapped[int] = mapped_column(Integer, default=1)
    guests_count: Mapped[int] = mapped_column(Integer, default=1)
    
    # Primary Guest Info
    guest_name: Mapped[Optional[str]] = mapped_column(String(255))
    guest_email: Mapped[Optional[str]] = mapped_column(String(255))
    guest_phone: Mapped[Optional[str]] = mapped_column(String(50))
    guest_nationality: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Status: pending, confirmed, checked_in, checked_out, cancelled
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    
    # Messages from OTA
    guest_messages: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    room: Mapped["Room"] = relationship("Room", back_populates="bookings")
    guests: Mapped[List["Guest"]] = relationship("Guest", back_populates="booking")
    access_codes: Mapped[List["AccessCode"]] = relationship("AccessCode", back_populates="booking")


class Guest(Base):
    """Guest entity with passport data."""
    __tablename__ = "guests"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    booking_id: Mapped[str] = mapped_column(String(36), ForeignKey("bookings.id"))
    
    # Personal Info
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(10))  # male, female
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    nationality: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Passport Info
    passport_number: Mapped[Optional[str]] = mapped_column(String(50))
    passport_issue_date: Mapped[Optional[date]] = mapped_column(Date)
    passport_expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    passport_issue_country: Mapped[Optional[str]] = mapped_column(String(100))
    passport_image_path: Mapped[Optional[str]] = mapped_column(Text)
    
    # MRZ Data (Machine Readable Zone)
    mrz_line1: Mapped[Optional[str]] = mapped_column(String(50))
    mrz_line2: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Processing Status
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    ocr_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # XNC Export Status
    xnc_exported: Mapped[bool] = mapped_column(Boolean, default=False)
    xnc_exported_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="guests")


class AccessCode(Base):
    """Smart Lock Access Code entity."""
    __tablename__ = "access_codes"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    booking_id: Mapped[str] = mapped_column(String(36), ForeignKey("bookings.id"))
    
    # TTLock Integration
    ttlock_passcode_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    ttlock_backup_passcode_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    
    # Passcodes
    passcode: Mapped[str] = mapped_column(String(20), nullable=False)
    backup_passcode: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Validity
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valid_to: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Delivery Status
    sent_to_guest: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sent_via: Mapped[Optional[str]] = mapped_column(String(50))  # channex, email, sms
    
    # Usage
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="access_codes")


class Staff(Base):
    """Staff/User entity."""
    __tablename__ = "staff"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Role: admin, owner, housekeeping, maintenance
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Telegram Integration
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)


class HousekeepingLog(Base):
    """Housekeeping activity log."""
    __tablename__ = "housekeeping_logs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    room_id: Mapped[str] = mapped_column(String(36), ForeignKey("rooms.id"))
    staff_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("staff.id"))
    
    # Status: dirty, cleaning, clean, inspected
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class MaintenanceIssue(Base):
    """Maintenance issue tracking."""
    __tablename__ = "maintenance_issues"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    room_id: Mapped[str] = mapped_column(String(36), ForeignKey("rooms.id"))
    reported_by_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("staff.id"))
    
    # Issue Details
    issue_type: Mapped[str] = mapped_column(String(50))  # missing_item, damage, repair_needed
    severity: Mapped[str] = mapped_column(String(20))  # low, medium, high, urgent
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Images (stored as paths or URLs)
    images: Mapped[Optional[list]] = mapped_column(JSON)
    
    # Resolution
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    resolved_by_id: Mapped[Optional[str]] = mapped_column(String(36))
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Notification
    notified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
