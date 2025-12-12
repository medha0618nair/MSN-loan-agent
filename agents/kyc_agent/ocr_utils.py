"""
OCR utilities for document text extraction.
Supports images and PDFs using pytesseract and pdfplumber.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import re

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available. OCR functionality limited.")

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("pdfplumber not available. PDF OCR unavailable.")

logger = logging.getLogger(__name__)


class OCRProcessor:
    """OCR processing for various document types."""
    
    def __init__(self):
        self.pan_pattern = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]{1}')
        self.aadhaar_pattern = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'[6-9]\d{9}')
    
    def process_image(self, file_path: str) -> Tuple[str, float]:
        """
        Extract text from image using Tesseract OCR.
        
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not TESSERACT_AVAILABLE:
            return "", 0.0
        
        try:
            image = Image.open(file_path)
            
            # Get OCR data with confidence
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [float(conf) for conf in ocr_data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Extract text
            text = pytesseract.image_to_string(image)
            
            return text.strip(), avg_confidence / 100.0
            
        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            return "", 0.0
    
    def process_pdf(self, file_path: str) -> Tuple[str, float]:
        """
        Extract text from PDF using pdfplumber.
        
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        if not PDF_AVAILABLE:
            return "", 0.0
        
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # PDFs with native text have high confidence
                confidence = 0.95 if text.strip() else 0.0
                
                return text.strip(), confidence
                
        except Exception as e:
            logger.error(f"PDF OCR failed: {e}")
            return "", 0.0
    
    def extract_pan(self, text: str) -> Dict[str, Any]:
        """Extract PAN number from text."""
        matches = self.pan_pattern.findall(text)
        
        if matches:
            return {
                "pan_number": matches[0],
                "confidence": 0.9,
                "found": True
            }
        
        return {
            "pan_number": None,
            "confidence": 0.0,
            "found": False
        }
    
    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract email and phone from text."""
        emails = self.email_pattern.findall(text)
        phones = self.phone_pattern.findall(text)
        
        return {
            "emails": emails[:3],  # Top 3 matches
            "phones": phones[:3],
            "email_found": len(emails) > 0,
            "phone_found": len(phones) > 0
        }
    
    def parse_pan_card(self, text: str) -> Dict[str, Any]:
        """Parse PAN card specific fields."""
        pan_data = self.extract_pan(text)
        
        # Extract name - look for line after "Name" or standalone name line
        name = None
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_clean = line.strip()
            # Check if this line contains "Name" keyword
            if 'name' in line.lower() and len(line_clean) > 4:
                # Try next line first (common format)
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # Skip if next line looks like another field or is too short
                    if next_line and len(next_line) > 2 and not any(kw in next_line.lower() for kw in ['father', 'date', 'dob', 'birth', 'signature']):
                        # Filter out non-alphabetic noise
                        name_parts = []
                        for word in next_line.split():
                            if any(c.isalpha() for c in word) and len(word) > 1:
                                name_parts.append(word)
                        if name_parts:
                            name = ' '.join(name_parts[:5])  # Take up to 5 words
                            break
                
                # Fallback: extract from same line after "Name"
                if not name:
                    parts = line_clean.split()
                    name_idx = -1
                    for idx, part in enumerate(parts):
                        if 'name' in part.lower():
                            name_idx = idx
                            break
                    if name_idx >= 0 and len(parts) > name_idx + 1:
                        name_parts = []
                        for word in parts[name_idx + 1:]:
                            if any(c.isalpha() for c in word) and len(word) > 1:
                                name_parts.append(word)
                        if name_parts:
                            name = ' '.join(name_parts[:5])
                            break
        
        # Calculate confidence based on extraction success
        confidence = 0.0
        if pan_data["pan_number"] and name:
            confidence = 0.95  # Both extracted successfully
        elif pan_data["pan_number"] or name:
            confidence = 0.50  # Only one extracted
        
        return {
            "pan_number": pan_data["pan_number"],
            "name": name,
            "confidence": confidence
        }

    def parse_aadhaar(self, text: str) -> Dict[str, Any]:
        """Parse Aadhaar specific fields using 12-digit pattern."""
        matches = self.aadhaar_pattern.findall(text)
        aadhaar_number = matches[0].replace(" ", "") if matches else None

        # Aadhaar numbers shouldn't be all repeated digits
        if aadhaar_number and len(set(aadhaar_number)) == 1:
            aadhaar_number = None

        # Extract name - look for line with name or standalone name after header
        name = None
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_clean = line.strip()
            # Check if this line contains "Name" or "name" keyword
            if 'name' in line.lower() and len(line_clean) > 4:
                # Try next line first (common format)
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # Skip if next line looks like another field or is too short
                    if next_line and len(next_line) > 2 and not any(kw in next_line.lower() for kw in ['dob', 'birth', 'male', 'female', 'address', 'aadhaar']):
                        # Filter out non-alphabetic noise
                        name_parts = []
                        for word in next_line.split():
                            if any(c.isalpha() for c in word) and len(word) > 1:
                                name_parts.append(word)
                        if name_parts:
                            name = ' '.join(name_parts[:5])
                            break
                
                # Fallback: extract from same line after "Name"
                if not name:
                    parts = line_clean.split()
                    name_idx = -1
                    for idx, part in enumerate(parts):
                        if 'name' in part.lower():
                            name_idx = idx
                            break
                    if name_idx >= 0 and len(parts) > name_idx + 1:
                        name_parts = []
                        for word in parts[name_idx + 1:]:
                            if any(c.isalpha() for c in word) and len(word) > 1:
                                name_parts.append(word)
                        if name_parts:
                            name = ' '.join(name_parts[:5])
                            break

        # Calculate confidence based on extraction success
        confidence = 0.0
        if aadhaar_number and name:
            confidence = 0.95  # Both extracted successfully
        elif aadhaar_number or name:
            confidence = 0.50  # Only one extracted

        return {
            "aadhaar_number": aadhaar_number,
            "name": name,
            "confidence": confidence
        }
    
    def parse_payslip(self, text: str) -> Dict[str, Any]:
        """Parse payslip specific fields."""
        # Extract salary amounts (simplified)
        amount_pattern = re.compile(r'(?:Rs\.?|₹)\s*([0-9,]+(?:\.[0-9]{2})?)', re.IGNORECASE)
        labeled_gross = re.search(r'gross[^0-9]*(?:rs\.?|₹)?\s*([0-9,]+(?:\.[0-9]{2})?)', text, re.IGNORECASE)
        labeled_net = re.search(r'net\s*(?:pay|salary)?[^0-9]*(?:rs\.?|₹)?\s*([0-9,]+(?:\.[0-9]{2})?)', text, re.IGNORECASE)

        amounts = amount_pattern.findall(text)
        cleaned_amounts = [float(amt.replace(',', '')) for amt in amounts if amt]

        gross = float(labeled_gross.group(1).replace(',', '')) if labeled_gross else (max(cleaned_amounts) if cleaned_amounts else None)
        net = float(labeled_net.group(1).replace(',', '')) if labeled_net else None

        contact = self.extract_contact_info(text)

        return {
            "amounts_found": cleaned_amounts[:5],
            "gross_salary": gross,
            "net_salary": net,
            "email": contact["emails"][0] if contact["emails"] else None,
            "confidence": 0.75 if gross else 0.35
        }

    def parse_bank_statement(self, text: str) -> Dict[str, Any]:
        """Detect salary/payroll signals in bank statements."""
        salary_keywords = [
            "salary", "payroll", "neft salary", "salary credit", "hdfc salary", "icici salary",
            "pay credit", "salary txn", "sala ry", "wage", "stipend"
        ]
        text_lower = text.lower()
        salary_hits = sum(1 for kw in salary_keywords if kw in text_lower)

        return {
            "salary_hits": salary_hits,
            "has_salary_signal": salary_hits > 0
        }
    
    def process_document(self, file_path: str, doc_type: str) -> Dict[str, Any]:
        """
        Process document based on type.
        
        Returns:
            Dict with raw_text, structured_fields, and confidence
        """
        file_path_obj = Path(file_path)
        
        # Determine file type and extract text
        if file_path_obj.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            raw_text, ocr_confidence = self.process_image(file_path)
        elif file_path_obj.suffix.lower() == '.pdf':
            raw_text, ocr_confidence = self.process_pdf(file_path)
        else:
            return {
                "raw_text": "",
                "structured_fields": {},
                "confidence": 0.0,
                "error": f"Unsupported file type: {file_path_obj.suffix}"
            }
        
        # Parse structured fields based on doc_type
        if doc_type == "pan":
            structured_fields = self.parse_pan_card(raw_text)
            final_confidence = structured_fields.get("confidence", 0.0)
        elif doc_type == "payslip":
            structured_fields = self.parse_payslip(raw_text)
            final_confidence = structured_fields.get("confidence", 0.0)
        elif doc_type == "aadhaar":
            structured_fields = self.parse_aadhaar(raw_text)
            final_confidence = structured_fields.get("confidence", 0.0)
        elif doc_type == "bank_statement":
            structured_fields = self.parse_bank_statement(raw_text)
            final_confidence = 0.8 if structured_fields.get("has_salary_signal") else 0.3
        else:
            # Generic contact extraction
            structured_fields = self.extract_contact_info(raw_text)
            final_confidence = ocr_confidence
        
        return {
            "raw_text": raw_text,
            "structured_fields": structured_fields,
            "confidence": final_confidence,
            "text_length": len(raw_text)
        }
