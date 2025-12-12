"""
KYC / OCR Agent - FastAPI Service
Handles document parsing, OCR, and face detection for loan verification.
Exposed as LangChain Tool for orchestrator integration.
"""
import os
import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import (
    KYCParseRequest, KYCParseResponse,
    OCRData, FaceCropEvidence, HealthResponse
)
from ocr_utils import OCRProcessor
from vision_utils import FaceDetector
from file_utils import compute_sha256, ensure_directory, save_face_crop, validate_file_exists

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="KYC/OCR Agent",
    description="Document parsing and verification agent with OCR and face detection",
    version="kyc-v1"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
ocr_processor = OCRProcessor()
face_detector = FaceDetector()

# Storage paths
UPLOAD_BASE = os.getenv("UPLOAD_PATH", "./data/uploads")
CROPS_BASE = os.getenv("CROPS_PATH", "./data/crops")

ensure_directory(UPLOAD_BASE)
ensure_directory(CROPS_BASE)

logger.info("KYC/OCR Agent initialized")


def log_with_app_id(app_id: str, message: str, level: str = "info"):
    """Helper to log with application_id prefix."""
    log_msg = f"[{app_id}] {message}"
    if level == "info":
        logger.info(log_msg)
    elif level == "error":
        logger.error(log_msg)
    elif level == "warning":
        logger.warning(log_msg)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Fast health check endpoint."""
    return HealthResponse()


@app.post("/kyc/parse", response_model=KYCParseResponse)
async def parse_document(request: KYCParseRequest):
    """
    Parse and extract information from KYC documents.
    
    Supports:
    - PAN card (with face extraction)
    - Payslip
    - Bank statement
    - Aadhaar (with face extraction)
    """
    log_with_app_id(request.application_id, f"Parse request: {request.doc_type} - {request.evidence_id}")
    
    try:
        # Validate file
        if not validate_file_exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Compute file hash
        file_sha256 = compute_sha256(request.file_path)
        
        # Process OCR
        log_with_app_id(request.application_id, f"Starting OCR for {request.doc_type}")
        ocr_result = ocr_processor.process_document(request.file_path, request.doc_type)
        
        ocr_data = OCRData(
            raw_text=ocr_result["raw_text"],
            structured_fields=ocr_result["structured_fields"],
            confidence_scores={"overall": ocr_result["confidence"]}
        )
        
        # No face detection — focus on OCR data only
        face_evidence = None
        overall_confidence = ocr_result["confidence"]
        
        # Validation — check for required ID numbers and names
        validation_errors = []
        
        if request.doc_type == "pan":
            if not ocr_data.structured_fields.get("pan_number"):
                validation_errors.append("PAN number not found in document")
            if not ocr_data.structured_fields.get("name"):
                validation_errors.append("Name not found in PAN document")

        if request.doc_type == "aadhaar":
            if not ocr_data.structured_fields.get("aadhaar_number"):
                validation_errors.append("Aadhaar number not found or invalid")
            if not ocr_data.structured_fields.get("name"):
                validation_errors.append("Name not found in Aadhaar document")
        
        if validation_errors:
            log_with_app_id(request.application_id, f"Validation errors: {validation_errors}", level="warning")
        
        # Build response
        response = KYCParseResponse(
            application_id=request.application_id,
            evidence_id=request.evidence_id,
            doc_type=request.doc_type,
            file_uri=request.file_path,
            file_sha256=file_sha256,
            ocr=ocr_data,
            id_crop_evidence=face_evidence,
            overall_confidence=overall_confidence,
            validation_errors=validation_errors
        )
        
        log_with_app_id(
            request.application_id,
            f"Parse complete: confidence={overall_confidence:.2f}, errors={len(validation_errors)}"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        log_with_app_id(request.application_id, f"Parse error: {str(e)}", level="error")
        raise HTTPException(status_code=500, detail=f"Document parsing failed: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
