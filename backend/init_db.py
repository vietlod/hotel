"""
Hotel PMS - Database Initialization Script
Creates database and runs initial migrations.

Usage:
    python init_db.py
"""
import os
import sys
from datetime import date, datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use SQLite for simplicity
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hotel_pms.db")

def init_database():
    """Initialize database with tables and sample data."""
    print("🗄️ Initializing Hotel PMS Database...")
    print(f"   Database: {DATABASE_URL}")
    print()
    
    # Import models to register them
    from app.database import Base
    from app.models import Property, Room, Booking, Guest, AccessCode, Staff
    
    # Create engine
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )
    
    # Create all tables
    print("📋 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("   ✓ Tables created")
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(Property).first()
        if existing:
            print("\n⚠️  Sample data already exists. Skipping seed.")
            return
        
        print("\n🌱 Seeding sample data...")
        
        # Create Property (matching actual model fields)
        property1 = Property(
            name="Sunrise Apartment",
            address="123 Nguyen Hue, District 1, Ho Chi Minh City",
            district="District 1",
            city="Ho Chi Minh",
            channex_property_id="channex_prop_001",
            xnc_registration_code="XNC2026001"
        )
        db.add(property1)
        db.flush()
        print(f"   ✓ Property: {property1.name} (ID: {property1.id[:8]}...)")
        
        # Create Rooms (matching actual model fields)
        rooms_data = [
            {"number": "101", "type": "studio", "lock_id": "10001"},
            {"number": "102", "type": "studio", "lock_id": "10002"},
            {"number": "201", "type": "1br", "lock_id": "10003"},
            {"number": "202", "type": "1br", "lock_id": "10004"},
            {"number": "301", "type": "2br", "lock_id": "10005"},
            {"number": "302", "type": "2br", "lock_id": "10006"},
        ]
        
        rooms = []
        for rd in rooms_data:
            room = Room(
                property_id=property1.id,
                room_number=rd["number"],
                room_type=rd["type"],
                ttlock_lock_id=rd["lock_id"],
                status="available"
            )
            db.add(room)
            rooms.append(room)
        db.flush()
        print(f"   ✓ Rooms: {len(rooms)} rooms created")
        
        # Create Sample Bookings
        today = date.today()
        bookings_data = [
            {
                "room_idx": 0,
                "guest_name": "John Smith",
                "nationality": "United States",
                "email": "john.smith@example.com",
                "phone": "+1234567890",
                "check_in": today + timedelta(days=1),
                "check_out": today + timedelta(days=4),
                "ota": "airbnb",
                "status": "confirmed",
                "passcode": "123456"
            },
            {
                "room_idx": 1,
                "guest_name": "Marie Dupont",
                "nationality": "France",
                "email": "marie.dupont@example.fr",
                "phone": "+33612345678",
                "check_in": today + timedelta(days=2),
                "check_out": today + timedelta(days=5),
                "ota": "booking",
                "status": "confirmed",
                "passcode": "654321"
            },
            {
                "room_idx": 2,
                "guest_name": "Tanaka Yuki",
                "nationality": "Japan",
                "email": "tanaka.yuki@example.jp",
                "phone": "+81901234567",
                "check_in": today,
                "check_out": today + timedelta(days=3),
                "ota": "agoda",
                "status": "checked_in",
                "passcode": "789012"
            },
            {
                "room_idx": 3,
                "guest_name": "Hans Mueller",
                "nationality": "Germany",
                "email": "hans@example.de",
                "phone": "+49123456789",
                "check_in": today + timedelta(days=3),
                "check_out": today + timedelta(days=7),
                "ota": "trip",
                "status": "confirmed",
                "passcode": None
            },
            {
                "room_idx": 4,
                "guest_name": "Kim Min-jun",
                "nationality": "South Korea",
                "email": "kim.minjun@example.kr",
                "phone": "+821012345678",
                "check_in": today,
                "check_out": today + timedelta(days=2),
                "ota": "airbnb",
                "status": "checked_in",
                "passcode": "456789"
            },
        ]
        
        for idx, bd in enumerate(bookings_data):
            room = rooms[bd["room_idx"]]
            nights = (bd["check_out"] - bd["check_in"]).days
            
            # Create Booking
            booking = Booking(
                room_id=room.id,
                channex_booking_id=f"channex_{idx+1:03d}",
                channex_revision_id=f"rev_{idx+1:03d}",
                ota_source=bd["ota"],
                ota_reservation_code=f"OTA{idx+10000:06d}",
                check_in=bd["check_in"],
                check_out=bd["check_out"],
                nights=nights,
                guests_count=1,
                guest_name=bd["guest_name"],
                guest_email=bd["email"],
                guest_phone=bd["phone"],
                guest_nationality=bd["nationality"],
                status=bd["status"]
            )
            db.add(booking)
            db.flush()
            
            # Create Guest record
            guest = Guest(
                booking_id=booking.id,
                full_name=bd["guest_name"],
                gender="male",
                date_of_birth=date(1990, 1, 15),
                nationality=bd["nationality"],
                passport_number=f"XX{(idx+1)*1111111:07d}",
                is_primary=True,
                xnc_exported=False
            )
            db.add(guest)
            
            # Update room status if checked in
            if bd["status"] == "checked_in":
                room.status = "occupied"
            
            # Create AccessCode if passcode exists
            if bd["passcode"]:
                access_code = AccessCode(
                    booking_id=booking.id,
                    passcode=bd["passcode"],
                    backup_passcode=str(int(bd["passcode"]) + 111111),
                    valid_from=datetime.combine(bd["check_in"], datetime.min.time().replace(hour=15)),
                    valid_to=datetime.combine(bd["check_out"], datetime.min.time().replace(hour=11)),
                    sent_to_guest=True,
                    sent_via="channex"
                )
                db.add(access_code)
        
        db.commit()
        print(f"   ✓ Bookings: {len(bookings_data)} bookings created")
        print(f"   ✓ Guests: {len(bookings_data)} guests created")
        print(f"   ✓ Access Codes: {sum(1 for b in bookings_data if b['passcode'])} codes created")
        
        # Create Staff
        staff_admin = Staff(
            email="admin@sunrise-apt.vn",
            full_name="Admin",
            role="owner",
            telegram_chat_id="123456789",
            is_active=True
        )
        db.add(staff_admin)
        
        # Housekeeping staff
        staff_maria = Staff(
            email="maria@sunrise-apt.vn",
            full_name="Maria Nguyen",
            role="housekeeping",
            is_active=True
        )
        db.add(staff_maria)
        
        staff_john = Staff(
            email="john@sunrise-apt.vn",
            full_name="John Tran",
            role="housekeeping",
            is_active=True
        )
        db.add(staff_john)
        
        # Maintenance staff
        staff_pedro = Staff(
            email="pedro@sunrise-apt.vn",
            full_name="Pedro Le",
            role="maintenance",
            is_active=True
        )
        db.add(staff_pedro)
        
        db.commit()
        print(f"   ✓ Staff: 4 staff accounts created (1 admin, 2 housekeeping, 1 maintenance)")
        
        print("\n✅ Database initialized successfully!")
        print(f"\n📊 Summary:")
        print(f"   • 1 Property")
        print(f"   • {len(rooms)} Rooms")
        print(f"   • {len(bookings_data)} Bookings")
        print(f"   • {len(bookings_data)} Guests")
        print(f"   • 4 Staff accounts")
        print(f"\n📂 Database file: hotel_pms.db")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
