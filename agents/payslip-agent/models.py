"""
Pydantic models for payslip income verification.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PayslipInput(BaseModel):
    """Input model for payslip verification."""
    payslip_file: bytes = Field(..., description="Binary payslip file (PDF/PNG/JPG)")
    document_type: Optional[str] = Field(default="payslip", description="Document type")


class IncomeComponentEarnings(BaseModel):
    """Earnings components from payslip."""
    basic_pay: float = Field(default=0.0, description="Basic salary")
    hra: float = Field(default=0.0, description="House Rent Allowance")
    special_allowance: float = Field(default=0.0, description="Special allowance")
    conveyance: float = Field(default=0.0, description="Conveyance/transport allowance")
    other_allowance: float = Field(default=0.0, description="Other allowances")
    gross_earnings: float = Field(default=0.0, description="Total gross earnings")


class IncomeComponentDeductions(BaseModel):
    """Deduction components from payslip."""
    pf: float = Field(default=0.0, description="Provident Fund")
    professional_tax: float = Field(default=0.0, description="Professional tax")
    income_tax: float = Field(default=0.0, description="Income tax")
    other_deductions: float = Field(default=0.0, description="Other deductions")
    total_deductions: float = Field(default=0.0, description="Total deductions")


class PayslipVerificationResponse(BaseModel):
    """Payslip verification output response."""
    payslip_present: bool = Field(..., description="Whether payslip was successfully processed")
    employee_name: Optional[str] = Field(default=None, description="Employee name")
    employee_id: Optional[str] = Field(default=None, description="Employee ID")
    designation: Optional[str] = Field(default=None, description="Job designation")
    department: Optional[str] = Field(default=None, description="Department")
    employer: Optional[str] = Field(default=None, description="Employer name")
    employer_address: Optional[str] = Field(default=None, description="Employer address")

    pay_period: Optional[str] = Field(default=None, description="Pay period (e.g., 'Jan 2025')")
    payment_date: Optional[str] = Field(default=None, description="Payment date (ISO format)")

    basic_pay: float = Field(default=0.0, description="Basic salary")
    hra: float = Field(default=0.0, description="House Rent Allowance")
    special_allowance: float = Field(default=0.0, description="Special allowance")
    conveyance: float = Field(default=0.0, description="Conveyance allowance")
    other_allowance: float = Field(default=0.0, description="Other allowances")
    gross_earnings: float = Field(default=0.0, description="Total gross earnings")

    pf: float = Field(default=0.0, description="Provident Fund deduction")
    professional_tax: float = Field(default=0.0, description="Professional tax deduction")
    income_tax: float = Field(default=0.0, description="Income tax deduction")
    other_deductions: float = Field(default=0.0, description="Other deductions")
    total_deductions: float = Field(default=0.0, description="Total deductions")

    net_pay_payslip: float = Field(default=0.0, description="Net pay from payslip")
    monthly_income: float = Field(default=0.0, description="Calculated monthly income")
    income_confidence: float = Field(default=0.0, description="Confidence score (0.0-1.0)")
    source: str = Field(default="payslip_only", description="Income source")
    agent_version: str = Field(default="payslip-v1", description="Agent version")
    ts: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "payslip_present": True,
                "employee_name": "John Doe",
                "employee_id": "EMP123456",
                "designation": "Software Engineer",
                "department": "Engineering",
                "employer": "TechCorp Inc",
                "employer_address": "123 Tech Park, City",
                "pay_period": "January 2025",
                "payment_date": "2025-02-05",
                "basic_pay": 50000.0,
                "hra": 10000.0,
                "special_allowance": 5000.0,
                "conveyance": 1000.0,
                "other_allowance": 2000.0,
                "gross_earnings": 68000.0,
                "pf": 6000.0,
                "professional_tax": 200.0,
                "income_tax": 5000.0,
                "other_deductions": 500.0,
                "total_deductions": 11700.0,
                "net_pay_payslip": 56300.0,
                "monthly_income": 56300.0,
                "income_confidence": 0.95,
                "source": "payslip_only",
                "agent_version": "payslip-v1",
                "ts": "2025-01-15T10:30:00"
            }
        }


class PayslipErrorResponse(BaseModel):
    """Error response for payslip processing."""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(default=None, description="Additional error details")
