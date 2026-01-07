"""
Hotel PMS - Passport OCR API Routes
Upload and OCR passport images to auto-fill guest information.
"""
import os
import shutil
from typing import Optional
from datetime import date
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from app.database import get_db
from app.models import Guest, Booking
from app.services.passport_ocr_service import passport_ocr_service, MRZParser, PassportData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/passport", tags=["Passport OCR"])


class MRZInput(BaseModel):
    """Manual MRZ input."""
    mrz_line1: str
    mrz_line2: str


class PassportDataResponse(BaseModel):
    """Passport data API response."""
    success: bool
    full_name: Optional[str] = None
    surname: Optional[str] = None
    given_names: Optional[str] = None
    passport_number: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    expiry_date: Optional[str] = None
    issuing_country: Optional[str] = None
    confidence: float = 0.0
    message: Optional[str] = None


def passport_data_to_response(data: PassportData) -> PassportDataResponse:
    """Convert PassportData to API response."""
    return PassportDataResponse(
        success=True,
        full_name=data.full_name,
        surname=data.surname,
        given_names=data.given_names,
        passport_number=data.passport_number,
        nationality=data.nationality,
        date_of_birth=data.date_of_birth.isoformat() if data.date_of_birth else None,
        gender=data.gender,
        expiry_date=data.expiry_date.isoformat() if data.expiry_date else None,
        issuing_country=data.issuing_country,
        confidence=data.confidence,
        message="Passport data extracted successfully"
    )


@router.post("/upload", response_model=PassportDataResponse)
async def upload_passport_image(
    booking_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload passport image and extract guest information via OCR.
    
    Supports: JPEG, PNG, WEBP images
    
    Returns extracted passport data including:
    - Full name
    - Passport number
    - Nationality
    - Date of birth
    - Gender
    - Expiry date
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {allowed_types}"
        )
    
    # Validate file size (max 10MB)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size: 10MB"
        )
    
    try:
        # Save the file
        file_path = passport_ocr_service.save_passport_image(
            booking_id, content, file.filename
        )
        
        # Extract passport data
        passport_data = await passport_ocr_service.extract_from_image(file_path)
        
        if passport_data:
            logger.info(f"Passport extracted for booking {booking_id}: {passport_data.full_name}")
            return passport_data_to_response(passport_data)
        else:
            return PassportDataResponse(
                success=False,
                confidence=0.0,
                message="Could not extract passport data. Please try with a clearer image or enter MRZ manually."
            )
            
    except Exception as e:
        logger.error(f"Passport OCR error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse-mrz", response_model=PassportDataResponse)
async def parse_mrz_manual(mrz_input: MRZInput):
    """
    Parse manually entered MRZ lines.
    
    Use this when OCR fails or for manual data entry.
    
    MRZ Format (TD3 - Passport):
    - Line 1 (44 chars): P<COUNTRY<SURNAME<<GIVEN_NAMES<<<...
    - Line 2 (44 chars): PASSPORT_NUM<CHECK<NATIONALITY<DOB<CHECK<GENDER<EXPIRY<CHECK...
    
    Example:
    ```
    P<USASMITH<<JOHN<WILLIAM<<<<<<<<<<<<<<<<<<<<<
    AB12345671USA9001011M3012315<<<<<<<<<<<<<<02
    ```
    """
    # Validate input length
    if len(mrz_input.mrz_line1) < 30 or len(mrz_input.mrz_line2) < 30:
        raise HTTPException(
            status_code=400,
            detail="MRZ lines too short. Each line should be 44 characters."
        )
    
    passport_data = passport_ocr_service.parse_mrz_manual(
        mrz_input.mrz_line1,
        mrz_input.mrz_line2
    )
    
    if passport_data:
        return passport_data_to_response(passport_data)
    else:
        return PassportDataResponse(
            success=False,
            confidence=0.0,
            message="Could not parse MRZ. Please check the format."
        )


@router.post("/apply-to-guest/{booking_id}")
async def apply_passport_to_guest(
    booking_id: str,
    passport_data: PassportDataResponse,
    db: Session = Depends(get_db)
):
    """
    Apply extracted passport data to a guest record.
    
    This updates the guest information in the database
    with the data extracted from the passport.
    """
    # Find the booking
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Find or create guest
    guest = db.query(Guest).filter(
        Guest.booking_id == booking_id,
        Guest.is_primary == True
    ).first()
    
    if not guest:
        # Create new guest
        guest = Guest(
            booking_id=booking_id,
            is_primary=True,
            full_name=passport_data.full_name or "Unknown"
        )
        db.add(guest)
    
    # Update guest with passport data
    if passport_data.full_name:
        guest.full_name = passport_data.full_name
    if passport_data.passport_number:
        guest.passport_number = passport_data.passport_number
    if passport_data.nationality:
        guest.nationality = passport_data.nationality
    if passport_data.date_of_birth:
        guest.date_of_birth = date.fromisoformat(passport_data.date_of_birth)
    if passport_data.gender:
        guest.gender = passport_data.gender
    if passport_data.expiry_date:
        guest.passport_expiry_date = date.fromisoformat(passport_data.expiry_date)
    if passport_data.issuing_country:
        guest.passport_issue_country = passport_data.issuing_country
    
    guest.ocr_verified = True
    
    # Also update booking guest info
    if passport_data.full_name:
        booking.guest_name = passport_data.full_name
    if passport_data.nationality:
        booking.guest_nationality = passport_data.nationality
    
    db.commit()
    
    return {
        "success": True,
        "guest_id": guest.id,
        "message": f"Guest {guest.full_name} updated with passport data"
    }


@router.get("/demo")
async def demo_mrz_parsing():
    """
    Demo endpoint showing MRZ parsing with sample data.
    
    Use this to test the MRZ parser without uploading an image.
    """
    sample_mrz1 = "P<USASMITH<<JOHN<WILLIAM<<<<<<<<<<<<<<<<<<<<<<"
    sample_mrz2 = "AB12345671USA9001011M3012315<<<<<<<<<<<<<<02"
    
    passport_data = MRZParser.parse(f"{sample_mrz1}\n{sample_mrz2}")
    
    if passport_data:
        return {
            "input": {
                "line1": sample_mrz1,
                "line2": sample_mrz2
            },
            "output": passport_data_to_response(passport_data),
            "explanation": {
                "line1_format": "P<ISSUING_COUNTRY<SURNAME<<GIVEN_NAMES<<<...",
                "line2_format": "PASSPORT_NO<CHECK<NATIONALITY<DOB<CHECK<GENDER<EXPIRY<CHECK..."
            }
        }
    else:
        return {"error": "Demo parsing failed"}


@router.get("/countries")
async def list_supported_countries():
    """List supported country codes for passport parsing."""
    return {
        "countries": MRZParser.COUNTRY_CODES,
        "note": "Country codes follow ISO 3166-1 alpha-3 standard"
    }
