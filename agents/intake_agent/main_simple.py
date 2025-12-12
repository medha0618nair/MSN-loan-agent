"""
Simplified Intake Agent - Working Version
Runs without Redis; uses Groq directly (no LangChain).
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from groq import Groq

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Intake Agent",
    description="Loan intake agent powered by Groq",
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

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# In-memory storage (since Redis not available)
conversations = {}
slots_storage = {}

logger.info("✅ Intake Agent initialized with Groq API")


# Schemas
class ConverseRequest(BaseModel):
    application_id: str
    conversation_id: str
    user_message: str
    context: Dict[str, Any] = {}


class SlotUpdateRequest(BaseModel):
    application_id: str
    conversation_id: str
    slot_name: str
    slot_value: Any


class SubmitRequest(BaseModel):
    application_id: str
    conversation_id: str


class ActionItem(BaseModel):
    type: str
    doc_type: str | None = None
    message: str | None = None


class IntakeResponse(BaseModel):
    application_id: str
    conversation_id: str
    slots: Dict[str, Any] = Field(default_factory=dict)
    required_uploads: list[str] = Field(default_factory=list)
    actions: list[ActionItem] = Field(default_factory=list)
    agent_version: str = "intake-v1"
    ts: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    assistant_reply: str | None = None
    rag_context: str | None = None
    next_prompt: str | None = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "intake_agent"
    version: str = "intake-v1"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Fast health check endpoint."""
    return HealthResponse()


@app.post("/chat/converse", response_model=IntakeResponse)
async def converse(request: ConverseRequest):
    """Conversational endpoint with Groq-powered responses."""
    logger.info(f"[{request.application_id}] Converse request: {request.user_message}")
    
    try:
        # Get or create conversation history
        conv_key = f"{request.application_id}:{request.conversation_id}"
        if conv_key not in conversations:
            conversations[conv_key] = []
        
        # Get current slots
        current_slots = slots_storage.get(request.application_id, {})
        
        # Create prompt for Groq
        system_prompt = f"""You are a helpful loan application assistant. 

Current collected information: {json.dumps(current_slots)}

Extract any loan-related information from the user's message such as:
- full_name
- email
- phone
- loan_amount
- loan_purpose
- employment_status
- monthly_income
- pan_number

Respond naturally and ask for missing information.
If user asks a question about loans, answer briefly."""

        # Call Groq API
        if groq_client:
            try:
                completion = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.user_message}
                    ],
                    temperature=0.7,
                    max_tokens=1024
                )
                assistant_reply = completion.choices[0].message.content
            except Exception as llm_err:
                logger.warning(f"Groq call failed: {llm_err}")
                assistant_reply = (
                    "I'm having trouble reaching the LLM right now. "
                    "I'll continue collecting your details meanwhile."
                )
        else:
            assistant_reply = (
                f"I received your message: '{request.user_message}'. "
                "Set GROQ_API_KEY to enable AI responses."
            )
        
        # Simple slot extraction (look for patterns)
        msg_lower = request.user_message.lower()
        
        # Extract loan amount
        import re
        amount_match = re.search(r'(\d+(?:,\d+)*)\s*(?:rupees?|rs\.?|₹|lakhs?)', msg_lower)
        if amount_match:
            amount = amount_match.group(1).replace(',', '')
            if 'lakh' in msg_lower:
                amount = str(int(amount) * 100000)
            current_slots['loan_amount'] = amount
        
        # Extract email
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', request.user_message)
        if email_match:
            current_slots['email'] = email_match.group()
        
        # Extract phone
        phone_match = re.search(r'[6-9]\d{9}', request.user_message)
        if phone_match:
            current_slots['phone'] = phone_match.group()
        
        # Update storage
        slots_storage[request.application_id] = current_slots
        conversations[conv_key].append({"user": request.user_message, "assistant": assistant_reply})
        
        # Determine required uploads
        required_uploads = []
        if current_slots.get("pan_number"):
            required_uploads.append("pan")
        if current_slots.get("employment_status") == "salaried":
            required_uploads.extend(["payslip", "bank_statement"])
        
        # Generate actions
        actions = []
        required_fields = ["full_name", "email", "phone", "loan_amount", "loan_purpose"]
        missing_fields = [f for f in required_fields if f not in current_slots]
        
        if missing_fields and len(current_slots) > 0:
            next_field = missing_fields[0].replace('_', ' ')
            actions.append(ActionItem(
                type="slot_request",
                message=f"Please provide your {next_field}"
            ))
        
        response = IntakeResponse(
            application_id=request.application_id,
            conversation_id=request.conversation_id,
            slots=current_slots,
            required_uploads=required_uploads,
            actions=actions,
            assistant_reply=assistant_reply,
            next_prompt=actions[0].message if actions else None
        )
        
        logger.info(f"[{request.application_id}] Response generated, slots: {len(current_slots)}")
        return response
        
    except Exception as e:
        logger.error(f"[{request.application_id}] Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/slot", response_model=IntakeResponse)
async def update_slot(request: SlotUpdateRequest):
    """Explicit slot update endpoint."""
    logger.info(f"[{request.application_id}] Slot update: {request.slot_name} = {request.slot_value}")
    
    try:
        # Get or create slots
        if request.application_id not in slots_storage:
            slots_storage[request.application_id] = {}
        
        # Update slot
        slots_storage[request.application_id][request.slot_name] = request.slot_value
        current_slots = slots_storage[request.application_id]
        
        # Check completeness
        required_slots = ["full_name", "email", "phone", "loan_amount", "loan_purpose"]
        missing_slots = [s for s in required_slots if s not in current_slots]
        
        actions = []
        next_prompt = None
        
        if missing_slots:
            next_prompt = f"Great! Now, could you provide your {missing_slots[0].replace('_', ' ')}?"
            actions.append(ActionItem(type="slot_request", message=next_prompt))
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
        
        logger.info(f"[{request.application_id}] Slot updated, total slots: {len(current_slots)}")
        return response
        
    except Exception as e:
        logger.error(f"[{request.application_id}] Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/submit", response_model=IntakeResponse)
async def submit_application(request: SubmitRequest):
    """Finalize and submit application."""
    logger.info(f"[{request.application_id}] Application submission request")
    
    try:
        current_slots = slots_storage.get(request.application_id, {})
        
        required_slots = ["full_name", "email", "phone", "loan_amount", "loan_purpose"]
        missing_slots = [s for s in required_slots if s not in current_slots]
        
        actions = []
        
        if missing_slots:
            actions.append(ActionItem(
                type="validation_error",
                message=f"Missing required information: {', '.join(missing_slots)}"
            ))
            assistant_reply = "Cannot submit yet. Please complete all required fields."
        else:
            actions.append(ActionItem(
                type="submit_success",
                message="Application submitted successfully. Proceeding to KYC verification."
            ))
            assistant_reply = "Thank you! Your application has been submitted."
        
        response = IntakeResponse(
            application_id=request.application_id,
            conversation_id=request.conversation_id,
            slots=current_slots,
            required_uploads=["pan", "payslip", "bank_statement"],
            actions=actions,
            assistant_reply=assistant_reply
        )
        
        logger.info(f"[{request.application_id}] Submission result: {actions[0].type}")
        return response
        
    except Exception as e:
        logger.error(f"[{request.application_id}] Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    if not GROQ_API_KEY:
        logger.warning("⚠️  GROQ_API_KEY not set! Agent will run with limited functionality.")
        logger.warning("   Set GROQ_API_KEY in .env file or environment variable")
    
    logger.info("")
    logger.info("="*60)
    logger.info("🚀 Starting Intake Agent on http://localhost:8001")
    logger.info("📚 API Docs: http://localhost:8001/docs")
    logger.info("="*60)
    logger.info("")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
