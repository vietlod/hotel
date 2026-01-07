"""
Hotel PMS - Standalone Demo Script
Test the complete booking flow with mock services.
No external dependencies required.

Usage:
    cd d:\HOTEL\backend
    python standalone_demo.py
"""
import asyncio
import random
import string
import os
import csv
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
from dataclasses import dataclass


# ============== Data Classes ==============

@dataclass
class XNCGuestData:
    full_name: str
    gender: str
    date_of_birth: date
    nationality: str
    passport_number: str
    temporary_address: str
    arrival_date: date
    departure_date: date
    passport_issue_date: Optional[date] = None
    passport_expiry_date: Optional[date] = None
    passport_issue_country: Optional[str] = None


# ============== Mock Channex Service ==============

class MockChannexService:
    def __init__(self):
        self._bookings: Dict[str, dict] = {}
        self._messages: Dict[str, List[dict]] = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        sample_bookings = [
            {
                "id": "channex_booking_001",
                "property_id": "prop_sunrise_apt",
                "arrival_date": (date.today() + timedelta(days=1)).isoformat(),
                "departure_date": (date.today() + timedelta(days=4)).isoformat(),
                "status": "confirmed",
                "ota_name": "Airbnb",
                "ota_reservation_code": "HMABCDEF123",
                "guest": {
                    "name": "John Smith",
                    "email": "john.smith@example.com",
                    "phone": "+1234567890",
                    "nationality": "United States"
                },
                "revision_id": "rev_001"
            },
            {
                "id": "channex_booking_002",
                "property_id": "prop_sunrise_apt",
                "arrival_date": (date.today() + timedelta(days=2)).isoformat(),
                "departure_date": (date.today() + timedelta(days=5)).isoformat(),
                "status": "confirmed",
                "ota_name": "Booking.com",
                "ota_reservation_code": "4567890123",
                "guest": {
                    "name": "Marie Dupont",
                    "email": "marie.dupont@example.fr",
                    "phone": "+33612345678",
                    "nationality": "France"
                },
                "revision_id": "rev_002"
            },
            {
                "id": "channex_booking_003",
                "property_id": "prop_sunrise_apt",
                "arrival_date": date.today().isoformat(),
                "departure_date": (date.today() + timedelta(days=3)).isoformat(),
                "status": "confirmed",
                "ota_name": "Agoda",
                "ota_reservation_code": "AGD789012",
                "guest": {
                    "name": "Tanaka Yuki",
                    "email": "tanaka.yuki@example.jp",
                    "phone": "+81901234567",
                    "nationality": "Japan"
                },
                "revision_id": "rev_003"
            }
        ]
        for b in sample_bookings:
            self._bookings[b["id"]] = b
    
    async def get_feed(self) -> List[dict]:
        return [b for b in self._bookings.values() if not b.get("acknowledged")]
    
    async def acknowledge_booking_revision(self, revision_id: str) -> bool:
        for b in self._bookings.values():
            if b.get("revision_id") == revision_id:
                b["acknowledged"] = True
                return True
        return False
    
    async def send_passcode_message(self, booking_id, guest_name, check_in_date, 
                                    check_out_date, passcode, property_address,
                                    wifi_name=None, wifi_password=None) -> dict:
        msg = {
            "id": f"msg_{booking_id}",
            "booking_id": booking_id,
            "sent_at": datetime.now().isoformat()
        }
        print(f"    [MOCK] 📨 Sent passcode {passcode} to {guest_name}")
        return msg


# ============== Mock TTLock Service ==============

class MockTTLockService:
    def __init__(self):
        self._locks = [
            {"lockId": 10001, "lockName": "Room 101 - Studio A", "electricQuantity": 85},
            {"lockId": 10002, "lockName": "Room 102 - Studio B", "electricQuantity": 90},
            {"lockId": 10003, "lockName": "Room 201 - 1BR", "electricQuantity": 75}
        ]
        self._gateways = [
            {"gatewayId": 20001, "gatewayName": "Gateway Floor 1-2", "isOnline": True}
        ]
        self._counter = 1000
    
    async def get_locks(self) -> List[dict]:
        return self._locks
    
    async def get_gateways(self) -> List[dict]:
        return self._gateways
    
    async def create_booking_passcode(self, lock_id, guest_name, check_in, check_out):
        self._counter += 1
        passcode = ''.join(random.choices(string.digits, k=6))
        backup = ''.join(random.choices(string.digits, k=6))
        print(f"    [MOCK] 🔐 Generated passcode {passcode} for {guest_name}")
        return {
            "passcode": passcode,
            "backup_passcode": backup,
            "passcode_id": self._counter,
            "valid_from": check_in,
            "valid_to": check_out
        }


# ============== XNC Service (NA17 Format) ==============

class XNCService:
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "exports", "xnc")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_na17_csv(self, guests, property_name, property_address, 
                          property_phone, recipient_authority, report_date) -> str:
        filename = f"NA17_{report_date.isoformat()}_{datetime.now().strftime('%H%M%S')}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        headers = [
            "STT", "Họ và tên", "Giới tính", "Ngày sinh", "Quốc tịch",
            "Số hộ chiếu", "Loại giấy tờ", "Ngày nhập cảnh", "Cửa khẩu nhập cảnh",
            "Mục đích nhập cảnh", "Tạm trú từ ngày", "Đến ngày",
            "Loại thị thực", "Số thị thực", "Ngày cấp thị thực", "Cơ quan cấp thị thực"
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            f.write(f"# Tên cơ sở lưu trú: {property_name}\n")
            f.write(f"# Địa chỉ: {property_address}\n")
            f.write(f"# Điện thoại: {property_phone}\n")
            f.write(f"# Kính gửi: {recipient_authority}\n")
            f.write(f"# Ngày báo cáo: {report_date.strftime('%d/%m/%Y')}\n#\n")
            
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for idx, g in enumerate(guests, 1):
                gender_vn = "Nam" if g.gender.lower() in ["male", "m"] else "Nữ"
                writer.writerow([
                    idx, g.full_name.upper(), gender_vn,
                    g.date_of_birth.strftime("%d/%m/%Y"), g.nationality,
                    g.passport_number, "Hộ chiếu phổ thông",
                    g.arrival_date.strftime("%d/%m/%Y"), "Sân bay Tân Sơn Nhất",
                    "Du lịch", g.arrival_date.strftime("%d/%m/%Y"),
                    g.departure_date.strftime("%d/%m/%Y"),
                    "", "", "", ""
                ])
        
        return filepath
    
    def generate_na17_txt(self, guests, property_name, property_address,
                          property_phone, recipient_authority, report_date) -> str:
        filename = f"NA17_Print_{report_date.isoformat()}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("PHIẾU KHAI BÁO TẠM TRÚ CHO NGƯỜI NƯỚC NGOÀI (MẪU NA17)\n")
            f.write("Theo Thông tư số 04/2015/TT-BCA\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Kính gửi: {recipient_authority}\n\n")
            f.write(f"Tên cơ sở lưu trú: {property_name}\n")
            f.write(f"Địa chỉ: {property_address}\n")
            f.write(f"Điện thoại: {property_phone}\n\n")
            f.write("-" * 70 + "\n")
            f.write(f"DANH SÁCH NGƯỜI NƯỚC NGOÀI TẠM TRÚ (Ngày {report_date.strftime('%d/%m/%Y')})\n")
            f.write("-" * 70 + "\n\n")
            
            for idx, g in enumerate(guests, 1):
                gender_vn = "Nam" if g.gender.lower() in ["male", "m"] else "Nữ"
                f.write(f"[{idx}] {g.full_name.upper()}\n")
                f.write(f"    Giới tính: {gender_vn}\n")
                f.write(f"    Ngày sinh: {g.date_of_birth.strftime('%d/%m/%Y')}\n")
                f.write(f"    Quốc tịch: {g.nationality}\n")
                f.write(f"    Số hộ chiếu: {g.passport_number}\n")
                f.write(f"    Tạm trú: {g.arrival_date.strftime('%d/%m/%Y')} - {g.departure_date.strftime('%d/%m/%Y')}\n")
                f.write(f"    Địa chỉ: {g.temporary_address}\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("                              NGƯỜI KHAI BÁO\n")
            f.write("                              (Ký, ghi rõ họ tên)\n\n\n")
            f.write("                              ___________________\n")
        
        return filepath


# ============== Demo Flow ==============

async def run_demo():
    print("\n" + "🏨 " * 15)
    print("\n   HOTEL PMS - DEMO BOOKING FLOW (Mock Mode)\n")
    print("🏨 " * 15 + "\n")
    
    channex = MockChannexService()
    ttlock = MockTTLockService()
    xnc = XNCService()
    
    # Step 1: Get bookings
    print("📥 STEP 1: Fetching bookings from Channex (mock)...")
    print("-" * 50)
    bookings = await channex.get_feed()
    print(f"Found {len(bookings)} bookings:\n")
    
    for b in bookings:
        g = b.get("guest", {})
        print(f"  📋 {b['id']}")
        print(f"     OTA: {b['ota_name']}")
        print(f"     Guest: {g.get('name')} ({g.get('nationality')})")
        print(f"     Check-in: {b['arrival_date']} → {b['departure_date']}\n")
    
    # Step 2: Generate passcodes
    print("\n🔐 STEP 2: Generating passcodes via TTLock (mock)...")
    print("-" * 50)
    
    locks = await ttlock.get_locks()
    print(f"Available locks: {', '.join([l['lockName'] for l in locks])}\n")
    
    passcode_results = []
    for i, b in enumerate(bookings):
        lock = locks[i % len(locks)]
        guest = b.get("guest", {})
        check_in = datetime.strptime(b['arrival_date'], "%Y-%m-%d").replace(hour=15)
        check_out = datetime.strptime(b['departure_date'], "%Y-%m-%d").replace(hour=11)
        
        result = await ttlock.create_booking_passcode(
            lock_id=lock['lockId'],
            guest_name=guest.get('name'),
            check_in=check_in,
            check_out=check_out
        )
        passcode_results.append({"booking": b, "lock": lock, "passcode": result})
        print(f"     → {lock['lockName']}: {result['passcode']} (backup: {result['backup_passcode']})")
    
    # Step 3: Send messages
    print("\n\n📨 STEP 3: Sending passcodes to guests...")
    print("-" * 50)
    
    for r in passcode_results:
        b = r['booking']
        g = b.get('guest', {})
        await channex.send_passcode_message(
            booking_id=b['id'],
            guest_name=g.get('name'),
            check_in_date=datetime.strptime(b['arrival_date'], "%Y-%m-%d").date(),
            check_out_date=datetime.strptime(b['departure_date'], "%Y-%m-%d").date(),
            passcode=r['passcode']['passcode'],
            property_address="123 Nguyen Hue, District 1, HCM"
        )
    
    # Step 4: Acknowledge
    print("\n✓ STEP 4: Acknowledging bookings...")
    print("-" * 50)
    for b in bookings:
        await channex.acknowledge_booking_revision(b['revision_id'])
        print(f"    ✓ Acknowledged: {b['id']}")
    
    # Step 5: XNC Report
    print("\n\n📋 STEP 5: Generating XNC Report (NA17 format)...")
    print("-" * 50)
    
    xnc_guests = []
    for b in bookings:
        g = b.get("guest", {})
        if g.get('nationality') and g.get('nationality') != 'Vietnam':
            xnc_guests.append(XNCGuestData(
                full_name=g.get('name', 'Unknown'),
                gender="male",
                date_of_birth=date(1990, 1, 15),
                nationality=g.get('nationality'),
                passport_number="AB" + ''.join(random.choices(string.digits, k=7)),
                temporary_address="123 Nguyen Hue, District 1, HCM",
                arrival_date=datetime.strptime(b['arrival_date'], "%Y-%m-%d").date(),
                departure_date=datetime.strptime(b['departure_date'], "%Y-%m-%d").date()
            ))
    
    today = date.today()
    csv_path = xnc.generate_na17_csv(
        guests=xnc_guests,
        property_name="Sunrise Apartment",
        property_address="123 Nguyen Hue, District 1, HCM",
        property_phone="0901234567",
        recipient_authority="Công an Phường Bến Nghé, Quận 1",
        report_date=today
    )
    print(f"\n    📄 CSV: {csv_path}")
    
    txt_path = xnc.generate_na17_txt(
        guests=xnc_guests,
        property_name="Sunrise Apartment",
        property_address="123 Nguyen Hue, District 1, HCM",
        property_phone="0901234567",
        recipient_authority="Công an Phường Bến Nghé, Quận 1",
        report_date=today
    )
    print(f"    📄 TXT: {txt_path}")
    
    # Summary
    print("\n\n" + "=" * 60)
    print("✅ DEMO COMPLETE!")
    print("=" * 60)
    print(f"""
Summary:
  - Processed: {len(bookings)} bookings
  - Generated: {len(passcode_results)} passcodes  
  - XNC Report: {len(xnc_guests)} foreign guests

Check the exports folder:
  {xnc.output_dir}
""")
    
    # Show sample of generated CSV
    print("\n📄 Sample NA17 CSV content:")
    print("-" * 50)
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        print(f.read()[:800])
    print("...")


if __name__ == "__main__":
    asyncio.run(run_demo())
