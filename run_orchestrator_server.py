#!/usr/bin/env python3
"""
Orchestrator API Server - Accept user data and return loan decisions
Start this server, then send user data via HTTP POST requests
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import orchestrator
from orchestrator_agent import MasterOrchestrator, OrchestratorConfig

# Initialize FastAPI
app = FastAPI(
    title="MSN Loan Orchestrator API",
    description="Submit applicant data and get loan decisions",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ApplicantInfo(BaseModel):
    """User applicant information"""
    name: str = Field(..., example="Jane Smith")
    email: str = Field(..., example="jane@example.com")
    phone: str = Field(..., example="+91-9123456789")
    employment_status: str = Field(default="salaried", example="salaried")
    annual_income: float = Field(..., example=1000000)
    current_employer: str = Field(..., example="FinTech Corp")
    designation: str = Field(..., example="Product Manager")
    years_at_current_employer: float = Field(default=1, example=4)
    loan_amount_requested: float = Field(..., example=750000)
    loan_tenure_months: int = Field(default=60, example=60)


class DocumentsInfo(BaseModel):
    """Document file paths"""
    aadhaar: Optional[str] = Field(default=None, example="/path/to/aadhaar.pdf")
    pan: Optional[str] = Field(default=None, example="/path/to/pan.pdf")
    payslip: Optional[str] = Field(default=None, example="/path/to/payslip.pdf")
    bank_statement: Optional[str] = Field(default=None, example="/path/to/bank_statement.pdf")
    passport: Optional[str] = Field(default=None, example="/path/to/passport.pdf")
    selfie: Optional[str] = Field(default=None, example="/path/to/selfie.jpg")


class LoanApplicationRequest(BaseModel):
    """Complete loan application request"""
    application_id: Optional[str] = Field(default=None, example="APP-001")
    applicant_info: ApplicantInfo
    documents: Optional[DocumentsInfo] = None
    custom_fields: Optional[Dict[str, Any]] = None


class LoanDecisionResponse(BaseModel):
    """Loan decision response"""
    application_id: str
    final_status: str  # APPROVED, REJECTED, MANUAL_REVIEW
    credit_score: int
    risk_level: str
    approved_amount: Optional[float]
    interest_rate: Optional[float]
    monthly_emi: Optional[float]
    tenure_months: Optional[int]
    total_repayment: Optional[float]
    reason: str
    evidence_trail: Dict[str, Any]
    processed_at: str


# Global orchestrator instance
orchestrator = None
processing_status = {}  # Track status of applications


async def init_orchestrator():
    """Initialize orchestrator on startup"""
    global orchestrator
    try:
        orchestrator = MasterOrchestrator()
        print("✅ Orchestrator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    await init_orchestrator()


@app.get("/health")
async def health_check():
    """Check orchestrator and all agents health"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        health = await orchestrator.check_all_agents_health()
        return {
            "status": "healthy",
            "orchestrator": "ready",
            "agents": health
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "One or more agents may not be running on required ports (8001-8006)"
        }


@app.post("/process-application", response_model=LoanDecisionResponse)
async def process_application(request: LoanApplicationRequest, background_tasks: BackgroundTasks):
    """
    Process loan application through all 6 agents
    
    Returns final loan decision with complete evidence trail
    """
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    # Generate application ID if not provided
    app_id = request.application_id or f"APP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    print(f"\n{'='*80}")
    print(f"📨 RECEIVED APPLICATION: {app_id}")
    print(f"👤 APPLICANT: {request.applicant_info.name}")
    print(f"💰 LOAN REQUEST: ₹{request.applicant_info.loan_amount_requested:,.0f}")
    print(f"{'='*80}\n")
    
    # Mark as processing
    processing_status[app_id] = "processing"
    
    try:
        # Convert request to dict format expected by orchestrator
        applicant_data = request.applicant_info.dict()
        documents = request.documents.dict() if request.documents else {}
        
        # Process application through all 6 agents
        result = await orchestrator.process_application(
            app_id=app_id,
            applicant_data=applicant_data,
            documents=documents,
            custom_fields=request.custom_fields or {}
        )
        
        # Mark as completed
        processing_status[app_id] = "completed"
        
        # Extract key information
        credit_info = result.get("evidence_trail", {}).get("credit", {})
        loan_info = result.get("loan_recommendation", {})
        
        response = LoanDecisionResponse(
            application_id=app_id,
            final_status=result.get("final_status", "MANUAL_REVIEW"),
            credit_score=credit_info.get("credit_score", 0),
            risk_level=credit_info.get("risk_level", "Unknown"),
            approved_amount=loan_info.get("approved_amount"),
            interest_rate=loan_info.get("interest_rate"),
            monthly_emi=loan_info.get("monthly_emi"),
            tenure_months=loan_info.get("tenure_months"),
            total_repayment=loan_info.get("total_repayment"),
            reason=result.get("reason", "Processing complete"),
            evidence_trail=result.get("evidence_trail", {}),
            processed_at=result.get("processed_at", datetime.utcnow().isoformat())
        )
        
        print(f"\n✅ Application {app_id} processed successfully")
        print(f"📊 Decision: {response.final_status}")
        print(f"💳 Credit Score: {response.credit_score}\n")
        
        return response
        
    except Exception as e:
        processing_status[app_id] = "failed"
        print(f"❌ Error processing application {app_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Application processing failed: {str(e)}"
        )


@app.get("/application-status/{app_id}")
async def get_application_status(app_id: str):
    """Check status of an application"""
    status = processing_status.get(app_id, "not_found")
    return {
        "application_id": app_id,
        "status": status
    }


@app.get("/agents/health")
async def agents_health():
    """Check individual agent health"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    try:
        health = await orchestrator.check_all_agents_health()
        agents_status = {}
        for stage, is_healthy in health.items():
            agents_status[stage] = {
                "healthy": is_healthy,
                "port": OrchestratorConfig.AGENTS[stage]["url"].split(":")[-1]
            }
        return agents_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/demo")
async def run_demo():
    """Run demo application for testing"""
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator not initialized")
    
    demo_request = LoanApplicationRequest(
        application_id="DEMO-001",
        applicant_info=ApplicantInfo(
            name="Demo User",
            email="demo@example.com",
            phone="+91-9000000000",
            annual_income=1000000,
            current_employer="Demo Corp",
            designation="Manager",
            years_at_current_employer=3,
            loan_amount_requested=500000,
            loan_tenure_months=60
        )
    )
    
    return await process_application(demo_request, BackgroundTasks())


@app.get("/")
async def root():
    """API Documentation"""
    return {
        "name": "MSN Loan Orchestrator API",
        "version": "1.0.0",
        "description": "Submit applicant data and get loan decisions",
        "endpoints": {
            "health": {
                "method": "GET",
                "path": "/health",
                "description": "Check orchestrator and all agents health"
            },
            "process_application": {
                "method": "POST",
                "path": "/process-application",
                "description": "Process loan application through all 6 agents",
                "request_body": "LoanApplicationRequest"
            },
            "application_status": {
                "method": "GET",
                "path": "/application-status/{app_id}",
                "description": "Check application processing status"
            },
            "agents_health": {
                "method": "GET",
                "path": "/agents/health",
                "description": "Check individual agent health"
            },
            "demo": {
                "method": "POST",
                "path": "/demo",
                "description": "Run demo test"
            }
        }
    }


if __name__ == "__main__":
    port = int(os.getenv("ORCHESTRATOR_PORT", 8000))
    print(f"\n🚀 Starting Orchestrator API Server on port {port}")
    print(f"📖 Docs available at http://localhost:{port}/docs")
    print(f"🔍 OpenAPI schema at http://localhost:{port}/openapi.json\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
