"""
LangChain Tool wrapper for payslip verification agent.
"""

from langchain.tools import tool
from typing import Dict, Optional
import json
import logging

logger = logging.getLogger(__name__)


@tool("payslip_verification")
def payslip_verification_tool(input: Dict) -> Dict:
    """
    LangChain tool for payslip income verification.
    
    This tool processes a payslip document and extracts structured income information.
    
    Args:
        input (dict): Must contain:
            - file_path (str): Path to payslip file (PDF/PNG/JPG)
            OR
            - file_bytes (bytes): Binary payslip data
            - file_type (str, optional): "pdf", "image", or "auto" (default: "auto")
    
    Returns:
        dict: Payslip verification response with extracted income data
        {
            "payslip_present": bool,
            "employee_name": str,
            "employee_id": str,
            "designation": str,
            "department": str,
            "employer": str,
            "employer_address": str,
            "pay_period": str,
            "payment_date": str,
            "basic_pay": float,
            "hra": float,
            "special_allowance": float,
            "conveyance": float,
            "other_allowance": float,
            "gross_earnings": float,
            "pf": float,
            "professional_tax": float,
            "income_tax": float,
            "other_deductions": float,
            "total_deductions": float,
            "net_pay_payslip": float,
            "monthly_income": float,
            "income_confidence": float,
            "source": str,
            "agent_version": str,
            "ts": str
        }
        OR on error:
        {
            "error": str,
            "details": str (optional)
        }
    
    Example:
        >>> input_data = {"file_path": "/path/to/payslip.pdf"}
        >>> result = payslip_verification_tool(input_data)
    """
    try:
        from extractor import extract_payslip_data
        from utils import calculate_confidence, validate_payslip_structure, sanitize_output
        from datetime import datetime
        
        logger.info(f"payslip_verification_tool called with input: {list(input.keys())}")
        
        # Get file data
        file_bytes = None
        file_type = input.get('file_type', 'auto')
        
        if 'file_bytes' in input:
            file_bytes = input['file_bytes']
            if isinstance(file_bytes, str):
                file_bytes = file_bytes.encode()
        
        elif 'file_path' in input:
            file_path = input['file_path']
            try:
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return {"error": "payslip_missing", "details": f"Cannot read file: {e}"}
        
        else:
            return {"error": "invalid_input", "details": "Must provide 'file_path' or 'file_bytes'"}
        
        if not file_bytes:
            return {"error": "payslip_missing", "details": "No file data provided"}
        
        # Extract payslip data
        extracted_data = extract_payslip_data(file_bytes, file_type)
        
        if not extracted_data:
            return {"error": "payslip_unreadable", "details": "Failed to extract data from payslip"}
        
        # Validate
        if not validate_payslip_structure(extracted_data):
            return {"error": "payslip_unreadable", "details": "Payslip structure validation failed"}
        
        # Calculate confidence
        extracted_fields = sum(1 for v in extracted_data.values() if v)
        confidence = calculate_confidence(extracted_fields, total_fields=10)
        
        # Prepare response
        response = {
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
        
        response = sanitize_output(response)
        logger.info(f"Payslip verification successful via tool: {response.get('employee_name')}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error in payslip_verification_tool: {e}", exc_info=True)
        return {"error": "payslip_unreadable", "details": str(e)}


# Alternative: Create a structured tool class for more complex LangChain integration
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class PayslipVerificationInput(BaseModel):
    """Input schema for payslip verification tool."""
    file_path: Optional[str] = Field(None, description="Path to payslip file")
    file_type: str = Field(default="auto", description="File type: pdf, image, or auto")


class PayslipVerificationTool(BaseTool):
    """
    LangChain tool for payslip verification using tool class.
    Enables structured input validation and better integration with agents.
    """
    name: str = "payslip_verification"
    description: str = "Extract structured income information from a payslip (PDF/PNG/JPG)"
    args_schema: type[PayslipVerificationInput] = PayslipVerificationInput
    
    def _run(self, file_path: str, file_type: str = "auto") -> Dict:
        """Execute the payslip verification."""
        return payslip_verification_tool({"file_path": file_path, "file_type": file_type})
    
    async def _arun(self, file_path: str, file_type: str = "auto") -> Dict:
        """Async execution of payslip verification."""
        return self._run(file_path, file_type)
