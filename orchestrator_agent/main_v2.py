#!/usr/bin/env python3
"""
Orchestrator v2 - Main FastAPI Server
Runs on port 9000
Handles: /orchestrate, /status/{job_id}, /agents/status
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config_v2 import OrchestratorConfigV2

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Orchestrator v2",
    description="Multi-agent orchestration system",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://10.110.1.81:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
os.makedirs(OrchestratorConfigV2.AUDIT_DIR, exist_ok=True)
os.makedirs(OrchestratorConfigV2.JOBS_DIR, exist_ok=True)

# Request/Response Models
class OrchestrateRequest(BaseModel):
    application_id: str
    user_answers: Dict[str, Any]
    file_uris: Dict[str, Optional[str]]
    loan_request: Dict[str, Any]

class OrchestrateResponse(BaseModel):
    job_id: str
    application_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    application_id: str
    status: str
    kyc_result: Optional[Dict[str, Any]] = None
    face_result: Optional[Dict[str, Any]] = None
    payslip_result: Optional[Dict[str, Any]] = None
    bank_result: Optional[Dict[str, Any]] = None
    credit_result: Optional[Dict[str, Any]] = None
    final_decision: Optional[Dict[str, Any]] = None

class AgentStatusResponse(BaseModel):
    intake: str
    kyc: str
    face: str
    payslip: str
    bank: str
    credit: str
    orchestrator: str

# Job storage
jobs_store: Dict[str, Dict[str, Any]] = {}

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "orchestrator", "port": 9000}

@app.get("/agents/status")
async def agents_status() -> AgentStatusResponse:
    """Check status of all agents"""
    logger.info("Checking agent health...")
    
    async with httpx.AsyncClient(timeout=OrchestratorConfigV2.HEALTH_CHECK_TIMEOUT) as client:
        results = {}
        
        for agent_name, config in OrchestratorConfigV2.ALL_AGENTS.items():
            try:
                response = await client.get(f"{config.url}/health")
                results[agent_name] = "RUNNING" if response.status_code == 200 else "DOWN"
            except Exception as e:
                logger.warning(f"Agent {agent_name} health check failed: {e}")
                results[agent_name] = "DOWN"
        
        return AgentStatusResponse(
            orchestrator="RUNNING",
            **results
        )

async def call_agent(agent_name: str, url: str, payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    """Call a single agent with retry logic"""
    
    logger.info(f"Calling {agent_name}: POST {url}")
    
    config = OrchestratorConfigV2.ALL_AGENTS.get(agent_name)
    retries = config.retries if config else 2
    
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ {agent_name} succeeded")
                    return result
                else:
                    logger.warning(f"{agent_name} returned {response.status_code}")
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {agent_name}: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2)  # Wait before retry
    
    logger.error(f"❌ {agent_name} failed after {retries} retries")
    return {"error": f"{agent_name} failed after {retries} retries", "status": "FAILED"}

@app.post("/orchestrate", response_model=OrchestrateResponse)
async def orchestrate(request: OrchestrateRequest) -> OrchestrateResponse:
    """
    Main orchestration endpoint
    1. Call parallel agents (KYC, Face, Payslip, Bank)
    2. Merge results
    3. Call credit agent
    4. Save audit file
    """
    
    job_id = f"JOB-{uuid4().hex[:12].upper()}"
    app_id = request.application_id
    
    logger.info(f"\n{'='*70}")
    logger.info(f"🚀 ORCHESTRATING JOB: {job_id}")
    logger.info(f"📱 Application: {app_id}")
    logger.info(f"{'='*70}\n")
    
    # Initialize job
    job_data = {
        "job_id": job_id,
        "application_id": app_id,
        "status": "PROCESSING",
        "started_at": datetime.utcnow().isoformat(),
        "stages": {},
        "final_decision": None
    }
    jobs_store[job_id] = job_data
    
    try:
        # Step 1: Call parallel agents
        logger.info("📊 STEP 1: Calling parallel agents (KYC, Face, Payslip, Bank)...")
        logger.info("-" * 70)
        
        parallel_tasks = {
            "kyc": call_agent(
                "kyc",
                OrchestratorConfigV2.get_agent_url("kyc"),
                {
                    "application_id": app_id,
                    "kyc_file": request.file_uris.get("kyc_file"),
                    "user_data": request.user_answers
                },
                OrchestratorConfigV2.PARALLEL_TIMEOUT
            ),
            "face": call_agent(
                "face",
                OrchestratorConfigV2.get_agent_url("face"),
                {
                    "application_id": app_id,
                    "selfie_file": request.file_uris.get("selfie_file"),
                    "user_data": request.user_answers
                },
                OrchestratorConfigV2.PARALLEL_TIMEOUT
            ),
            "payslip": call_agent(
                "payslip",
                OrchestratorConfigV2.get_agent_url("payslip"),
                {
                    "application_id": app_id,
                    "payslip_file": request.file_uris.get("payslip_file"),
                    "user_data": request.user_answers
                },
                OrchestratorConfigV2.PARALLEL_TIMEOUT
            ),
            "bank": call_agent(
                "bank",
                OrchestratorConfigV2.get_agent_url("bank"),
                {
                    "application_id": app_id,
                    "bank_statement_file": request.file_uris.get("bank_statement_file"),
                    "user_data": request.user_answers
                },
                OrchestratorConfigV2.PARALLEL_TIMEOUT
            ),
        }
        
        # Run all in parallel
        parallel_results = await asyncio.gather(
            parallel_tasks["kyc"],
            parallel_tasks["face"],
            parallel_tasks["payslip"],
            parallel_tasks["bank"]
        )
        
        job_data["stages"]["kyc"] = parallel_results[0]
        job_data["stages"]["face"] = parallel_results[1]
        job_data["stages"]["payslip"] = parallel_results[2]
        job_data["stages"]["bank"] = parallel_results[3]
        
        logger.info("✅ All parallel agents completed\n")
        
        # Step 2: Merge results
        logger.info("🔗 STEP 2: Merging parallel agent results...")
        logger.info("-" * 70)
        
        merged_evidence = {
            "kyc_verified": job_data["stages"]["kyc"].get("verified", False),
            "kyc_data": job_data["stages"]["kyc"].get("data", {}),
            "face_verified": job_data["stages"]["face"].get("verified", False),
            "face_liveness": job_data["stages"]["face"].get("liveness_score", 0),
            "income_verified": job_data["stages"]["payslip"].get("verified", False),
            "monthly_income": job_data["stages"]["payslip"].get("monthly_income", request.user_answers.get("monthly_income")),
            "bank_balance": job_data["stages"]["bank"].get("balance", 0),
            "average_balance": job_data["stages"]["bank"].get("average_balance", 0),
        }
        
        logger.info(f"Merged evidence: {len(merged_evidence)} fields\n")
        
        # Step 3: Call credit agent
        logger.info("💳 STEP 3: Calling credit agent for final decision...")
        logger.info("-" * 70)
        
        credit_result = await call_agent(
            "credit",
            OrchestratorConfigV2.get_agent_url("credit"),
            {
                "application_id": app_id,
                "user_answers": request.user_answers,
                "loan_request": request.loan_request,
                "evidence": merged_evidence
            },
            OrchestratorConfigV2.CREDIT_TIMEOUT
        )
        
        job_data["stages"]["credit"] = credit_result
        
        logger.info("✅ Credit agent completed\n")
        
        # Step 4: Build final decision
        logger.info("📋 STEP 4: Building final decision...")
        logger.info("-" * 70)
        
        final_decision = {
            "job_id": job_id,
            "application_id": app_id,
            "status": credit_result.get("final_status", "PENDING"),
            "credit_score": credit_result.get("score", 0),
            "reason": credit_result.get("reason", ""),
            "approved_amount": credit_result.get("approved_amount"),
            "interest_rate": credit_result.get("interest_rate"),
            "monthly_emi": credit_result.get("monthly_emi"),
            "tenure_months": request.loan_request.get("tenure_months"),
            "evidence": {
                "kyc": job_data["stages"]["kyc"],
                "face": job_data["stages"]["face"],
                "payslip": job_data["stages"]["payslip"],
                "bank": job_data["stages"]["bank"],
                "credit": job_data["stages"]["credit"]
            },
            "processed_at": datetime.utcnow().isoformat()
        }
        
        job_data["final_decision"] = final_decision
        job_data["status"] = "COMPLETED"
        
        # Step 5: Save audit file
        audit_file = os.path.join(OrchestratorConfigV2.AUDIT_DIR, f"{job_id}.json")
        with open(audit_file, 'w') as f:
            json.dump(job_data, f, indent=2, default=str)
        
        logger.info(f"✅ Audit saved: {audit_file}\n")
        
        logger.info(f"{'='*70}")
        logger.info(f"✅ ORCHESTRATION COMPLETED: {final_decision['status']}")
        logger.info(f"{'='*70}\n")
        
        return OrchestrateResponse(
            job_id=job_id,
            application_id=app_id,
            status="COMPLETED",
            message=f"Orchestration completed. Status: {final_decision['status']}"
        )
    
    except Exception as e:
        logger.error(f"❌ Orchestration failed: {e}\n")
        job_data["status"] = "FAILED"
        job_data["error"] = str(e)
        
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str) -> JobStatus:
    """Get status of a job"""
    
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_store[job_id]
    
    return JobStatus(
        job_id=job_id,
        application_id=job["application_id"],
        status=job["status"],
        kyc_result=job["stages"].get("kyc"),
        face_result=job["stages"].get("face"),
        payslip_result=job["stages"].get("payslip"),
        bank_result=job["stages"].get("bank"),
        credit_result=job["stages"].get("credit"),
        final_decision=job.get("final_decision")
    )

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting Orchestrator on {OrchestratorConfigV2.ORCHESTRATOR_HOST}:{OrchestratorConfigV2.ORCHESTRATOR_PORT}...")
    uvicorn.run(
        app,
        host=OrchestratorConfigV2.ORCHESTRATOR_HOST,
        port=OrchestratorConfigV2.ORCHESTRATOR_PORT
    )
