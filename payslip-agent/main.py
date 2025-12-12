"""
FastAPI application for Payslip Income Verification Agent.
"""

import logging
from datetime import datetime
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from io import BytesIO

from models import PayslipVerificationResponse, PayslipErrorResponse
from extractor import extract_payslip_data, generate_sample_ocr_text, parse_payslip_text
from utils import calculate_confidence, validate_payslip_structure, sanitize_output

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Payslip Income Verification Agent",
    description="Extracts structured income information from payslips (PDF/PNG/JPG)",
    version="payslip-v1"
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "payslip-income-verification-agent",
        "version": "payslip-v1",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/payslip/verify", response_model=PayslipVerificationResponse)
async def verify_payslip(payslip_file: UploadFile = File(...)) -> PayslipVerificationResponse:
    """
    Verify payslip and extract income information.
    
    **Request:**
    - `payslip_file`: Binary file (PDF/PNG/JPG)
    
    **Response:**
    - Structured payslip data with income components and confidence score
    
    **Error Responses:**
    - `payslip_unreadable`: OCR extraction failed
    - `payslip_missing`: No valid payslip detected
    """
    try:
        # Read file
        if not payslip_file:
            logger.error("No file provided")
            raise HTTPException(status_code=400, detail="payslip_missing")
        
        file_bytes = await payslip_file.read()
        if not file_bytes:
            logger.error("Empty file")
            raise HTTPException(status_code=400, detail="payslip_missing")
        
        logger.info(f"Processing payslip file: {payslip_file.filename} ({len(file_bytes)} bytes)")
        
        # Extract data from payslip
        extracted_data = extract_payslip_data(file_bytes)
        
        if not extracted_data:
            logger.error("Failed to extract data from payslip")
            raise HTTPException(status_code=422, detail="payslip_unreadable")
        
        # Validate structure
        if not validate_payslip_structure(extracted_data):
            logger.warning("Extracted data does not meet minimum payslip structure requirements")
            raise HTTPException(status_code=422, detail="payslip_unreadable")
        
        # Calculate confidence
        extracted_fields = sum(1 for v in extracted_data.values() if v)
        confidence = calculate_confidence(extracted_fields, total_fields=10)
        
        # Prepare response
        response_data = {
            'payslip_present': True,
            'employee_name': extracted_data.get('employee_name'),
            'employee_id': extracted_data.get('employee_id'),
            'designation': extracted_data.get('designation'),
            'department': extracted_data.get('department'),
            'employer': extracted_data.get('employer'),
            'employer_address': extracted_data.get('employer_address'),
            'pay_period': extracted_data.get('pay_period'),
            'payment_date': extracted_data.get('payment_date'),
            'basic_pay': extracted_data.get('basic_pay', 0.0),
            'hra': extracted_data.get('hra', 0.0),
            'special_allowance': extracted_data.get('special_allowance', 0.0),
            'conveyance': extracted_data.get('conveyance', 0.0),
            'other_allowance': extracted_data.get('other_allowance', 0.0),
            'gross_earnings': extracted_data.get('gross_earnings', 0.0),
            'pf': extracted_data.get('pf', 0.0),
            'professional_tax': extracted_data.get('professional_tax', 0.0),
            'income_tax': extracted_data.get('income_tax', 0.0),
            'other_deductions': extracted_data.get('other_deductions', 0.0),
            'total_deductions': extracted_data.get('total_deductions', 0.0),
            'net_pay_payslip': extracted_data.get('net_pay_payslip', 0.0),
            'monthly_income': extracted_data.get('net_pay_payslip', 0.0),
            'income_confidence': confidence,
            'source': 'payslip_only',
            'agent_version': 'payslip-v1',
            'ts': datetime.utcnow().isoformat()
        }
        
        # Sanitize output
        response_data = sanitize_output(response_data)
        
        logger.info(f"Payslip verification successful: {response_data['employee_name']} - Net Pay: {response_data['net_pay_payslip']}")
        
        return PayslipVerificationResponse(**response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in verify_payslip: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="payslip_unreadable")


@app.post("/payslip/test")
async def test_payslip_extraction():
    """
    Test endpoint that uses sample OCR text for demonstration.
    
    Returns: Sample payslip verification response
    """
    try:
        # Generate sample OCR text
        sample_text = generate_sample_ocr_text()
        logger.info("Processing test payslip with sample OCR text")
        
        # Parse the text
        from extractor import parse_payslip_text
        extracted_data = parse_payslip_text(sample_text)
        
        # Calculate confidence
        extracted_fields = sum(1 for v in extracted_data.values() if v)
        confidence = calculate_confidence(extracted_fields, total_fields=10)
        
        # Prepare response
        response_data = {
            'payslip_present': True,
            'employee_name': extracted_data.get('employee_name'),
            'employee_id': extracted_data.get('employee_id'),
            'designation': extracted_data.get('designation'),
            'department': extracted_data.get('department'),
            'employer': extracted_data.get('employer'),
            'employer_address': extracted_data.get('employer_address'),
            'pay_period': extracted_data.get('pay_period'),
            'payment_date': extracted_data.get('payment_date'),
            'basic_pay': extracted_data.get('basic_pay', 0.0),
            'hra': extracted_data.get('hra', 0.0),
            'special_allowance': extracted_data.get('special_allowance', 0.0),
            'conveyance': extracted_data.get('conveyance', 0.0),
            'other_allowance': extracted_data.get('other_allowance', 0.0),
            'gross_earnings': extracted_data.get('gross_earnings', 0.0),
            'pf': extracted_data.get('pf', 0.0),
            'professional_tax': extracted_data.get('professional_tax', 0.0),
            'income_tax': extracted_data.get('income_tax', 0.0),
            'other_deductions': extracted_data.get('other_deductions', 0.0),
            'total_deductions': extracted_data.get('total_deductions', 0.0),
            'net_pay_payslip': extracted_data.get('net_pay_payslip', 0.0),
            'monthly_income': extracted_data.get('net_pay_payslip', 0.0),
            'income_confidence': confidence,
            'source': 'payslip_only',
            'agent_version': 'payslip-v1',
            'ts': datetime.utcnow().isoformat()
        }
        
        response_data = sanitize_output(response_data)
        return JSONResponse(status_code=200, content=response_data)
    
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        return JSONResponse(status_code=500, content={"error": "test_failed", "details": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
