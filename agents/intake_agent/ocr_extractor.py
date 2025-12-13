"""
OCR Extractor for Document Verification
Extracts data from KYC documents using Tesseract OCR
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import pytesseract
    from PIL import Image
    import pdfplumber
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

logger = logging.getLogger(__name__)

class OCRExtractor:
    """Extract document data using Tesseract OCR"""
    
    def __init__(self):
        if not TESSERACT_AVAILABLE:
            logger.warning("Tesseract OCR not available. Install pytesseract and tesseract-ocr.")
    
    def extract_from_document(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from KYC document (Aadhaar/PAN/Passport)
        
        Args:
            file_path: Path to document (image or PDF)
        
        Returns:
            Dictionary with extracted data: {pan_number, aadhaar_number, name, dob, father_name}
        """
        if not TESSERACT_AVAILABLE:
            logger.error("Tesseract OCR not available")
            return {}
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                return self._extract_from_image(file_path)
            elif file_ext == '.pdf':
                return self._extract_from_pdf(file_path)
            else:
                logger.error(f"Unsupported file format: {file_ext}")
                return {}
        
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return {}
    
    def _extract_from_image(self, image_path: str) -> Dict[str, Any]:
        """Extract text from image using Tesseract"""
        try:
            image = Image.open(image_path)
            raw_text = pytesseract.image_to_string(image)
            
            return self._parse_ocr_text(raw_text)
        
        except Exception as e:
            logger.error(f"Image OCR error: {e}")
            return {}
    
    def _extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from PDF using pdfplumber"""
        try:
            extracted_data = {}
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        parsed = self._parse_ocr_text(text)
                        # Merge extracted data (first occurrence wins)
                        for key, value in parsed.items():
                            if key not in extracted_data and value:
                                extracted_data[key] = value
            
            return extracted_data
        
        except Exception as e:
            logger.error(f"PDF OCR error: {e}")
            return {}
    
    def _parse_ocr_text(self, text: str) -> Dict[str, Any]:
        """Parse OCR text to extract structured data"""
        extracted = {
            "pan_number": None,
            "aadhaar_number": None,
            "name": None,
            "dob": None,
            "father_name": None
        }
        
        # PAN pattern: AAAAA9999A (e.g., DIJPN7537R)
        pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', text)
        if pan_match:
            extracted["pan_number"] = pan_match.group(0)
            logger.info(f"Extracted PAN: {extracted['pan_number']}")
        
        # Aadhaar pattern: 12 digits
        aadhaar_match = re.search(r'\b\d{12}\b', text)
        if aadhaar_match:
            extracted["aadhaar_number"] = aadhaar_match.group(0)
            logger.info(f"Extracted Aadhaar: {extracted['aadhaar_number']}")
        
        # DOB patterns: DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
        dob_match = re.search(r'\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b', text)
        if dob_match:
            day, month, year = dob_match.groups()
            # Normalize to DD/MM/YYYY format
            extracted["dob"] = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
            logger.info(f"Extracted DOB: {extracted['dob']}")
        
        # Name extraction (heuristic: capitalized words after specific keywords)
        # Look for patterns like "Name: JOHN DOE" or just capitalized sequences
        lines = text.split('\n')
        
        # Common document keywords to skip
        skip_keywords = ['GOVT', 'OF', 'INDIA', 'INCOME', 'TAX', 'DEPARTMENT', 'PERMANENT', 
                        'ACCOUNT', 'NUMBER', 'CARD', 'PAN', 'AADHAAR', 'PASSPORT', 'GOVERNMENT',
                        'ISSUED', 'DATE', 'BIRTH', 'FATHER', 'MOTHER', 'SPOUSE', 'SIGNATURE']
        
        for i, line in enumerate(lines):
            # Skip lines with too many special characters
            if sum(1 for c in line if c.isalpha()) < 3:
                continue
            
            # Look for name patterns (usually proper case or all caps)
            if 'name' in line.lower():
                # Extract words after "name"
                parts = line.split(':')
                if len(parts) > 1:
                    potential_name = parts[1].strip()
                    # Take first meaningful capitalized sequence
                    words = potential_name.split()
                    if words:
                        name_candidate = ' '.join(w for w in words[:3] if w and w[0].isupper())
                        if name_candidate and len(name_candidate) > 2:
                            extracted["name"] = name_candidate
                            logger.info(f"Extracted Name (keyword): {extracted['name']}")
                            break
            
            # Fallback: look for all-caps sequences (common in document scans)
            all_caps_words = re.findall(r'\b[A-Z][A-Z\s]{2,}\b', line)
            if all_caps_words and not extracted["name"]:
                # Skip common keywords - only take names with 2+ words or known name patterns
                for word_seq in all_caps_words:
                    words = word_seq.strip().split()
                    
                    # Filter out skip keywords
                    name_words = [w for w in words if w not in skip_keywords]
                    
                    if name_words:
                        candidate = ' '.join(name_words)
                        # Only accept if it looks like a name (has multiple parts or is long enough)
                        if len(name_words) >= 2 or len(candidate) > 6:
                            extracted["name"] = candidate
                            logger.info(f"Extracted Name (caps): {extracted['name']}")
                            break
        
        # Father's name extraction (usually after "Father" keyword)
        for i, line in enumerate(lines):
            if 'father' in line.lower():
                parts = line.split(':')
                if len(parts) > 1:
                    potential_father = parts[1].strip()
                    if potential_father and len(potential_father) > 3:
                        extracted["father_name"] = potential_father
                        logger.info(f"Extracted Father Name: {extracted['father_name']}")
                        break
        
        return extracted


# Singleton instance
ocr_extractor = OCRExtractor()


def extract_document_data(file_path: str) -> Dict[str, Any]:
    """Convenience function to extract data from document"""
    return ocr_extractor.extract_from_document(file_path)
