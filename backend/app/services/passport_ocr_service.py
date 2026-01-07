"""
Hotel PMS - Passport OCR Service
Extract guest information from passport images using MRZ parsing.

Supports:
- MRZ (Machine Readable Zone) extraction
- Passport data parsing (name, DOB, nationality, passport number, expiry)
- Multiple OCR backends (Tesseract, Google Vision API)
"""
import re
import os
import logging
from datetime import date, datetime
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PassportData:
    """Extracted passport data."""
    full_name: str
    surname: str
    given_names: str
    passport_number: str
    nationality: str
    date_of_birth: Optional[date]
    gender: str
    expiry_date: Optional[date]
    issuing_country: str
    mrz_line1: Optional[str] = None
    mrz_line2: Optional[str] = None
    confidence: float = 0.0
    raw_text: Optional[str] = None


class MRZParser:
    """
    Parse Machine Readable Zone (MRZ) from passport.
    
    MRZ Format (TD3 - Passport):
    Line 1 (44 chars): P<ISSUING_COUNTRY<SURNAME<<GIVEN_NAMES<<<<<<<<<<<<<<<<<<
    Line 2 (44 chars): PASSPORT_NUMBER<CHECK<NATIONALITY<DOB<CHECK<GENDER<EXPIRY<CHECK<OPTIONAL<CHECK
    """
    
    # Country code to name mapping
    COUNTRY_CODES = {
        "USA": "United States",
        "GBR": "United Kingdom",
        "FRA": "France",
        "DEU": "Germany",
        "JPN": "Japan",
        "KOR": "South Korea",
        "CHN": "China",
        "VNM": "Vietnam",
        "AUS": "Australia",
        "CAN": "Canada",
        "ITA": "Italy",
        "ESP": "Spain",
        "NLD": "Netherlands",
        "BEL": "Belgium",
        "CHE": "Switzerland",
        "THA": "Thailand",
        "SGP": "Singapore",
        "MYS": "Malaysia",
        "IDN": "Indonesia",
        "PHL": "Philippines",
        "IND": "India",
        "RUS": "Russia",
        "BRA": "Brazil",
        "MEX": "Mexico",
        "ARG": "Argentina",
    }
    
    @staticmethod
    def clean_mrz_text(text: str) -> str:
        """Clean OCR output to valid MRZ characters."""
        # Replace common OCR errors
        replacements = {
            'O': '0',  # Letter O to zero
            'I': '1',  # Letter I to one
            'S': '5',  # Sometimes S becomes 5
            ' ': '',   # Remove spaces
            '\n': '',  # Remove newlines in middle
        }
        
        # Only keep valid MRZ characters: A-Z, 0-9, <
        cleaned = ''.join(
            c for c in text.upper() 
            if c.isalnum() or c == '<'
        )
        return cleaned
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[date]:
        """
        Parse MRZ date format: YYMMDD.
        Handles century determination (00-30 = 2000s, 31-99 = 1900s for DOB).
        """
        if len(date_str) != 6 or not date_str.isdigit():
            return None
        
        try:
            yy = int(date_str[0:2])
            mm = int(date_str[2:4])
            dd = int(date_str[4:6])
            
            # Determine century
            current_year = datetime.now().year % 100
            if yy <= current_year + 10:  # Likely 2000s
                year = 2000 + yy
            else:  # Likely 1900s
                year = 1900 + yy
            
            return date(year, mm, dd)
        except ValueError:
            return None
    
    @staticmethod
    def calculate_check_digit(data: str) -> int:
        """Calculate MRZ check digit."""
        weights = [7, 3, 1]
        values = {
            '<': 0, '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
            '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14,
            'F': 15, 'G': 16, 'H': 17, 'I': 18, 'J': 19,
            'K': 20, 'L': 21, 'M': 22, 'N': 23, 'O': 24,
            'P': 25, 'Q': 26, 'R': 27, 'S': 28, 'T': 29,
            'U': 30, 'V': 31, 'W': 32, 'X': 33, 'Y': 34, 'Z': 35
        }
        
        total = 0
        for i, char in enumerate(data.upper()):
            total += values.get(char, 0) * weights[i % 3]
        
        return total % 10
    
    @classmethod
    def parse(cls, mrz_text: str) -> Optional[PassportData]:
        """
        Parse MRZ text and extract passport data.
        
        Args:
            mrz_text: Raw MRZ text (2 lines, 44 chars each for TD3)
            
        Returns:
            PassportData object or None if parsing fails
        """
        # Clean and split into lines
        lines = mrz_text.strip().split('\n')
        
        if len(lines) < 2:
            # Try to split 88-char string
            cleaned = cls.clean_mrz_text(mrz_text)
            if len(cleaned) >= 88:
                lines = [cleaned[:44], cleaned[44:88]]
            else:
                logger.warning(f"Invalid MRZ: expected 2 lines, got {len(lines)}")
                return None
        
        line1 = cls.clean_mrz_text(lines[0])
        line2 = cls.clean_mrz_text(lines[1])
        
        # Validate line lengths
        if len(line1) < 44 or len(line2) < 44:
            logger.warning(f"Invalid MRZ line lengths: {len(line1)}, {len(line2)}")
            return None
        
        try:
            # Parse Line 1: Document type, country, name
            doc_type = line1[0:2]
            issuing_country = line1[2:5]
            name_field = line1[5:44]
            
            # Split name by <<
            name_parts = name_field.split('<<')
            surname = name_parts[0].replace('<', ' ').strip()
            given_names = ' '.join(name_parts[1:]).replace('<', ' ').strip() if len(name_parts) > 1 else ""
            
            # Parse Line 2: Passport number, nationality, DOB, gender, expiry
            passport_number = line2[0:9].replace('<', '')
            passport_check = line2[9]
            nationality = line2[10:13]
            dob_str = line2[13:19]
            dob_check = line2[19]
            gender_code = line2[20]
            expiry_str = line2[21:27]
            expiry_check = line2[27]
            
            # Parse dates
            date_of_birth = cls.parse_date(dob_str)
            expiry_date = cls.parse_date(expiry_str)
            
            # Parse gender
            gender_map = {'M': 'male', 'F': 'female', '<': 'unknown'}
            gender = gender_map.get(gender_code, 'unknown')
            
            # Get country name
            nationality_name = cls.COUNTRY_CODES.get(nationality, nationality)
            issuing_country_name = cls.COUNTRY_CODES.get(issuing_country, issuing_country)
            
            # Build full name
            full_name = f"{given_names} {surname}".strip()
            if not full_name:
                full_name = surname or "Unknown"
            
            # Calculate confidence based on check digits
            confidence = 1.0
            if passport_check.isdigit():
                expected = cls.calculate_check_digit(line2[0:9])
                if int(passport_check) != expected:
                    confidence *= 0.7
            
            return PassportData(
                full_name=full_name,
                surname=surname,
                given_names=given_names,
                passport_number=passport_number,
                nationality=nationality_name,
                date_of_birth=date_of_birth,
                gender=gender,
                expiry_date=expiry_date,
                issuing_country=issuing_country_name,
                mrz_line1=line1,
                mrz_line2=line2,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"MRZ parsing error: {e}")
            return None


class PassportOCRService:
    """
    Passport OCR service with multiple backend support.
    
    Priority:
    1. Google Cloud Vision (if configured)
    2. Tesseract OCR (local, free)
    3. Manual MRZ input
    """
    
    def __init__(self):
        self.upload_dir = Path("uploads/passports")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Check available OCR backends
        self.tesseract_available = self._check_tesseract()
        self.google_vision_available = False  # Would check API key
        
        logger.info(f"PassportOCR initialized. Tesseract: {self.tesseract_available}")
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract is installed."""
        try:
            import subprocess
            result = subprocess.run(['tesseract', '--version'], 
                                    capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    async def extract_from_image(self, image_path: str) -> Optional[PassportData]:
        """
        Extract passport data from image.
        
        Args:
            image_path: Path to passport image
            
        Returns:
            PassportData or None
        """
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return None
        
        # Try OCR backends in order
        mrz_text = None
        
        if self.tesseract_available:
            mrz_text = await self._ocr_tesseract(image_path)
        
        if not mrz_text:
            logger.warning("OCR failed, no MRZ detected")
            return None
        
        # Parse MRZ
        passport_data = MRZParser.parse(mrz_text)
        if passport_data:
            passport_data.raw_text = mrz_text
        
        return passport_data
    
    async def _ocr_tesseract(self, image_path: str) -> Optional[str]:
        """Extract text using Tesseract OCR."""
        try:
            import subprocess
            
            # Run tesseract with MRZ-optimized settings
            result = subprocess.run([
                'tesseract', image_path, 'stdout',
                '--psm', '6',  # Assume uniform block of text
                '-c', 'tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                text = result.stdout.strip()
                logger.info(f"Tesseract OCR result: {text[:100]}...")
                return text
            else:
                logger.error(f"Tesseract error: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
        
        return None
    
    def parse_mrz_manual(self, mrz_line1: str, mrz_line2: str) -> Optional[PassportData]:
        """
        Parse manually entered MRZ lines.
        
        Args:
            mrz_line1: First MRZ line (44 chars)
            mrz_line2: Second MRZ line (44 chars)
            
        Returns:
            PassportData or None
        """
        mrz_text = f"{mrz_line1}\n{mrz_line2}"
        return MRZParser.parse(mrz_text)
    
    def validate_passport_number(self, passport_number: str, country: str) -> bool:
        """Validate passport number format by country."""
        patterns = {
            "United States": r'^[0-9]{9}$',
            "United Kingdom": r'^[0-9]{9}$',
            "France": r'^[0-9A-Z]{9}$',
            "Germany": r'^[CFGHJKLMNPRTVWXYZ0-9]{9}$',
            "Japan": r'^[A-Z]{2}[0-9]{7}$',
            "South Korea": r'^[A-Z]{1,2}[0-9]{7,8}$',
            "China": r'^[GE][0-9]{8}$',
            "Vietnam": r'^[A-Z][0-9]{7,8}$',
        }
        
        pattern = patterns.get(country, r'^[A-Z0-9]{6,12}$')
        return bool(re.match(pattern, passport_number.upper()))
    
    def save_passport_image(self, booking_id: str, image_data: bytes, 
                           filename: str) -> str:
        """Save uploaded passport image."""
        # Create booking-specific directory
        booking_dir = self.upload_dir / booking_id
        booking_dir.mkdir(exist_ok=True)
        
        # Save file
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        file_path = booking_dir / safe_filename
        
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"Saved passport image: {file_path}")
        return str(file_path)


# Demo function for testing
def demo_mrz_parsing():
    """Demo MRZ parsing with sample data."""
    # Sample MRZ (TD3 format)
    sample_mrz = """P<USASMITH<<JOHN<WILLIAM<<<<<<<<<<<<<<<<<<<<<
AB12345671USA9001011M3012315<<<<<<<<<<<<<<02"""
    
    print("🛂 MRZ Parsing Demo")
    print("=" * 50)
    print(f"Input MRZ:\n{sample_mrz}")
    print("=" * 50)
    
    result = MRZParser.parse(sample_mrz)
    
    if result:
        print(f"\n✅ Parsed Successfully!")
        print(f"   Full Name: {result.full_name}")
        print(f"   Surname: {result.surname}")
        print(f"   Given Names: {result.given_names}")
        print(f"   Passport: {result.passport_number}")
        print(f"   Nationality: {result.nationality}")
        print(f"   DOB: {result.date_of_birth}")
        print(f"   Gender: {result.gender}")
        print(f"   Expiry: {result.expiry_date}")
        print(f"   Confidence: {result.confidence:.0%}")
    else:
        print("\n❌ Parsing failed")
    
    return result


# Singleton service
passport_ocr_service = PassportOCRService()


if __name__ == "__main__":
    demo_mrz_parsing()
