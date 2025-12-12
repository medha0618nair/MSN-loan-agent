"""
Pydantic schemas for Credit Scoring Agent.
Strict validation of all incoming and outgoing JSON.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Evidence Models
class IntakeEvidence(BaseModel):
    """Intake agent output: slot-filled conversation data."""
    applicant_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    loan_amount: Optional[int] = None
    loan_purpose: Optional[str] = None
    pan: Optional[str] = None


class KYCEvidence(BaseModel):
    """KYC/OCR agent output: identity verification."""
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    name_extracted: Optional[str] = None
    kyc_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    doc_type: Optional[str] = None


class FaceEvidence(BaseModel):
    """Face verification agent output."""
    face_verified: bool = False
    match_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    liveness_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class PayslipEvidence(BaseModel):
    """Payslip OCR agent output: salary from documents."""
    net_pay_payslip: Optional[int] = None
    gross_pay_payslip: Optional[int] = None
    monthly_income: Optional[int] = None
    income_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    employment_status: Optional[str] = None


class BankEvidence(BaseModel):
    """Bank statement agent output: salary detection from CSV."""
    median_salary: Optional[int] = None
    avg_salary: Optional[int] = None
    months_salary_detected: Optional[int] = None
    payroll_consistency: float = Field(default=0.0, ge=0.0, le=1.0)
    salary_share_of_credits: float = Field(default=0.0, ge=0.0, le=1.0)
    inflow_std: Optional[float] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    bank_salary_detected: bool = False


class FraudEvidence(BaseModel):
    """Fraud detection agent output."""
    fraud_score: float = Field(default=0.0, ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)
    suspicious_keywords: List[str] = Field(default_factory=list)


class EvidenceBundle(BaseModel):
    """Combined evidence from all agents."""
    intake: Optional[IntakeEvidence] = None
    kyc: Optional[KYCEvidence] = None
    face: Optional[FaceEvidence] = None
    payslip: Optional[PayslipEvidence] = None
    bank: Optional[BankEvidence] = None
    fraud: Optional[FraudEvidence] = None


class LoanRequest(BaseModel):
    """Loan product details."""
    loan_amount: int = Field(gt=0)
    tenure_months: int = Field(gt=0, le=84)
    monthly_emi_estimate: float = Field(ge=0.0)


class AppMetadata(BaseModel):
    """Metadata about application submission."""
    submission_ts: str
    source: str = "web"


class CreditScoringRequest(BaseModel):
    """Complete request to credit scoring endpoint."""
    application_id: str
    evidence: EvidenceBundle
    loan_request: LoanRequest
    app_metadata: AppMetadata


# Response Models
class FeatureImportances(BaseModel):
    """Feature importance scores from model."""
    income: float = 0.0
    payroll_consistency: float = 0.0
    fraud_score: float = 0.0
    face_confidence: float = 0.0
    kyc_confidence: float = 0.0
    dti: float = 0.0
    tenure: float = 0.0
    other: float = 0.0


class CreditScoringResponse(BaseModel):
    """Standard response from credit scoring endpoint."""
    application_id: str
    pd_score: float = Field(ge=0.0, le=1.0)
    risk_tier: str  # LOW / MEDIUM / HIGH
    recommended_action: str  # APPROVE / REVIEW / REJECT
    max_eligible_loan: int
    recommended_tenure_months: int
    monthly_emi_recommendation: float
    explanation: List[str]
    feature_importances: FeatureImportances
    confidence: float = Field(ge=0.0, le=1.0)
    agent_version: str
    ts: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    details: Optional[str] = None


class ModelInfoResponse(BaseModel):
    """Model metadata endpoint response."""
    model_version: str
    training_date: Optional[str] = None
    feature_list: List[str]
    model_type: str
    status: str
