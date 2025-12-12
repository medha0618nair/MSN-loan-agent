"""
Pydantic models for Bank Statement Agent.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class BankParseRequest(BaseModel):
    """Request schema for bank statement parsing."""
    application_id: str = Field(..., description="Unique application identifier")
    evidence_id: str = Field(..., description="Unique evidence identifier")
    file_uri: str = Field(..., description="Path to the bank statement CSV file")


class BankParseResponse(BaseModel):
    """Response schema for bank statement parsing."""
    application_id: str
    evidence_id: str
    bank_salary_detected: bool
    salary_amounts: List[float] = Field(default_factory=list, description="Extracted salary amounts")
    salary_dates: List[str] = Field(default_factory=list, description="ISO format dates of salary credits")
    months_salary_detected: int
    avg_salary: float
    median_salary: float
    monthly_income_estimate: float
    payroll_consistency: float = Field(..., ge=0.0, le=1.0, description="Consistency score 0-1")
    inflow_std: float = Field(..., description="Standard deviation of positive credits")
    salary_share_of_credits: float = Field(..., ge=0.0, le=1.0, description="Salary as % of total credits")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score 0-1")
    agent_version: str = "bank-v1"
    ts: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO timestamp")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    agent: str = "bank-agent"
    version: str = "bank-v1"
