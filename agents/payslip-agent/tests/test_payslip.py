"""
Pytest tests for payslip income verification agent.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import json
from io import BytesIO


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def sample_payslip_ocr_text():
    """Sample OCR text extracted from a payslip."""
    return """
    PAYSLIP FOR THE MONTH OF MARCH 2024
    
    Employee Details:
    Employee Name: John Doe
    Employee ID: EMP12345
    Department: Engineering
    Designation: Senior Software Engineer
    Company: Tech Solutions India Pvt Ltd
    Address: 123 Tech Park, Bangalore, India
    
    Pay Period: 01-Mar-2024 to 31-Mar-2024
    Payment Date: 05-Apr-2024
    
    EARNINGS:
    Basic Pay: 50,000.00
    House Rent Allowance (HRA): 15,000.00
    Special Allowance: 5,000.00
    Conveyance Allowance: 1,500.00
    Other Allowance: 500.00
    Gross Earnings: 72,000.00
    
    DEDUCTIONS:
    Provident Fund (PF): 6,000.00
    Professional Tax: 200.00
    Income Tax: 8,000.00
    Other Deductions: 500.00
    Total Deductions: 14,700.00
    
    NET PAY: 57,300.00
    """


@pytest.fixture
def sample_payslip_dict():
    """Sample parsed payslip data."""
    return {
        'employee_name': 'John Doe',
        'employee_id': 'EMP12345',
        'department': 'Engineering',
        'designation': 'Senior Software Engineer',
        'employer': 'Tech Solutions India Pvt Ltd',
        'employer_address': '123 Tech Park, Bangalore, India',
        'pay_period': '01-Mar-2024 to 31-Mar-2024',
        'payment_date': '05-Apr-2024',
        'basic_pay': 50000.0,
        'hra': 15000.0,
        'special_allowance': 5000.0,
        'conveyance': 1500.0,
        'other_allowance': 500.0,
        'gross_earnings': 72000.0,
        'pf': 6000.0,
        'professional_tax': 200.0,
        'income_tax': 8000.0,
        'other_deductions': 500.0,
        'total_deductions': 14700.0,
        'net_pay_payslip': 57300.0,
    }


@pytest.fixture
def sample_payslip_response(sample_payslip_dict):
    """Sample full payslip verification response."""
    return {
        'payslip_present': True,
        'employee_name': sample_payslip_dict['employee_name'],
        'employee_id': sample_payslip_dict['employee_id'],
        'designation': sample_payslip_dict['designation'],
        'department': sample_payslip_dict['department'],
        'employer': sample_payslip_dict['employer'],
        'employer_address': sample_payslip_dict['employer_address'],
        'pay_period': sample_payslip_dict['pay_period'],
        'payment_date': sample_payslip_dict['payment_date'],
        'basic_pay': 50000.0,
        'hra': 15000.0,
        'special_allowance': 5000.0,
        'conveyance': 1500.0,
        'other_allowance': 500.0,
        'gross_earnings': 72000.0,
        'pf': 6000.0,
        'professional_tax': 200.0,
        'income_tax': 8000.0,
        'other_deductions': 500.0,
        'total_deductions': 14700.0,
        'net_pay_payslip': 57300.0,
        'monthly_income': 57300.0,
        'income_confidence': 1.0,
        'source': 'payslip_only',
        'agent_version': 'payslip-v1',
        'ts': datetime.utcnow().isoformat(),
    }


# ==============================================================================
# TESTS FOR utils.py
# ==============================================================================

class TestExtractNumbers:
    """Test extract_numbers function."""
    
    def test_extract_basic_amount(self):
        """Test extracting basic currency amount."""
        from utils import extract_numbers
        result = extract_numbers("50,000.00")
        assert result == 50000.0
    
    def test_extract_amount_with_rupee_symbol(self):
        """Test extracting amount with rupee symbol."""
        from utils import extract_numbers
        result = extract_numbers("₹50,000.00")
        assert result == 50000.0
    
    def test_extract_amount_without_decimals(self):
        """Test extracting amount without decimal places."""
        from utils import extract_numbers
        result = extract_numbers("50000")
        assert result == 50000.0
    
    def test_extract_from_text(self):
        """Test extracting amount from descriptive text."""
        from utils import extract_numbers
        result = extract_numbers("Basic Pay: 50,000.00")
        assert result == 50000.0
    
    def test_extract_no_match(self):
        """Test when no amount is found."""
        from utils import extract_numbers
        result = extract_numbers("No amount here")
        assert result == 0.0


class TestExtractDate:
    """Test extract_date function."""
    
    def test_extract_date_dd_mmm_yyyy(self):
        """Test extracting date in DD-MMM-YYYY format."""
        from utils import extract_date
        result = extract_date("Payment Date: 05-Apr-2024")
        assert result == "05-Apr-2024"
    
    def test_extract_date_dd_mm_yyyy(self):
        """Test extracting date in DD/MM/YYYY format."""
        from utils import extract_date
        result = extract_date("Date: 05/04/2024")
        assert result is not None
    
    def test_extract_date_no_match(self):
        """Test when no date is found."""
        from utils import extract_date
        result = extract_date("No date here")
        assert result is None


class TestCalculateConfidence:
    """Test calculate_confidence function."""
    
    def test_confidence_all_fields_present(self):
        """Test confidence when all fields are present."""
        from utils import calculate_confidence
        confidence = calculate_confidence(10, total_fields=10)
        assert confidence == 1.0
    
    def test_confidence_half_fields(self):
        """Test confidence when half fields are present."""
        from utils import calculate_confidence
        confidence = calculate_confidence(5, total_fields=10)
        assert confidence == 0.5
    
    def test_confidence_no_fields(self):
        """Test confidence when no fields are present."""
        from utils import calculate_confidence
        confidence = calculate_confidence(0, total_fields=10)
        assert confidence == 0.0
    
    def test_confidence_clamped(self):
        """Test confidence is clamped to [0, 1]."""
        from utils import calculate_confidence
        confidence = calculate_confidence(15, total_fields=10)
        assert confidence <= 1.0


class TestValidatePayslipStructure:
    """Test validate_payslip_structure function."""
    
    def test_valid_structure(self, sample_payslip_dict):
        """Test with valid payslip structure."""
        from utils import validate_payslip_structure
        assert validate_payslip_structure(sample_payslip_dict)
    
    def test_missing_required_fields(self):
        """Test with missing required fields."""
        from utils import validate_payslip_structure
        incomplete = {'employee_name': 'John Doe'}
        assert not validate_payslip_structure(incomplete)
    
    def test_empty_dict(self):
        """Test with empty dictionary."""
        from utils import validate_payslip_structure
        assert not validate_payslip_structure({})


class TestSanitizeOutput:
    """Test sanitize_output function."""
    
    def test_sanitize_rounds_monetary_fields(self, sample_payslip_response):
        """Test that monetary fields are rounded to 2 decimals."""
        from utils import sanitize_output
        sample_payslip_response['basic_pay'] = 50000.126
        sample_payslip_response['income_confidence'] = 0.9543
        result = sanitize_output(sample_payslip_response)
        
        assert result['basic_pay'] == 50000.13
        assert result['income_confidence'] == 0.95
    
    def test_sanitize_clamps_confidence(self, sample_payslip_response):
        """Test that confidence is clamped to [0, 1]."""
        from utils import sanitize_output
        sample_payslip_response['income_confidence'] = 1.5
        result = sanitize_output(sample_payslip_response)
        
        assert result['income_confidence'] <= 1.0
    
    def test_sanitize_preserves_strings(self, sample_payslip_response):
        """Test that string fields are preserved."""
        from utils import sanitize_output
        result = sanitize_output(sample_payslip_response)
        
        assert result['employee_name'] == 'John Doe'
        assert result['employee_id'] == 'EMP12345'


# ==============================================================================
# TESTS FOR extractor.py
# ==============================================================================

class TestParsePayslipText:
    """Test parse_payslip_text function."""
    
    def test_parse_sample_payslip(self, sample_payslip_ocr_text, sample_payslip_dict):
        """Test parsing sample payslip text."""
        from extractor import parse_payslip_text
        result = parse_payslip_text(sample_payslip_ocr_text)
        
        assert result['employee_name'] == sample_payslip_dict['employee_name']
        assert result['basic_pay'] == sample_payslip_dict['basic_pay']
        assert result['gross_earnings'] == sample_payslip_dict['gross_earnings']
        assert result['net_pay_payslip'] == sample_payslip_dict['net_pay_payslip']
    
    def test_parse_empty_text(self):
        """Test parsing empty text."""
        from extractor import parse_payslip_text
        result = parse_payslip_text("")
        assert result['employee_name'] is None
    
    def test_parse_extracts_all_earnings(self, sample_payslip_ocr_text):
        """Test that all earnings are extracted."""
        from extractor import parse_payslip_text
        result = parse_payslip_text(sample_payslip_ocr_text)
        
        assert result['basic_pay'] == 50000.0
        assert result['hra'] == 15000.0
        assert result['special_allowance'] == 5000.0
        assert result['conveyance'] == 1500.0
        assert result['other_allowance'] == 500.0
    
    def test_parse_extracts_all_deductions(self, sample_payslip_ocr_text):
        """Test that all deductions are extracted."""
        from extractor import parse_payslip_text
        result = parse_payslip_text(sample_payslip_ocr_text)
        
        assert result['pf'] == 6000.0
        assert result['professional_tax'] == 200.0
        assert result['income_tax'] == 8000.0
        assert result['other_deductions'] == 500.0


class TestGenerateSampleOCRText:
    """Test generate_sample_ocr_text function."""
    
    def test_generates_text(self):
        """Test that sample text is generated."""
        from extractor import generate_sample_ocr_text
        text = generate_sample_ocr_text()
        
        assert text is not None
        assert len(text) > 0
        assert "Employee" in text
    
    def test_generated_text_contains_earnings(self):
        """Test that generated text contains earnings."""
        from extractor import generate_sample_ocr_text
        text = generate_sample_ocr_text()
        
        assert "Basic" in text or "basic" in text
        assert "HRA" in text or "hra" in text
    
    def test_generated_text_parseable(self):
        """Test that generated text can be parsed."""
        from extractor import generate_sample_ocr_text, parse_payslip_text
        text = generate_sample_ocr_text()
        result = parse_payslip_text(text)
        
        assert result['employee_name'] is not None
        assert result['basic_pay'] > 0


# ==============================================================================
# TESTS FOR main.py (FastAPI endpoints)
# ==============================================================================

@pytest.fixture
def client():
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


class TestHealthEndpoint:
    """Test /health endpoint."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()['status'] == 'ok'


class TestTestEndpoint:
    """Test POST /payslip/test endpoint."""
    
    def test_test_endpoint_success(self, client):
        """Test demo endpoint with sample data."""
        response = client.post("/payslip/test")
        assert response.status_code == 200
        
        data = response.json()
        assert 'payslip_present' in data
        assert data['payslip_present'] is True
        assert data['employee_name'] is not None
    
    def test_test_endpoint_response_schema(self, client):
        """Test that test endpoint returns correct schema."""
        response = client.post("/payslip/test")
        data = response.json()
        
        required_fields = [
            'payslip_present', 'employee_name', 'basic_pay',
            'gross_earnings', 'net_pay_payslip', 'income_confidence',
            'source', 'agent_version', 'ts'
        ]
        
        for field in required_fields:
            assert field in data


@pytest.mark.skip(reason="Requires actual file upload")
class TestVerifyEndpoint:
    """Test POST /payslip/verify endpoint."""
    
    def test_verify_endpoint_missing_file(self, client):
        """Test verify endpoint without file."""
        response = client.post("/payslip/verify")
        assert response.status_code == 400
        assert 'error' in response.json()
    
    def test_verify_endpoint_invalid_format(self, client):
        """Test verify endpoint with invalid file format."""
        response = client.post(
            "/payslip/verify",
            files={"payslip": ("test.txt", b"invalid content", "text/plain")}
        )
        assert response.status_code == 400
        assert 'error' in response.json()


# ==============================================================================
# TESTS FOR tool_wrapper.py
# ==============================================================================

class TestPayslipVerificationTool:
    """Test payslip_verification_tool function."""
    
    @patch('tool_wrapper.extract_payslip_data')
    def test_tool_with_valid_input(self, mock_extract, sample_payslip_dict):
        """Test tool with valid file path input."""
        from tool_wrapper import payslip_verification_tool
        
        mock_extract.return_value = sample_payslip_dict
        
        result = payslip_verification_tool({'file_path': '/fake/path.pdf'})
        
        assert result['payslip_present'] is True
        assert result['employee_name'] == 'John Doe'
        assert 'ts' in result
        assert 'agent_version' in result
    
    def test_tool_missing_file(self):
        """Test tool when file doesn't exist."""
        from tool_wrapper import payslip_verification_tool
        
        result = payslip_verification_tool({'file_path': '/nonexistent/file.pdf'})
        
        assert 'error' in result
        assert result['error'] == 'payslip_missing'
    
    def test_tool_missing_input(self):
        """Test tool with missing required input."""
        from tool_wrapper import payslip_verification_tool
        
        result = payslip_verification_tool({})
        
        assert 'error' in result
        assert result['error'] == 'invalid_input'
    
    @patch('tool_wrapper.extract_payslip_data')
    def test_tool_returns_iso_timestamp(self, mock_extract, sample_payslip_dict):
        """Test that tool returns ISO format timestamp."""
        from tool_wrapper import payslip_verification_tool
        
        mock_extract.return_value = sample_payslip_dict
        
        result = payslip_verification_tool({'file_path': '/fake/path.pdf'})
        
        ts = result['ts']
        # Should be parseable as ISO format
        datetime.fromisoformat(ts)


# ==============================================================================
# INTEGRATION TESTS
# ==============================================================================

class TestIntegration:
    """Integration tests across modules."""
    
    def test_end_to_end_payslip_extraction(self, sample_payslip_ocr_text):
        """Test full extraction pipeline from text to response."""
        from extractor import parse_payslip_text
        from utils import sanitize_output, validate_payslip_structure
        
        parsed = parse_payslip_text(sample_payslip_ocr_text)
        assert validate_payslip_structure(parsed)
        
        response = {
            'payslip_present': True,
            'employee_name': parsed.get('employee_name'),
            'basic_pay': parsed.get('basic_pay', 0.0),
            'gross_earnings': parsed.get('gross_earnings', 0.0),
            'net_pay_payslip': parsed.get('net_pay_payslip', 0.0),
            'income_confidence': 0.95,
            'source': 'payslip_only',
            'agent_version': 'payslip-v1',
            'ts': datetime.utcnow().isoformat(),
        }
        
        sanitized = sanitize_output(response)
        assert sanitized['payslip_present'] is True
        assert sanitized['employee_name'] == 'John Doe'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
