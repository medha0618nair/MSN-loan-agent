"""
Pydantic schemas for KYC/OCR Agent.
Ensures strict JSON contracts for document processing.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class OCRData(BaseModel):
    """Extracted OCR data."""
    raw_text: str = Field(..., description="Raw OCR text")
    structured_fields: Dict[str, Any] = Field(default_factory=dict, description="Parsed structured fields")
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Per-field confidence")


class FaceCropEvidence(BaseModel):
    """Face crop evidence from ID document."""
    crop_file_uri: Optional[str] = Field(None, description="Path to cropped face image")
    face_detected: bool = Field(False, description="Whether a face was detected")
    face_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Face detection confidence")
    face_bbox: Optional[List[int]] = Field(None, description="Bounding box [x, y, w, h]")


class KYCParseRequest(BaseModel):
    """Request for KYC document parsing."""
    application_id: str = Field(..., description="Unique application ID")
    evidence_id: str = Field(..., description="Unique evidence ID")
    doc_type: str = Field(..., description="Document type (pan, payslip, bank_statement, aadhaar)")
    file_path: str = Field(..., description="Path to uploaded document")


class KYCParseResponse(BaseModel):
    """Standardized response contract for KYC Agent."""
    application_id: str
    evidence_id: str
    doc_type: str
    file_uri: str
    file_sha256: str
    ocr: OCRData
    id_crop_evidence: Optional[FaceCropEvidence] = None
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    agent_version: str = "kyc-v1"
    ts: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    validation_errors: List[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    service: str = "kyc_agent"
    version: str = "kyc-v1"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
