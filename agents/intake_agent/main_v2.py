#!/usr/bin/env python3
"""
Intake Agent v2 - FastAPI Server
Strict conversational flow with file uploads
Runs on port 8001
"""

import os
import logging
from typing import Optional
from uuid import uuid4
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chat_flow_v2 import ConversationFlowV2, QuestionStage
from storage_v2 import ConversationStorageV2
from ocr_extractor import extract_document_data

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Intake Agent v2",
    description="Strict sequential conversation with file uploads",
    version="2.0"
)

origins = [
    "http://localhost:3001",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
flow = ConversationFlowV2()
storage = ConversationStorageV2()

# Request/Response Models
class StartRequest(BaseModel):
    application_id: Optional[str] = None

class MessageRequest(BaseModel):
    application_id: str
    user_message: str

class MessageResponse(BaseModel):
    application_id: str
    bot_message: str
    current_stage: str
    next_stage: Optional[str]
    completed: bool
    collected_data: dict

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "intake-agent", "port": 8001}

@app.post("/start")
async def start_conversation(request: StartRequest) -> MessageResponse:
    """Start or resume conversation"""
    
    app_id = request.application_id or f"APP-{uuid4().hex[:12].upper()}"
    
    # Try to load existing conversation
    state = storage.load_conversation(app_id)
    
    if not state:
        # New conversation
        state = storage.initialize_conversation(app_id)
        logger.info(f"Started new conversation: {app_id}")
    else:
        logger.info(f"Resumed conversation: {app_id}")
    
    # Get first question
    current_stage = state.get("current_stage", "loan_type")
    question_enum = QuestionStage[current_stage.upper()]
    question_text = flow.QUESTIONS[question_enum]
    
    bot_message = f"Welcome to loan verification!\n\n{question_text}"
    storage.add_message(app_id, "bot", bot_message)
    
    return MessageResponse(
        application_id=app_id,
        bot_message=bot_message,
        current_stage=current_stage,
        next_stage=None,
        completed=False,
        collected_data=state.get("collected_data", {})
    )

@app.post("/message")
async def handle_message(request: MessageRequest) -> MessageResponse:
    """Handle user message"""
    
    app_id = request.application_id
    user_message = request.user_message
    
    # Load state
    state = storage.load_conversation(app_id)
    if not state:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    current_stage_str = state.get("current_stage")
    collected_data = state.get("collected_data", {})  # Fresh copy from disk
    
    # Parse stage
    try:
        current_stage = QuestionStage[current_stage_str.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid stage")
    
    # Validate answer
    is_valid, value = flow.validate_answer(current_stage, user_message)
    
    if not is_valid:
        # Validation failed - re-ask same question
        error_msg = value  # value contains error message
        question_text = flow.QUESTIONS[current_stage]
        bot_message = f"❌ {error_msg}\n\n{question_text}"
        storage.add_message(app_id, "user", user_message)
        storage.add_message(app_id, "bot", bot_message)
        
        return MessageResponse(
            application_id=app_id,
            bot_message=bot_message,
            current_stage=current_stage_str,
            next_stage=None,
            completed=False,
            collected_data=collected_data
        )
    
    # Validation passed - save answer
    collected_data[current_stage_str] = value
    storage.add_answer(app_id, current_stage_str, value)  # Persist to disk
    storage.add_message(app_id, "user", user_message)
    
    # If KYC file uploaded, extract OCR data
    if current_stage == QuestionStage.KYC_FILE:
        logger.info(f"KYC file uploaded: {value}")
        ocr_data = extract_document_data(value)
        if ocr_data:
            # Store OCR data in conversation state
            state = storage.load_conversation(app_id)
            state["ocr_data"] = ocr_data
            storage.save_conversation(app_id, state)
            logger.info(f"Extracted OCR data: {ocr_data}")
        else:
            logger.warning("Failed to extract OCR data from KYC file")
    
    # Get next question
    next_stage, next_question = flow.get_next_question(current_stage, collected_data)
    
    if next_stage is None:
        # All questions answered - check if flow is complete
        if flow.is_flow_complete(collected_data):
            # Load current state to get OCR data
            current_state = storage.load_conversation(app_id)
            ocr_data = current_state.get("ocr_data", {})
            
            # Validate collected data against OCR data
            if ocr_data:
                is_valid_ocr, validation_msg = flow.validate_against_ocr(collected_data, ocr_data)
                if not is_valid_ocr:
                    # Validation failed - reject submission
                    bot_message = f"❌ Document verification failed!\n{validation_msg}\n\nPlease provide correct information matching your documents."
                    storage.add_message(app_id, "bot", bot_message)
                    
                    return MessageResponse(
                        application_id=app_id,
                        bot_message=bot_message,
                        current_stage=current_stage_str,
                        next_stage=None,
                        completed=False,
                        collected_data=collected_data
                    )
                else:
                    logger.info(f"Document verification passed: {validation_msg}")
                    bot_message = f"✅ {validation_msg}"
                    storage.add_message(app_id, "bot", bot_message)
            
            # Flow complete - prepare payload and send to orchestrator
            storage.mark_completed(app_id)
            
            bot_message = "✅ Application data collected! Submitting to orchestrator..."
            storage.add_message(app_id, "bot", bot_message)
            
            # Prepare payload for orchestrator
            payload = {
                "application_id": app_id,
                "user_answers": collected_data,
                "file_uris": {
                    "kyc_file": collected_data.get("kyc_file"),
                    "selfie_file": collected_data.get("selfie_file"),
                    "payslip_file": collected_data.get("payslip_file"),
                    "bank_statement_file": collected_data.get("bank_statement_file")
                },
                "loan_request": {
                    "loan_amount": collected_data.get("loan_amount"),
                    "tenure_months": collected_data.get("tenure_months")
                }
            }
            
            # Send to orchestrator
            try:
                orchestrator_response = requests.post(
                    "http://localhost:9000/orchestrate",
                    json=payload,
                    timeout=30
                )
                
                if orchestrator_response.status_code == 200:
                    job_data = orchestrator_response.json()
                    bot_message = f"✅ Application submitted for verification.\nJob ID: {job_data.get('job_id')}\n\nVerification in progress..."
                    storage.add_message(app_id, "bot", bot_message)
                else:
                    logger.error(f"Orchestrator error: {orchestrator_response.status_code}")
                    bot_message = "⚠️ Submitted but orchestrator returned error. Please contact support."
                    storage.add_message(app_id, "bot", bot_message)
            
            except Exception as e:
                logger.error(f"Error calling orchestrator: {e}")
                bot_message = f"⚠️ Error submitting to orchestrator: {str(e)}"
                storage.add_message(app_id, "bot", bot_message)
            
            return MessageResponse(
                application_id=app_id,
                bot_message=bot_message,
                current_stage=current_stage_str,
                next_stage=None,
                completed=True,
                collected_data=collected_data
            )
        else:
            bot_message = "⚠️ Required data missing. Please review your answers."
            return MessageResponse(
                application_id=app_id,
                bot_message=bot_message,
                current_stage=current_stage_str,
                next_stage=None,
                completed=False,
                collected_data=collected_data
            )
    
    # Move to next stage
    next_stage_str = next_stage.value
    storage.update_stage(app_id, next_stage_str)
    
    bot_message = next_question
    storage.add_message(app_id, "bot", bot_message)
    
    return MessageResponse(
        application_id=app_id,
        bot_message=bot_message,
        current_stage=next_stage_str,
        next_stage=next_stage_str,
        completed=False,
        collected_data=collected_data
    )

@app.get("/state/{app_id}")
async def get_state(app_id: str):
    """Get current conversation state"""
    state = storage.load_conversation(app_id)
    if not state:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return state

@app.post("/reset/{app_id}")
async def reset(app_id: str):
    """Reset conversation"""
    storage.initialize_conversation(app_id)
    return {"message": "Conversation reset", "application_id": app_id}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Intake Agent on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
