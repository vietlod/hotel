"""
Hotel PMS - Reports API Routes
XNC immigration reports and other exports.
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import logging

from app.schemas import XNCReportRequest, XNCReportResponse, XNCGuestData
from app.services import xnc_service, telegram_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports")


@router.post("/xnc/generate", response_model=XNCReportResponse)
async def generate_xnc_report(
    report_date: date = Query(..., description="Report date"),
    property_id: Optional[str] = Query(None, description="Filter by property"),
    format: str = Query("xml", description="Output format: xml or csv")
):
    """
    Generate XNC (Immigration) report for a specific date.
    
    Collects all foreign guests with check-in on the specified date
    and generates XML/CSV file for upload to xuatnhapcanh.gov.vn
    """
    try:
        # TODO: Query guests from database
        # guests = db.query(Guest).join(Booking).filter(
        #     Booking.check_in == report_date,
        #     Guest.nationality != "Vietnam"
        # ).all()
        
        # For demo, use mock data
        mock_guests = [
            XNCGuestData(
                full_name="John Doe",
                gender="male",
                date_of_birth=date(1990, 5, 15),
                nationality="United States",
                passport_number="US12345678",
                passport_issue_date=date(2020, 1, 1),
                passport_expiry_date=date(2030, 1, 1),
                passport_issue_country="USA",
                temporary_address="123 Nguyen Hue, District 1, Ho Chi Minh City",
                arrival_date=report_date,
                departure_date=date(2026, 1, 10)
            )
        ]
        
        # Generate report
        if format == "csv":
            file_path = xnc_service.generate_csv(
                guests=mock_guests,
                property_name="Demo Property",
                property_address="123 Demo Street",
                report_date=report_date
            )
            file_format = "csv"
        else:
            file_path = xnc_service.generate_xml(
                guests=mock_guests,
                property_name="Demo Property",
                property_address="123 Demo Street",
                property_phone="0901234567",
                report_date=report_date
            )
            file_format = "xml"
        
        # Notify admin
        await telegram_service.notify_xnc_report(
            report_date=str(report_date),
            guests_count=len(mock_guests),
            file_path=file_path,
            status="Generated successfully"
        )
        
        return XNCReportResponse(
            report_date=report_date,
            guests_count=len(mock_guests),
            file_path=file_path,
            file_format=file_format
        )
        
    except Exception as e:
        logger.error(f"Error generating XNC report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/xnc/download/{filename}")
async def download_xnc_report(filename: str):
    """
    Download a generated XNC report file.
    """
    import os
    
    file_path = os.path.join(
        os.path.dirname(__file__), 
        "..", "..", "exports", "xnc", 
        filename
    )
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


@router.get("/xnc/pending")
async def get_pending_xnc_guests(
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None)
):
    """
    Get list of foreign guests pending XNC report.
    
    These are guests who have checked in but haven't been
    exported to the XNC portal yet.
    """
    # TODO: Query from database where xnc_exported = False
    return {"pending_guests": [], "count": 0}


@router.post("/xnc/mark-exported")
async def mark_guests_exported(guest_ids: list[str]):
    """
    Mark guests as exported to XNC portal.
    
    Call this after successfully uploading to the portal.
    """
    # TODO: Update guests in database
    return {"marked": len(guest_ids)}


# ============== Booking/Revenue Reports ==============

@router.get("/bookings/summary")
async def get_bookings_summary(
    from_date: date = Query(...),
    to_date: date = Query(...),
    property_id: Optional[str] = Query(None)
):
    """
    Get booking summary for a date range.
    """
    # TODO: Aggregate bookings from database
    return {
        "from_date": from_date,
        "to_date": to_date,
        "total_bookings": 0,
        "total_nights": 0,
        "by_source": {},
        "by_status": {}
    }


@router.get("/occupancy")
async def get_occupancy_report(
    from_date: date = Query(...),
    to_date: date = Query(...),
    property_id: Optional[str] = Query(None)
):
    """
    Get occupancy rate report.
    """
    # TODO: Calculate from bookings
    return {
        "from_date": from_date,
        "to_date": to_date,
        "total_rooms": 0,
        "occupied_nights": 0,
        "occupancy_rate": 0.0
    }
