"""
Hotel PMS - Pydantic Schemas
Request/Response models for API endpoints.
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ============== Property Schemas ==============

class PropertyBase(BaseModel):
    """Base property schema."""
    name: str
    address: str
    district: Optional[str] = None
    city: str = "Ho Chi Minh"


class PropertyCreate(PropertyBase):
    """Create property request."""
    channex_property_id: Optional[str] = None
    xnc_registration_code: Optional[str] = None


class PropertyResponse(PropertyBase):
    """Property response."""
    id: str
    channex_property_id: Optional[str] = None
    xnc_registration_code: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== Room Schemas ==============

class RoomBase(BaseModel):
    """Base room schema."""
    room_number: str
    room_type: Optional[str] = None


class RoomCreate(RoomBase):
    """Create room request."""
    property_id: str
    ttlock_lock_id: Optional[str] = None
    ttlock_gateway_id: Optional[str] = None


class RoomResponse(RoomBase):
    """Room response."""
    id: str
    property_id: str
    ttlock_lock_id: Optional[str] = None
    status: str
    
    class Config:
        from_attributes = True


# ============== Booking Schemas ==============

class BookingBase(BaseModel):
    """Base booking schema."""
    check_in: date
    check_out: date
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None


class BookingCreate(BookingBase):
    """Create booking request (manual)."""
    room_id: str
    ota_source: str = "direct"
    guests_count: int = 1


class BookingFromChannex(BaseModel):
    """Booking data from Channex webhook."""
    channex_booking_id: str
    channex_revision_id: Optional[str] = None
    property_id: str
    room_type_id: Optional[str] = None
    arrival_date: date
    departure_date: date
    status: str
    ota_name: str
    ota_reservation_code: Optional[str] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None
    guest_nationality: Optional[str] = None
    guests_count: int = 1


class BookingResponse(BookingBase):
    """Booking response."""
    id: str
    room_id: str
    channex_booking_id: Optional[str] = None
    ota_source: str
    ota_reservation_code: Optional[str] = None
    nights: int
    guests_count: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BookingDetail(BookingResponse):
    """Booking detail with related data."""
    guests: List["GuestResponse"] = []
    access_codes: List["AccessCodeResponse"] = []


# ============== Guest Schemas ==============

class GuestBase(BaseModel):
    """Base guest schema."""
    full_name: str
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None


class GuestCreate(GuestBase):
    """Create guest request."""
    booking_id: str
    passport_number: Optional[str] = None
    passport_issue_date: Optional[date] = None
    passport_expiry_date: Optional[date] = None
    passport_issue_country: Optional[str] = None
    is_primary: bool = False


class GuestResponse(GuestBase):
    """Guest response."""
    id: str
    booking_id: str
    passport_number: Optional[str] = None
    is_primary: bool
    ocr_verified: bool
    xnc_exported: bool
    
    class Config:
        from_attributes = True


class GuestPassportData(BaseModel):
    """Passport OCR extraction result."""
    full_name: str
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    passport_number: str
    passport_issue_date: Optional[date] = None
    passport_expiry_date: Optional[date] = None
    passport_issue_country: Optional[str] = None
    mrz_line1: Optional[str] = None
    mrz_line2: Optional[str] = None


# ============== Access Code Schemas ==============

class AccessCodeBase(BaseModel):
    """Base access code schema."""
    valid_from: datetime
    valid_to: datetime


class AccessCodeCreate(AccessCodeBase):
    """Create access code request."""
    booking_id: str


class AccessCodeResponse(AccessCodeBase):
    """Access code response."""
    id: str
    booking_id: str
    passcode: str
    backup_passcode: Optional[str] = None
    sent_to_guest: bool
    sent_at: Optional[datetime] = None
    usage_count: int
    
    class Config:
        from_attributes = True


# ============== Channex Webhook Schemas ==============

class ChannexWebhookPayload(BaseModel):
    """Channex webhook payload."""
    event: str
    property_id: str
    booking_id: Optional[str] = None
    payload: dict


class ChannexBookingEvent(BaseModel):
    """Channex booking event data."""
    id: str
    property_id: str
    room_type_id: Optional[str] = None
    arrival_date: str
    departure_date: str
    status: str
    guest: Optional[dict] = None
    ota_name: str
    ota_reservation_code: Optional[str] = None


# ============== XNC Report Schemas ==============

class XNCGuestData(BaseModel):
    """Guest data for XNC XML export."""
    full_name: str
    gender: str
    date_of_birth: date
    nationality: str
    passport_number: str
    passport_issue_date: Optional[date] = None
    passport_expiry_date: Optional[date] = None
    passport_issue_country: Optional[str] = None
    temporary_address: str
    arrival_date: date
    departure_date: date


class XNCReportRequest(BaseModel):
    """XNC report generation request."""
    report_date: date
    property_id: Optional[str] = None


class XNCReportResponse(BaseModel):
    """XNC report generation response."""
    report_date: date
    guests_count: int
    file_path: str
    file_format: str  # xml, excel


# ============== Telegram Notification Schemas ==============

class TelegramNotification(BaseModel):
    """Telegram notification payload."""
    channel: str  # admin, housekeeping, maintenance
    message: str
    images: Optional[List[str]] = None


# ============== Health Check ==============

class HealthCheck(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    environment: str
    database: str = "connected"
    channex: str = "unknown"
    ttlock: str = "unknown"
    telegram: str = "unknown"


# Update forward references
BookingDetail.model_rebuild()
