"""
Hotel PMS - XNC Service (Updated)
Immigration Portal Report Generation based on NA17 Template.

Mẫu NA17 - Phiếu khai báo tạm trú cho người nước ngoài
(Theo Thông tư 04/2015/TT-BCA)
"""
import os
from typing import List, Optional
from datetime import date, datetime
from lxml import etree
import csv
import logging

from app.config import settings
from app.schemas import XNCGuestData

logger = logging.getLogger(__name__)


# NA17 Field mappings (Vietnamese)
NA17_FIELDS = {
    "property_name": "Tên cơ sở lưu trú",
    "property_address": "Địa chỉ",
    "property_phone": "Điện thoại",
    "recipient": "Kính gửi (Công an phường/xã)",
    "stt": "STT",
    "full_name": "Họ và tên",
    "gender": "Giới tính",
    "dob": "Ngày tháng năm sinh",
    "nationality": "Quốc tịch",
    "passport_number": "Số hộ chiếu",
    "document_type": "Loại giấy tờ",
    "entry_date": "Ngày nhập cảnh",
    "entry_port": "Cửa khẩu nhập cảnh",
    "entry_purpose": "Mục đích nhập cảnh",
    "stay_from": "Tạm trú từ ngày",
    "stay_to": "Đến ngày",
    "visa_type": "Loại thị thực",
    "visa_number": "Số thị thực",
    "visa_issue_date": "Ngày cấp thị thực",
    "visa_issuer": "Cơ quan cấp thị thực"
}


class XNCServiceNA17:
    """
    Vietnam Immigration Report Service - NA17 Format.
    
    Generates reports for foreigner temporary residence registration
    following the official NA17 template format.
    
    Portal: hochiminh.xuatnhapcanh.gov.vn
    Regulation: Thông tư 04/2015/TT-BCA
    """
    
    def __init__(self):
        self.portal_url = settings.xnc_portal_url
        self.output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "exports", "xnc")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    # ============== CSV Export (Primary - for Portal Upload) ==============
    
    def generate_na17_csv(
        self,
        guests: List[XNCGuestData],
        property_name: str,
        property_address: str,
        property_phone: str,
        recipient_authority: str,  # e.g., "Công an Phường Bến Nghé, Quận 1"
        report_date: date
    ) -> str:
        """
        Generate CSV file following NA17 format for batch upload.
        
        This is the most compatible format for the XNC portal's "Import Data" feature.
        
        Args:
            guests: List of foreign guest data
            property_name: Name of accommodation establishment
            property_address: Full address
            property_phone: Contact phone number
            recipient_authority: Police station to submit to
            report_date: Date of the report
            
        Returns:
            Path to generated CSV file
        """
        filename = f"NA17_{report_date.isoformat()}_{datetime.now().strftime('%H%M%S')}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        # NA17 CSV headers (matching portal import format)
        headers = [
            "STT",
            "Họ và tên",
            "Giới tính",
            "Ngày sinh",
            "Quốc tịch",
            "Số hộ chiếu",
            "Loại giấy tờ",
            "Ngày nhập cảnh",
            "Cửa khẩu nhập cảnh",
            "Mục đích nhập cảnh",
            "Tạm trú từ ngày",
            "Đến ngày",
            "Loại thị thực",
            "Số thị thực",
            "Ngày cấp thị thực",
            "Cơ quan cấp thị thực"
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            # Write property header info as comments
            f.write(f"# Tên cơ sở lưu trú: {property_name}\n")
            f.write(f"# Địa chỉ: {property_address}\n")
            f.write(f"# Điện thoại: {property_phone}\n")
            f.write(f"# Kính gửi: {recipient_authority}\n")
            f.write(f"# Ngày báo cáo: {report_date.strftime('%d/%m/%Y')}\n")
            f.write(f"#\n")
            
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for idx, guest in enumerate(guests, 1):
                row = [
                    idx,  # STT
                    guest.full_name.upper(),  # Họ và tên
                    self._translate_gender(guest.gender),  # Giới tính
                    self._format_date_vn(guest.date_of_birth),  # Ngày sinh
                    guest.nationality,  # Quốc tịch
                    guest.passport_number,  # Số hộ chiếu
                    "Hộ chiếu phổ thông",  # Loại giấy tờ (default)
                    self._format_date_vn(guest.arrival_date),  # Ngày nhập cảnh
                    "Sân bay Tân Sơn Nhất",  # Cửa khẩu (default for HCM)
                    "Du lịch",  # Mục đích (default)
                    self._format_date_vn(guest.arrival_date),  # Tạm trú từ ngày
                    self._format_date_vn(guest.departure_date),  # Đến ngày
                    "",  # Loại thị thực (optional)
                    "",  # Số thị thực (optional)
                    "",  # Ngày cấp thị thực (optional)
                    ""   # Cơ quan cấp thị thực (optional)
                ]
                writer.writerow(row)
        
        logger.info(f"Generated NA17 CSV: {filepath} with {len(guests)} guests")
        return filepath
    
    # ============== XML Export (Alternative) ==============
    
    def generate_na17_xml(
        self,
        guests: List[XNCGuestData],
        property_name: str,
        property_address: str,
        property_phone: str,
        recipient_authority: str,
        report_date: date
    ) -> str:
        """
        Generate XML file following NA17 structure.
        
        Note: The official portal may not support XML - CSV is preferred.
        This is provided as an alternative for systems that require XML.
        """
        filename = f"NA17_{report_date.isoformat()}_{datetime.now().strftime('%H%M%S')}.xml"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create root element
        root = etree.Element("PhieuKhaiBaoTamTru")
        root.set("version", "NA17")
        root.set("regulation", "TT04/2015/BCA")
        
        # Property info section
        cslt = etree.SubElement(root, "CoSoLuuTru")
        etree.SubElement(cslt, "TenCoSo").text = property_name
        etree.SubElement(cslt, "DiaChi").text = property_address
        etree.SubElement(cslt, "DienThoai").text = property_phone
        etree.SubElement(cslt, "KinhGui").text = recipient_authority
        
        # Report metadata
        metadata = etree.SubElement(root, "ThongTinBaoCao")
        etree.SubElement(metadata, "NgayBaoCao").text = report_date.strftime("%d/%m/%Y")
        etree.SubElement(metadata, "SoLuongKhach").text = str(len(guests))
        
        # Guest list
        guest_list = etree.SubElement(root, "DanhSachNguoiNuocNgoai")
        
        for idx, guest in enumerate(guests, 1):
            guest_elem = etree.SubElement(guest_list, "NguoiNuocNgoai")
            guest_elem.set("stt", str(idx))
            
            # Personal info
            etree.SubElement(guest_elem, "HoTen").text = guest.full_name.upper()
            etree.SubElement(guest_elem, "GioiTinh").text = self._translate_gender(guest.gender)
            etree.SubElement(guest_elem, "NgaySinh").text = self._format_date_vn(guest.date_of_birth)
            etree.SubElement(guest_elem, "QuocTich").text = guest.nationality
            
            # Passport info
            passport = etree.SubElement(guest_elem, "HoChieu")
            etree.SubElement(passport, "SoHoChieu").text = guest.passport_number
            etree.SubElement(passport, "LoaiGiayTo").text = "Hộ chiếu phổ thông"
            if guest.passport_issue_date:
                etree.SubElement(passport, "NgayCap").text = self._format_date_vn(guest.passport_issue_date)
            if guest.passport_expiry_date:
                etree.SubElement(passport, "NgayHetHan").text = self._format_date_vn(guest.passport_expiry_date)
            if guest.passport_issue_country:
                etree.SubElement(passport, "NoiCap").text = guest.passport_issue_country
            
            # Entry info
            entry = etree.SubElement(guest_elem, "ThongTinNhapCanh")
            etree.SubElement(entry, "NgayNhapCanh").text = self._format_date_vn(guest.arrival_date)
            etree.SubElement(entry, "CuaKhau").text = "Sân bay Tân Sơn Nhất"
            etree.SubElement(entry, "MucDich").text = "Du lịch"
            
            # Stay info
            stay = etree.SubElement(guest_elem, "TamTru")
            etree.SubElement(stay, "DiaChi").text = guest.temporary_address
            etree.SubElement(stay, "TuNgay").text = self._format_date_vn(guest.arrival_date)
            etree.SubElement(stay, "DenNgay").text = self._format_date_vn(guest.departure_date)
        
        # Write XML file
        tree = etree.ElementTree(root)
        tree.write(
            filepath,
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True
        )
        
        logger.info(f"Generated NA17 XML: {filepath} with {len(guests)} guests")
        return filepath
    
    # ============== Format for Manual Entry ==============
    
    def generate_na17_printable(
        self,
        guests: List[XNCGuestData],
        property_name: str,
        property_address: str,
        property_phone: str,
        recipient_authority: str,
        report_date: date
    ) -> str:
        """
        Generate a printable text format for manual submission.
        
        This creates a human-readable format that can be printed
        and submitted physically if needed.
        """
        filename = f"NA17_Print_{report_date.isoformat()}_{datetime.now().strftime('%H%M%S')}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("PHIẾU KHAI BÁO TẠM TRÚ CHO NGƯỜI NƯỚC NGOÀI (MẪU NA17)\n")
            f.write("Theo Thông tư số 04/2015/TT-BCA ngày 05/01/2015 của Bộ Công an\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Kính gửi: {recipient_authority}\n\n")
            
            f.write("THÔNG TIN CƠ SỞ LƯU TRÚ:\n")
            f.write(f"  - Tên cơ sở: {property_name}\n")
            f.write(f"  - Địa chỉ: {property_address}\n")
            f.write(f"  - Điện thoại: {property_phone}\n\n")
            
            f.write(f"Ngày báo cáo: {report_date.strftime('%d/%m/%Y')}\n")
            f.write(f"Tổng số khách: {len(guests)} người\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("DANH SÁCH NGƯỜI NƯỚC NGOÀI TẠM TRÚ:\n")
            f.write("-" * 80 + "\n\n")
            
            for idx, guest in enumerate(guests, 1):
                f.write(f"[{idx}] {guest.full_name.upper()}\n")
                f.write(f"    - Giới tính: {self._translate_gender(guest.gender)}\n")
                f.write(f"    - Ngày sinh: {self._format_date_vn(guest.date_of_birth)}\n")
                f.write(f"    - Quốc tịch: {guest.nationality}\n")
                f.write(f"    - Số hộ chiếu: {guest.passport_number}\n")
                f.write(f"    - Tạm trú: {self._format_date_vn(guest.arrival_date)} đến {self._format_date_vn(guest.departure_date)}\n")
                f.write(f"    - Địa chỉ tạm trú: {guest.temporary_address}\n")
                f.write("\n")
            
            f.write("-" * 80 + "\n\n")
            f.write("                                        Ngày ... tháng ... năm ...\n")
            f.write("                                        NGƯỜI KHAI BÁO\n")
            f.write("                                        (Ký, ghi rõ họ tên)\n\n\n\n")
            f.write("                                        _________________________\n")
        
        logger.info(f"Generated NA17 printable: {filepath}")
        return filepath
    
    # ============== Helper Methods ==============
    
    def _translate_gender(self, gender: str) -> str:
        """Translate gender to Vietnamese."""
        if gender and gender.lower() in ["male", "m", "nam"]:
            return "Nam"
        elif gender and gender.lower() in ["female", "f", "nữ", "nu"]:
            return "Nữ"
        return gender or "Không rõ"
    
    def _format_date_vn(self, d: Optional[date]) -> str:
        """Format date to Vietnamese format (dd/mm/yyyy)."""
        if d:
            return d.strftime("%d/%m/%Y")
        return ""
    
    def get_pending_guests_count(self) -> int:
        """Get count of pending guests (mock for now)."""
        return 0


# Export service - use this updated version
xnc_service = XNCServiceNA17()
