"""
Payslip OCR extraction and parsing logic.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from io import BytesIO
import re

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from utils import (
    extract_numbers,
    extract_email,
    extract_phone,
    extract_date,
    extract_month_year,
    calculate_confidence,
    validate_payslip_structure,
    normalize_text
)

logger = logging.getLogger(__name__)

# Initialize OCR reader (lazy load)
_ocr_reader = None


def get_ocr_reader():
    """Lazy load EasyOCR reader for efficiency."""
    global _ocr_reader
    if _ocr_reader is None and EASYOCR_AVAILABLE:
        try:
            logger.info("Initializing EasyOCR reader...")
            _ocr_reader = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR reader initialized")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            _ocr_reader = None
    return _ocr_reader


def extract_text_from_image(image_bytes: bytes) -> Optional[str]:
    """
    Extract text from image using EasyOCR.
    
    Args:
        image_bytes: Binary image data (PNG/JPG)
    
    Returns:
        Extracted text or None if extraction fails
    """
    if not PIL_AVAILABLE:
        logger.error("PIL not available")
        return None
    
    try:
        # Load image from bytes
        image = Image.open(BytesIO(image_bytes))
        image = image.convert('RGB')
        
        # Use EasyOCR
        reader = get_ocr_reader()
        if reader is None:
            logger.error("OCR reader not available")
            return None
        
        # Read text
        results = reader.readtext(image)
        text = "\n".join([result[1] for result in results])
        
        logger.info(f"Extracted {len(text)} characters from image")
        return text
    
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        return None


def extract_text_from_pdf(pdf_bytes: bytes) -> Optional[str]:
    """
    Extract text from PDF using PyPDF2 (fallback if available).
    
    Args:
        pdf_bytes: Binary PDF data
    
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        import PyPDF2
        pdf_file = BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        logger.info(f"Extracted {len(text)} characters from PDF")
        return text
    except ImportError:
        logger.warning("PyPDF2 not available, cannot process PDF")
        return None
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return None


def parse_payslip_text(text: str) -> Dict[str, Any]:
    """
    Parse extracted payslip text and extract structured data.
    
    Args:
        text: Raw OCR/PDF extracted text
    
    Returns:
        Dictionary with parsed payslip fields
    """
    if not text:
        return {}
    
    data = {
        'employee_name': None,
        'employee_id': None,
        'designation': None,
        'department': None,
        'employer': None,
        'employer_address': None,
        'pay_period': None,
        'payment_date': None,
        'basic_pay': 0.0,
        'hra': 0.0,
        'special_allowance': 0.0,
        'conveyance': 0.0,
        'other_allowance': 0.0,
        'gross_earnings': 0.0,
        'pf': 0.0,
        'professional_tax': 0.0,
        'income_tax': 0.0,
        'other_deductions': 0.0,
        'total_deductions': 0.0,
        'net_pay_payslip': 0.0,
    }
    
    lines = text.split('\n')
    
    # Extract personal information
    for line in lines:
        normalized = normalize_text(line)
        
        # Employee name (often on first meaningful line)
        if 'name' in normalized and not data['employee_name']:
            match = re.search(r'name\s*[:-]?\s*([A-Za-z\s]+)', line, re.IGNORECASE)
            if match:
                data['employee_name'] = match.group(1).strip()
        
        # Employee ID
        if ('id' in normalized or 'emp' in normalized) and not data['employee_id']:
            match = re.search(r'(?:emp(?:loyee)?\.?\s*)?(?:id|#)\s*[:-]?\s*([A-Z0-9]+)', line, re.IGNORECASE)
            if match:
                data['employee_id'] = match.group(1).strip()
        
        # Designation
        if ('designation' in normalized or 'position' in normalized) and not data['designation']:
            match = re.search(r'(?:designation|position)\s*[:-]?\s*([A-Za-z\s]+)', line, re.IGNORECASE)
            if match:
                data['designation'] = match.group(1).strip()
        
        # Department
        if 'department' in normalized and not data['department']:
            match = re.search(r'department\s*[:-]?\s*([A-Za-z\s]+)', line, re.IGNORECASE)
            if match:
                data['department'] = match.group(1).strip()
        
        # Employer
        if ('employer' in normalized or 'company' in normalized) and not data['employer']:
            match = re.search(r'(?:employer|company)\s*[:-]?\s*([A-Za-z0-9\s&.,]+)', line, re.IGNORECASE)
            if match:
                data['employer'] = match.group(1).strip()
        
        # Payment date
        if not data['payment_date']:
            date = extract_date(line)
            if date:
                data['payment_date'] = date
        
        # Pay period
        if not data['pay_period']:
            month_year = extract_month_year(line)
            if month_year:
                data['pay_period'] = month_year
    
    # Extract monetary values
    amount_patterns = {
        'basic_pay': [r'basic\s+pay', r'basic\s+salary'],
        'hra': [r'hra', r'house\s+rent'],
        'special_allowance': [r'special\s+allowance'],
        'conveyance': [r'conveyance', r'transport'],
        'other_allowance': [r'other\s+allowance'],
        'gross_earnings': [r'gross\s+earnings', r'gross\s+salary', r'total\s+earnings'],
        'pf': [r'provident\s+fund', r'pf'],
        'professional_tax': [r'professional\s+tax', r'pt'],
        'income_tax': [r'income\s+tax', r'it'],
        'other_deductions': [r'other\s+deduction'],
        'total_deductions': [r'total\s+deduction'],
        'net_pay_payslip': [r'net\s+pay', r'net\s+salary'],
    }
    
    for field, patterns in amount_patterns.items():
        for line in lines:
            normalized = normalize_text(line)
            for pattern in patterns:
                if re.search(pattern, normalized):
                    # Try to extract number from this line or next
                    amount = extract_numbers(line)
                    if amount > 0:
                        data[field] = amount
                        break
            if data[field] > 0:
                break
    
    return data


def extract_payslip_data(file_bytes: bytes, file_type: str = "auto") -> Dict[str, Any]:
    """
    Main function to extract and parse payslip data.
    
    Args:
        file_bytes: Binary file data
        file_type: "pdf", "image", or "auto"
    
    Returns:
        Parsed payslip data dictionary
    """
    try:
        # Determine file type
        if file_type == "auto":
            # Check magic bytes
            if file_bytes.startswith(b'%PDF'):
                file_type = "pdf"
            elif file_bytes.startswith(b'\x89PNG') or file_bytes.startswith(b'\xff\xd8'):
                file_type = "image"
            else:
                logger.warning("Unknown file type, attempting as image")
                file_type = "image"
        
        # Extract text based on type
        if file_type == "pdf":
            text = extract_text_from_pdf(file_bytes)
        else:
            text = extract_text_from_image(file_bytes)
        
        if not text:
            logger.error("No text extracted from file")
            return {}
        
        # Parse extracted text
        data = parse_payslip_text(text)
        
        # Validate structure
        if not validate_payslip_structure(data):
            logger.warning("Extracted data does not match valid payslip structure")
        
        return data
    
    except Exception as e:
        logger.error(f"Error in extract_payslip_data: {e}", exc_info=True)
        return {}


def generate_sample_ocr_text() -> str:
    """Generate sample OCR text for testing."""
    sample_text = """
    MONTHLY PAYSLIP
    
    Employee Name: John Doe
    Employee ID: EMP123456
    Designation: Software Engineer
    Department: Engineering
    Employer: TechCorp India Private Limited
    Employer Address: 123 Tech Park, Bangalore 560001
    
    Pay Period: January 2025
    Payment Date: 05-02-2025
    
    EARNINGS
    Basic Pay: 50,000.00
    House Rent Allowance (HRA): 10,000.00
    Special Allowance: 5,000.00
    Conveyance: 1,000.00
    Other Allowance: 2,000.00
    ────────────────────
    Gross Earnings: 68,000.00
    
    DEDUCTIONS
    Provident Fund (PF): 6,000.00
    Professional Tax: 200.00
    Income Tax: 5,000.00
    Other Deductions: 500.00
    ────────────────────
    Total Deductions: 11,700.00
    
    NET PAY: 56,300.00
    """
    return sample_text
