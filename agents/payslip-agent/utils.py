"""
Utility functions for payslip income verification.
"""

import re
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def extract_numbers(text: str) -> float:
    """
    Extract numeric value from text, handling Indian currency format.
    
    Args:
        text: Text containing number (e.g., "50,000.00" or "50000")
    
    Returns:
        Float value or 0.0 if extraction fails
    """
    if not text:
        return 0.0
    
    try:
        # Remove common currency symbols and whitespace
        cleaned = re.sub(r'[^\d.-]', '', text.strip())
        if cleaned:
            return float(cleaned)
        return 0.0
    except (ValueError, TypeError):
        logger.warning(f"Could not extract number from: {text}")
        return 0.0


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    if not text:
        return ""
    return text.strip().lower()


def extract_email(text: str) -> Optional[str]:
    """Extract email from text."""
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return emails[0] if emails else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    phones = re.findall(r'\b\d{10}\b|\+91\d{10}\b', text)
    return phones[0] if phones else None


def extract_date(text: str) -> Optional[str]:
    """Extract date from text in various formats."""
    if not text:
        return None
    
    # Try common date patterns
    patterns = [
        r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # DD/MM/YYYY or DD-MM-YYYY
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # YYYY/MM/DD
        r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',  # DD Month YYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None


def extract_month_year(text: str) -> Optional[str]:
    """Extract month-year period from text."""
    if not text:
        return None
    
    # Pattern: Month Year or Mon-Mon Year
    patterns = [
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*-\s*(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None


def calculate_confidence(field_count: int, total_fields: int = 10) -> float:
    """Calculate extraction confidence based on field extraction rate."""
    if total_fields == 0:
        return 0.0
    confidence = min(1.0, field_count / total_fields)
    return round(confidence, 2)


def validate_payslip_structure(data: Dict[str, Any]) -> bool:
    """
    Validate that extracted data has minimum required structure.
    
    Args:
        data: Extracted payslip data
    
    Returns:
        True if payslip has basic structure, False otherwise
    """
    # Require at least basic pay or gross earnings
    has_earnings = data.get('gross_earnings', 0) > 0 or data.get('basic_pay', 0) > 0
    
    # Require net pay
    has_net_pay = data.get('net_pay_payslip', 0) > 0
    
    # Require employee name or ID
    has_identity = bool(data.get('employee_name')) or bool(data.get('employee_id'))
    
    return has_earnings and has_net_pay and has_identity


def sanitize_output(response_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize output for API response."""
    # Round all monetary values to 2 decimals
    monetary_fields = [
        'basic_pay', 'hra', 'special_allowance', 'conveyance', 'other_allowance',
        'gross_earnings', 'pf', 'professional_tax', 'income_tax', 'other_deductions',
        'total_deductions', 'net_pay_payslip', 'monthly_income'
    ]
    
    for field in monetary_fields:
        if field in response_dict and isinstance(response_dict[field], float):
            response_dict[field] = round(response_dict[field], 2)
    
    # Ensure confidence is between 0 and 1
    if 'income_confidence' in response_dict:
        response_dict['income_confidence'] = max(0.0, min(1.0, response_dict['income_confidence']))
    
    return response_dict
