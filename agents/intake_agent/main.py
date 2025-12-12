"""
Intake / RAG Chat Agent - FastAPI Service
Powered by LangChain for RAG, slot-filling, and conversational memory.
"""
import os
import logging
import math
from datetime import datetime
from typing import Dict, Any
import requests

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import (
    ConverseRequest, SlotUpdateRequest, SubmitRequest, UploadRequest,
    IntakeResponse, ActionItem, HealthResponse
)
from langchain_pipeline import IntakePipeline
from dotenv import load_dotenv, find_dotenv

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Intake Agent",
    description="LangChain-powered RAG and slot-filling agent for loan intake",
    version="intake-v1"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment from nearest .env (repo root)
load_dotenv(find_dotenv(), override=False)

# Initialize LangChain pipeline
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
DOCS_PATH = os.getenv("DOCS_PATH", "./data/docs")
KYC_SERVICE_URL = os.getenv("KYC_SERVICE_URL", "http://localhost:8002")

pipeline = IntakePipeline(
    groq_api_key=GROQ_API_KEY,
    redis_host=REDIS_HOST,
    redis_port=REDIS_PORT,
    docs_path=DOCS_PATH
)

logger.info("Intake Agent initialized with LangChain pipeline")
if GROQ_API_KEY and GROQ_API_KEY != "your-groq-api-key-here":
    logger.info("GROQ_API_KEY loaded from environment (.env or process env)")
else:
    logger.warning("GROQ_API_KEY is missing or default; Groq calls will fail. Set it in .env or the environment.")


def log_with_app_id(app_id: str, message: str, level: str = "info"):
    """Helper to log with application_id prefix."""
    log_msg = f"[{app_id}] {message}"
    if level == "info":
        logger.info(log_msg)
    elif level == "error":
        logger.error(log_msg)
    elif level == "warning":
        logger.warning(log_msg)


def _normalize_str(val: str) -> str:
    """Lowercase alphanumeric normalization for fuzzy equality."""
    return "".join(ch for ch in val.lower() if ch.isalnum()) if val else ""


def compare_slots_with_kyc(slots: Dict[str, Any], doc_type: str, kyc_result: Dict[str, Any]) -> list[str]:
    """Return mismatch messages between collected slots and KYC OCR output.
    Only validates PAN and Aadhaar numbers - name/income matching handled by separate team.
    """
    mismatches: list[str] = []
    structured = (kyc_result or {}).get("ocr", {}).get("structured_fields", {})

    if doc_type == "pan":
        pan_slot = slots.get("pan_number")
        pan_ocr = structured.get("pan_number")
        if pan_slot and pan_ocr and _normalize_str(pan_slot) != _normalize_str(pan_ocr):
            mismatches.append(f"PAN mismatch: provided {pan_slot} vs OCR {pan_ocr}")

    if doc_type == "aadhaar":
        aadhaar_slot = slots.get("aadhaar_number")
        aadhaar_ocr = structured.get("aadhaar_number")
        if aadhaar_slot and aadhaar_ocr and _normalize_str(aadhaar_slot) != _normalize_str(aadhaar_ocr):
            mismatches.append(f"Aadhaar mismatch: provided {aadhaar_slot} vs OCR {aadhaar_ocr}")

    # Payslip/bank statement: no validation, just pass through OCR data
    return mismatches


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Fast health check endpoint."""
    return HealthResponse()


@app.post("/chat/converse", response_model=IntakeResponse)
async def converse(request: ConverseRequest):
    """
    Conversational RAG endpoint.
    Handles natural language queries using LangChain RAG retrieval.
    """
    log_with_app_id(request.application_id, f"Converse request: {request.user_message}")
    
    try:
        # Get conversational reply with RAG
        reply_data = pipeline.conversational_reply(
            user_message=request.user_message,
            conversation_id=request.conversation_id,
            application_id=request.application_id
        )
        
        # Also extract slots opportunistically
        slot_data = pipeline.extract_slots(
            user_message=request.user_message,
            application_id=request.application_id,
            conversation_id=request.conversation_id
        )
        
        # Get current slots
        current_slots = pipeline._get_slots(request.application_id)
        
        # Determine required uploads
        required_uploads = []
        if current_slots.get("pan_number"):
            required_uploads.append("pan")
        if current_slots.get("employment_status") == "salaried":
            required_uploads.extend(["payslip", "bank_statement"])
        
        # Generate actions
        actions = []
        for upload in required_uploads:
            if not pipeline.has_upload(request.application_id, upload):
                actions.append(ActionItem(
                    type="upload_request",
                    doc_type=upload,
                    message=f"Please upload your {upload.upper()} document"
                ))
        
        response = IntakeResponse(
            application_id=request.application_id,
            conversation_id=request.conversation_id,
            slots=current_slots,
            required_uploads=required_uploads,
            actions=actions,
            assistant_reply=reply_data["assistant_reply"],
            rag_context=reply_data["rag_context"],
            next_prompt=slot_data.next_question
        )
        
        log_with_app_id(request.application_id, f"Converse response generated, slots: {len(current_slots)}")
        return response
        
    except Exception as e:
        log_with_app_id(request.application_id, f"Converse error: {str(e)}", level="error")
        raise HTTPException(status_code=500, detail=f"Conversation processing failed: {str(e)}")


@app.post("/chat/slot", response_model=IntakeResponse)
async def update_slot(request: SlotUpdateRequest):
    """
    Explicit slot update endpoint.
    Used by orchestrator to set specific slot values.
    """
    log_with_app_id(request.application_id, f"Slot update: {request.slot_name} = {request.slot_value}")
    
    try:
        # Save slot
        pipeline._save_slot(request.application_id, request.slot_name, request.slot_value)
        
        # Get updated slots
        current_slots = pipeline._get_slots(request.application_id)
        
        # Check completeness
        required_slots = ["full_name", "email", "phone", "loan_amount", "loan_purpose"]
        missing_slots = [s for s in required_slots if s not in current_slots]
        
        # Determine next action
        actions = []
        next_prompt = None
        
        if missing_slots:
            next_prompt = f"Great! Now, could you provide your {missing_slots[0].replace('_', ' ')}?"
            actions.append(ActionItem(
                type="slot_request",
                message=next_prompt
            ))
        else:
            actions.append(ActionItem(
                type="ready_for_upload",
                message="All information collected. Please proceed with document upload."
            ))
        
        response = IntakeResponse(
            application_id=request.application_id,
            conversation_id=request.conversation_id,
            slots=current_slots,
            required_uploads=["pan", "payslip", "bank_statement"],
            actions=actions,
            assistant_reply=f"Updated {request.slot_name} successfully.",
            next_prompt=next_prompt
        )
        
        log_with_app_id(request.application_id, f"Slot updated, total slots: {len(current_slots)}")
        return response
        
    except Exception as e:
        log_with_app_id(request.application_id, f"Slot update error: {str(e)}", level="error")
        raise HTTPException(status_code=500, detail=f"Slot update failed: {str(e)}")


@app.post("/chat/upload", response_model=IntakeResponse)
async def register_upload(request: UploadRequest):
    """
    Register an uploaded document and trigger downstream KYC parsing.
    Returns intake state plus the KYC agent's OCR/face evidence.
    """
    log_with_app_id(request.application_id, f"Upload received: {request.doc_type} -> {request.file_path}")

    evidence_id = request.evidence_id or f"{request.doc_type}-{request.conversation_id}"

    # Mark upload for required_uploads logic
    pipeline.mark_upload(request.application_id, request.doc_type)

    kyc_result: Dict[str, Any] | None = None
    actions = []

    try:
        kyc_response = requests.post(
            f"{KYC_SERVICE_URL}/kyc/parse",
            json={
                "application_id": request.application_id,
                "evidence_id": evidence_id,
                "doc_type": request.doc_type,
                "file_path": request.file_path,
            },
            timeout=60,
        )
        kyc_response.raise_for_status()
        kyc_result = kyc_response.json()

        if kyc_result.get("validation_errors"):
            actions.append(ActionItem(
                type="kyc_validation_error",
                doc_type=request.doc_type,
                message="; ".join(kyc_result.get("validation_errors", []))
            ))
        else:
            actions.append(ActionItem(
                type="kyc_success",
                doc_type=request.doc_type,
                message="KYC parsed successfully"
            ))

    except Exception as e:
        log_with_app_id(request.application_id, f"KYC call failed: {e}", level="error")
        raise HTTPException(status_code=502, detail=f"KYC parsing failed: {e}")

    # Current slots and outstanding uploads
    current_slots = pipeline._get_slots(request.application_id)
    required_uploads = []
    if current_slots.get("pan_number"):
        required_uploads.append("pan")
    if current_slots.get("employment_status") == "salaried":
        required_uploads.extend(["payslip", "bank_statement"])

    remaining_actions = []
    for upload in required_uploads:
        if not pipeline.has_upload(request.application_id, upload):
            remaining_actions.append(ActionItem(
                type="upload_request",
                doc_type=upload,
                message=f"Please upload your {upload.upper()} document"
            ))

    # Slot vs OCR mismatch checks
    slot_mismatches = compare_slots_with_kyc(current_slots, request.doc_type, kyc_result)
    for msg in slot_mismatches:
        actions.append(ActionItem(
            type="kyc_slot_mismatch",
            doc_type=request.doc_type,
            message=msg
        ))

    actions.extend(remaining_actions)

    response = IntakeResponse(
        application_id=request.application_id,
        conversation_id=request.conversation_id,
        slots=current_slots,
        required_uploads=required_uploads,
        actions=actions,
        assistant_reply="Document received and sent for KYC parsing.",
        kyc_result=kyc_result,
    )

    log_with_app_id(request.application_id, f"Upload handled, actions={len(actions)}")
    return response


@app.post("/chat/submit", response_model=IntakeResponse)
async def submit_application(request: SubmitRequest):
    """
    Finalize and submit application.
    Validates all required slots and uploads are complete.
    """
    log_with_app_id(request.application_id, "Application submission request")
    
    try:
        # Get current slots
        current_slots = pipeline._get_slots(request.application_id)
        
        # Validate required slots
        required_slots = ["full_name", "email", "phone", "loan_amount", "loan_purpose"]
        missing_slots = [s for s in required_slots if s not in current_slots]
        
        actions = []
        
        if missing_slots:
            actions.append(ActionItem(
                type="validation_error",
                message=f"Missing required information: {', '.join(missing_slots)}"
            ))
            
            response = IntakeResponse(
                application_id=request.application_id,
                conversation_id=request.conversation_id,
                slots=current_slots,
                required_uploads=["pan", "payslip", "bank_statement"],
                actions=actions,
                assistant_reply="Cannot submit yet. Please complete all required fields."
            )
        else:
            actions.append(ActionItem(
                type="submit_success",
                message="Application submitted successfully. Proceeding to KYC verification."
            ))
            
            response = IntakeResponse(
                application_id=request.application_id,
                conversation_id=request.conversation_id,
                slots=current_slots,
                required_uploads=["pan", "payslip", "bank_statement"],
                actions=actions,
                assistant_reply="Thank you! Your application has been submitted. We'll proceed with document verification next."
            )
        
        log_with_app_id(request.application_id, f"Application submission result: {actions[0].type}")
        return response
        
    except Exception as e:
        log_with_app_id(request.application_id, f"Submission error: {str(e)}", level="error")
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")


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
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
