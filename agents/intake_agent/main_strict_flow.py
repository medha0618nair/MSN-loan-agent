"""
Intake Agent - Strict Conversational Flow
FastAPI service with sequential question-answer flow
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chat_flow import ConversationFlowManager
from storage import ConversationStorage

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Intake Agent - Conversational Flow",
    description="Strict sequential question-answer conversation",
    version="2.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize flow manager and storage
flow_manager = ConversationFlowManager()
storage = ConversationStorage()

# ==================== REQUEST/RESPONSE MODELS ====================

class StartRequest(BaseModel):
    application_id: str
    conversation_id: Optional[str] = None

class UserMessageRequest(BaseModel):
    application_id: str
    user_message: str

class StartResponse(BaseModel):
    application_id: str
    conversation_id: str
    bot_message: str
    next_question_id: str
    current_question: Dict[str, Any]

class MessageResponse(BaseModel):
    application_id: str
    bot_message: str
    next_question_id: Optional[str]
    current_question: Optional[Dict[str, Any]]
    collected_slots: Dict[str, Any]
    completed: bool
    message: str

# ==================== ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "intake_agent",
        "version": "2.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/start", response_model=StartResponse)
async def start_conversation(request: StartRequest):
    """
    Start a new conversation
    Always starts with loan_type question
    """
    application_id = request.application_id
    conversation_id = request.conversation_id or str(uuid4())
    
    # Initialize or load existing conversation
    existing_state = storage.load_conversation_state(application_id)
    
    if existing_state and not existing_state.get("completed"):
        # Resume existing conversation
        current_q_id = existing_state.get("current_question_id", "loan_type")
    else:
        # Start new conversation
        storage.initialize_conversation(application_id, conversation_id)
        current_q_id = "loan_type"
    
    current_question = flow_manager.get_question_by_id(current_q_id)
    
    if not current_question:
        raise HTTPException(status_code=400, detail="Invalid question ID")
    
    bot_message = current_question["question"]
    
    # Add to message history
    storage.add_message(application_id, "bot", bot_message)
    
    logger.info(f"[{application_id}] Started conversation, first question: {current_q_id}")
    
    return StartResponse(
        application_id=application_id,
        conversation_id=conversation_id,
        bot_message=bot_message,
        next_question_id=current_q_id,
        current_question=current_question
    )

@app.post("/message", response_model=MessageResponse)
async def handle_user_message(request: UserMessageRequest):
    """
    Handle user message and validate against current question
    Only move to next question if validation passes
    """
    application_id = request.application_id
    user_message = request.user_message.strip()
    
    # Load conversation state
    state = storage.load_conversation_state(application_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Conversation not found. Start with /start endpoint")
    
    if state.get("completed"):
        raise HTTPException(status_code=400, detail="This conversation is already completed")
    
    current_q_id = state.get("current_question_id")
    current_question = flow_manager.get_question_by_id(current_q_id)
    
    if not current_question:
        raise HTTPException(status_code=400, detail="Invalid current question")
    
    # Add user message to history
    storage.add_message(application_id, "user", user_message)
    
    # Validate the answer
    is_valid, validated_value = flow_manager.validate_answer(current_q_id, user_message)
    
    if not is_valid:
        # Validation failed - ask again
        bot_message = f"❌ {validated_value}\n\n{current_question['question']}"
        storage.add_message(application_id, "bot", bot_message)
        
        logger.warning(f"[{application_id}] Validation failed for {current_q_id}: {validated_value}")
        
        return MessageResponse(
            application_id=application_id,
            bot_message=bot_message,
            next_question_id=current_q_id,
            current_question=current_question,
            collected_slots=state.get("collected_slots", {}),
            completed=False,
            message="Validation failed, please retry"
        )
    
    # Validation passed - save the answer
    field_name = current_question["field_name"]
    storage.update_collected_slots(application_id, field_name, validated_value)
    
    logger.info(f"[{application_id}] Validated {field_name}: {validated_value}")
    
    # Reload state with updated slots
    state = storage.load_conversation_state(application_id)
    collected_slots = state.get("collected_slots", {})
    
    # Get next question
    next_question = flow_manager.get_next_question(current_q_id, collected_slots)
    
    if next_question:
        # There are more questions
        next_q_id = next_question["id"]
        bot_message = next_question["question"]
        
        storage.set_current_question(application_id, next_q_id)
        storage.add_message(application_id, "bot", bot_message)
        
        logger.info(f"[{application_id}] Moving to next question: {next_q_id}")
        
        return MessageResponse(
            application_id=application_id,
            bot_message=bot_message,
            next_question_id=next_q_id,
            current_question=next_question,
            collected_slots=collected_slots,
            completed=False,
            message="Answer recorded. Next question..."
        )
    else:
        # All questions completed
        storage.mark_completed(application_id)
        
        bot_message = "✅ Your application is complete and ready for verification!"
        storage.add_message(application_id, "bot", bot_message)
        
        logger.info(f"[{application_id}] Conversation completed")
        
        return MessageResponse(
            application_id=application_id,
            bot_message=bot_message,
            next_question_id=None,
            current_question=None,
            collected_slots=collected_slots,
            completed=True,
            message="Application complete!"
        )

@app.get("/state/{application_id}")
async def get_conversation_state(application_id: str):
    """Get current conversation state"""
    state = storage.load_conversation_state(application_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return state

@app.post("/reset/{application_id}")
async def reset_conversation(application_id: str):
    """Reset a conversation to start over"""
    conversation_id = str(uuid4())
    storage.initialize_conversation(application_id, conversation_id)
    
    logger.info(f"[{application_id}] Conversation reset")
    
    return {
        "application_id": application_id,
        "message": "Conversation reset. Start with /start endpoint",
        "reset_at": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
