"""
Hotel PMS - Demo Script
Test the complete booking flow with mock services.

Usage:
    cd d:\HOTEL\backend
    python -m app.demo
"""
import asyncio
from datetime import date, datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.mock_services import mock_channex_service, mock_ttlock_service
from app.services.xnc_service import xnc_service
from app.schemas import XNCGuestData


async def demo_booking_flow():
    """
    Demonstrate the complete booking flow:
    1. New booking received from Channex
    2. Passcode generated via TTLock
    3. Passcode sent to guest
    4. XNC report generated
    """
    print("=" * 60)
    print("🏨 HOTEL PMS - DEMO BOOKING FLOW")
    print("=" * 60)
    print()
    
    # Step 1: Get new bookings from Channex (mock)
    print("📥 Step 1: Fetching new bookings from Channex...")
    print("-" * 40)
    
    bookings = await mock_channex_service.get_feed()
    print(f"Found {len(bookings)} new bookings:")
    
    for booking in bookings[:3]:  # Show first 3
        guest = booking.get("guest", {})
        print(f"""
  📋 Booking: {booking['id']}
     OTA: {booking['ota_name']}
     Guest: {guest.get('name', 'N/A')}
     Nationality: {guest.get('nationality', 'N/A')}
     Check-in: {booking['arrival_date']}
     Check-out: {booking['departure_date']}
""")
    
    # Step 2: Generate passcodes for each booking
    print("\n🔐 Step 2: Generating passcodes via TTLock...")
    print("-" * 40)
    
    locks = await mock_ttlock_service.get_locks()
    print(f"Available locks: {len(locks)}")
    
    passcode_results = []
    for i, booking in enumerate(bookings[:3]):
        lock = locks[i % len(locks)]
        guest = booking.get("guest", {})
        
        check_in = datetime.strptime(booking['arrival_date'], "%Y-%m-%d").replace(hour=15)
        check_out = datetime.strptime(booking['departure_date'], "%Y-%m-%d").replace(hour=11)
        
        passcode_data = await mock_ttlock_service.create_booking_passcode(
            lock_id=lock['lockId'],
            guest_name=guest.get('name', 'Guest'),
            check_in=check_in,
            check_out=check_out
        )
        
        passcode_results.append({
            "booking": booking,
            "lock": lock,
            "passcode": passcode_data
        })
        
        print(f"""
  🔑 Lock: {lock['lockName']}
     Guest: {guest.get('name')}
     Passcode: {passcode_data['passcode']}
     Backup: {passcode_data['backup_passcode']}
     Valid: {check_in.strftime('%Y-%m-%d %H:%M')} - {check_out.strftime('%Y-%m-%d %H:%M')}
""")
    
    # Step 3: Send passcode messages to guests
    print("\n📨 Step 3: Sending passcode messages to guests...")
    print("-" * 40)
    
    for result in passcode_results:
        booking = result['booking']
        passcode = result['passcode']
        guest = booking.get('guest', {})
        
        message = await mock_channex_service.send_passcode_message(
            booking_id=booking['id'],
            guest_name=guest.get('name', 'Guest'),
            check_in_date=datetime.strptime(booking['arrival_date'], "%Y-%m-%d").date(),
            check_out_date=datetime.strptime(booking['departure_date'], "%Y-%m-%d").date(),
            passcode=passcode['passcode'],
            property_address="123 Nguyen Hue, District 1, Ho Chi Minh City",
            wifi_name="Sunrise_Guest",
            wifi_password="Welcome2025"
        )
        
        print(f"  ✅ Sent to: {guest.get('name')} ({booking['id']})")
    
    # Step 4: Acknowledge bookings
    print("\n✓ Step 4: Acknowledging bookings...")
    print("-" * 40)
    
    for booking in bookings[:3]:
        await mock_channex_service.acknowledge_booking_revision(booking['revision_id'])
        print(f"  ✓ Acknowledged: {booking['id']}")
    
    # Step 5: Generate XNC Report
    print("\n📋 Step 5: Generating XNC Report (NA17 format)...")
    print("-" * 40)
    
    # Create guest data for XNC report
    xnc_guests = []
    for booking in bookings[:3]:
        guest = booking.get('guest', {})
        if guest.get('nationality') and guest.get('nationality') != 'Vietnam':
            xnc_guests.append(XNCGuestData(
                full_name=guest.get('name', 'Unknown'),
                gender="male",  # Would come from passport OCR
                date_of_birth=date(1990, 1, 15),  # Would come from passport OCR
                nationality=guest.get('nationality', 'Unknown'),
                passport_number="AB1234567",  # Would come from passport OCR
                passport_issue_date=date(2020, 1, 1),
                passport_expiry_date=date(2030, 1, 1),
                passport_issue_country=guest.get('nationality', 'Unknown'),
                temporary_address="123 Nguyen Hue, District 1, Ho Chi Minh City",
                arrival_date=datetime.strptime(booking['arrival_date'], "%Y-%m-%d").date(),
                departure_date=datetime.strptime(booking['departure_date'], "%Y-%m-%d").date()
            ))
    
    # Generate reports in multiple formats
    today = date.today()
    
    csv_path = xnc_service.generate_na17_csv(
        guests=xnc_guests,
        property_name="Sunrise Apartment",
        property_address="123 Nguyen Hue, District 1, Ho Chi Minh City",
        property_phone="0901234567",
        recipient_authority="Công an Phường Bến Nghé, Quận 1, TP.HCM",
        report_date=today
    )
    print(f"  📄 CSV Report: {csv_path}")
    
    xml_path = xnc_service.generate_na17_xml(
        guests=xnc_guests,
        property_name="Sunrise Apartment",
        property_address="123 Nguyen Hue, District 1, Ho Chi Minh City",
        property_phone="0901234567",
        recipient_authority="Công an Phường Bến Nghé, Quận 1, TP.HCM",
        report_date=today
    )
    print(f"  📄 XML Report: {xml_path}")
    
    txt_path = xnc_service.generate_na17_printable(
        guests=xnc_guests,
        property_name="Sunrise Apartment",
        property_address="123 Nguyen Hue, District 1, Ho Chi Minh City",
        property_phone="0901234567",
        recipient_authority="Công an Phường Bến Nghé, Quận 1, TP.HCM",
        report_date=today
    )
    print(f"  📄 Printable: {txt_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETE!")
    print("=" * 60)
    print(f"""
Summary:
  - Processed {len(bookings[:3])} bookings
  - Generated {len(passcode_results)} passcodes
  - Sent {len(passcode_results)} guest messages
  - Created XNC report with {len(xnc_guests)} foreign guests

Generated files are in:
  d:\\HOTEL\\backend\\exports\\xnc\\
""")


async def demo_simulate_new_booking():
    """Simulate receiving a new booking webhook."""
    print("\n" + "=" * 60)
    print("🎲 SIMULATING NEW BOOKING")
    print("=" * 60)
    
    new_booking = mock_channex_service.simulate_new_booking()
    guest = new_booking.get('guest', {})
    
    print(f"""
New booking created:
  - Booking ID: {new_booking['id']}
  - OTA: {new_booking['ota_name']}
  - Guest: {guest.get('name')}
  - Check-in: {new_booking['arrival_date']}
  - Check-out: {new_booking['departure_date']}

This would trigger:
  1. Webhook POST to /api/v1/webhooks/channex
  2. Background task to process booking
  3. Passcode generation
  4. Message sent to guest
  5. Admin notification via Telegram
""")
    
    return new_booking


async def demo_list_locks():
    """List available TTLock locks."""
    print("\n" + "=" * 60)
    print("🔐 TTLOCK LOCKS")
    print("=" * 60)
    
    locks = await mock_ttlock_service.get_locks()
    gateways = await mock_ttlock_service.get_gateways()
    
    print(f"\nGateways ({len(gateways)}):")
    for gw in gateways:
        print(f"  - {gw['gatewayName']} (ID: {gw['gatewayId']}, Online: {gw['isOnline']})")
    
    print(f"\nLocks ({len(locks)}):")
    for lock in locks:
        print(f"  - {lock['lockName']} (ID: {lock['lockId']}, Battery: {lock['electricQuantity']}%)")
    
    return locks


async def main():
    """Run all demos."""
    print("\n" + "🏨 " * 20)
    print("\n      HOTEL PMS - PROPERTY MANAGEMENT SYSTEM DEMO\n")
    print("🏨 " * 20 + "\n")
    
    # Show available locks
    await demo_list_locks()
    
    # Run main booking flow demo
    await demo_booking_flow()
    
    # Simulate a new booking
    await demo_simulate_new_booking()
    
    print("\n✨ All demos completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
