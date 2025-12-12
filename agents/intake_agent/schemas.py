"""
Pydantic schemas for Intake Agent requests and responses.
Ensures strict JSON contracts for LangChain Tool integration.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class ConverseRequest(BaseModel):
    """Request for conversational RAG chat."""
    application_id: str = Field(..., description="Unique application ID")
    conversation_id: str = Field(..., description="Unique conversation ID")
    user_message: str = Field(..., description="User's natural language input")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class SlotUpdateRequest(BaseModel):
    """Request for slot-filling updates."""
    application_id: str = Field(..., description="Unique application ID")
    conversation_id: str = Field(..., description="Unique conversation ID")
    slot_name: str = Field(..., description="Slot to update (e.g., 'full_name', 'loan_amount')")
    slot_value: Any = Field(..., description="Value for the slot")


class UploadRequest(BaseModel):
    """Request to register an uploaded document and trigger KYC parsing."""
    application_id: str = Field(..., description="Unique application ID")
    conversation_id: str = Field(..., description="Unique conversation ID")
    doc_type: str = Field(..., description="Document type (pan, aadhaar, payslip, bank_statement)")
    file_path: str = Field(..., description="Path to uploaded document accessible to KYC agent")
    evidence_id: Optional[str] = Field(None, description="Optional evidence identifier")


class SubmitRequest(BaseModel):
    """Request to finalize and submit application."""
    application_id: str = Field(..., description="Unique application ID")
    conversation_id: str = Field(..., description="Unique conversation ID")


class ActionItem(BaseModel):
    """Action item for orchestrator."""
    type: str = Field(..., description="Action type (upload_request, validation_error, etc.)")
    doc_type: Optional[str] = Field(None, description="Document type if applicable")
    message: Optional[str] = Field(None, description="Human-readable message")


class IntakeResponse(BaseModel):
    """Standardized response contract for Intake Agent."""
    application_id: str
    conversation_id: str
    slots: Dict[str, Any] = Field(default_factory=dict)
    required_uploads: List[str] = Field(default_factory=list)
    actions: List[ActionItem] = Field(default_factory=list)
    agent_version: str = "intake-v1"
    ts: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    assistant_reply: Optional[str] = Field(None, description="Natural language response")
    rag_context: Optional[str] = Field(None, description="Retrieved RAG context")
    next_prompt: Optional[str] = Field(None, description="Suggested next question")
    kyc_result: Optional[Dict[str, Any]] = Field(None, description="KYC parse response if available")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    service: str = "intake_agent"
    version: str = "intake-v1"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
