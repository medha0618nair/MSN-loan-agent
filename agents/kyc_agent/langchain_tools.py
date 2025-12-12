"""
LangChain Tool wrapper for KYC/OCR Agent.
Allows orchestrator to call KYC agent as a LangChain tool.
"""
from langchain.tools import tool
from typing import Dict, Any
import requests
import json
import logging

logger = logging.getLogger(__name__)

KYC_SERVICE_URL = "http://localhost:8002"


@tool("kyc_parse")
def kyc_parse_tool(input_data: str) -> str:
    """
    Parse and extract information from KYC documents (PAN, Aadhaar, payslip, bank statements).
    
    Performs OCR, extracts structured fields, and detects faces in ID documents.
    
    Args:
        input_data: JSON string with keys: application_id, evidence_id, doc_type, file_path
        
    Returns:
        JSON string with OCR results, structured fields, face crop evidence, and validation errors
        
    Example:
        input = {
            "application_id": "app-0001",
            "evidence_id": "ev-pan-001",
            "doc_type": "pan",
            "file_path": "./data/uploads/pan_card.jpg"
        }
    """
    try:
        data = json.loads(input_data)
        
        response = requests.post(
            f"{KYC_SERVICE_URL}/kyc/parse",
            json={
                "application_id": data["application_id"],
                "evidence_id": data["evidence_id"],
                "doc_type": data["doc_type"],
                "file_path": data["file_path"]
            },
            timeout=60  # OCR can take time
        )
        
        response.raise_for_status()
        return json.dumps(response.json())
        
    except Exception as e:
        logger.error(f"KYC parse tool error: {e}")
        return json.dumps({
            "error": str(e),
            "overall_confidence": 0.0,
            "validation_errors": [f"Tool execution failed: {str(e)}"]
        })


# Export tools list for orchestrator
KYC_TOOLS = [kyc_parse_tool]
