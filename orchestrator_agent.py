"""
Master Orchestrator Agent - Coordinates entire loan processing workflow

Execution Order:
1. Intake Agent       - Collect applicant info
2. KYC Agent         - Verify identity documents
3. Face Agent        - Verify face identity & liveness
4. Payslip Agent     - Verify income from payslip
5. Bank Agent        - Analyze bank statements
6. Credit Decision   - Final scoring & decision
7. Return Final Decision

Author: Multi-Agent Orchestration System
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp

from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProcessingStage(str, Enum):
    """Processing stages in order."""
    INTAKE = "intake"
    KYC = "kyc"
    FACE = "face"
    PAYSLIP = "payslip"
    BANK = "bank"
    CREDIT = "credit"
    FINAL = "final"


@dataclass
class StageConfig:
    """Configuration for each processing stage."""
    stage: ProcessingStage
    port: int
    endpoint: str
    description: str
    required: bool = True
    parallel_with: Optional[List[ProcessingStage]] = None


class OrchestratorConfig:
    """Master orchestrator configuration."""
    
    # Execution order: STRICTLY SEQUENTIAL
    PROCESSING_ORDER = [
        ProcessingStage.INTAKE,
        ProcessingStage.KYC,
        ProcessingStage.FACE,
        ProcessingStage.PAYSLIP,
        ProcessingStage.BANK,
        ProcessingStage.CREDIT,
    ]
    
    # Agent configurations
    AGENTS = {
        ProcessingStage.INTAKE: {
            "url": "http://localhost:8001",
            "endpoint": "/start",
            "method": "POST",
            "description": "Conversational intake - collect applicant info (strict sequential flow)"
        },
        ProcessingStage.KYC: {
            "url": "http://localhost:8002",
            "endpoint": "/parse-document",
            "method": "POST",
            "description": "KYC verification - parse identity documents"
        },
        ProcessingStage.FACE: {
            "url": "http://localhost:8003",
            "endpoint": "/verify-face",
            "method": "POST",
            "description": "Face verification - liveness & identity match"
        },
        ProcessingStage.PAYSLIP: {
            "url": "http://localhost:8004",
            "endpoint": "/payslip/verify",
            "method": "POST",
            "description": "Income verification - parse payslip"
        },
        ProcessingStage.BANK: {
            "url": "http://localhost:8005",
            "endpoint": "/parse-bank-statement",
            "method": "POST",
            "description": "Bank analysis - statement parsing"
        },
        ProcessingStage.CREDIT: {
            "url": "http://localhost:8006",
            "endpoint": "/score-application",
            "method": "POST",
            "description": "Credit decision - scoring & final decision"
        },
    }
    
    # Timeouts
    HEALTH_CHECK_TIMEOUT = 5
    PROCESSING_TIMEOUT = 60
    MAX_RETRIES = 2
    
    # Logging
    LOG_LEVEL = logging.INFO


class EvidenceCollector:
    """Collects and manages evidence from all agents."""
    
    def __init__(self, application_id: str):
        self.application_id = application_id
        self.evidence: Dict[ProcessingStage, Dict[str, Any]] = {}
        self.timestamps: Dict[ProcessingStage, str] = {}
        self.errors: Dict[ProcessingStage, str] = {}
        self.status: Dict[ProcessingStage, str] = {}
    
    def add_evidence(self, stage: ProcessingStage, data: Dict[str, Any]) -> None:
        """Add evidence from a processing stage."""
        self.evidence[stage] = data
        self.timestamps[stage] = datetime.utcnow().isoformat()
        self.status[stage] = "completed"
        logger.info(f"[{self.application_id}] Evidence collected from {stage.value}")
    
    def add_error(self, stage: ProcessingStage, error: str) -> None:
        """Record error from a stage."""
        self.errors[stage] = error
        self.status[stage] = "failed"
        logger.error(f"[{self.application_id}] Error in {stage.value}: {error}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get evidence summary."""
        return {
            "application_id": self.application_id,
            "timestamp": datetime.utcnow().isoformat(),
            "evidence": self.evidence,
            "status": self.status,
            "errors": self.errors,
            "timestamps": self.timestamps
        }


class AgentClient:
    """HTTP client for agent communication."""
    
    def __init__(self, stage: ProcessingStage):
        self.stage = stage
        self.config = OrchestratorConfig.AGENTS[stage]
        self.base_url = self.config["url"]
        self.endpoint = self.config["endpoint"]
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> bool:
        """Check if agent is healthy."""
        try:
            url = f"{self.base_url}/health"
            async with self.session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=OrchestratorConfig.HEALTH_CHECK_TIMEOUT)
            ) as response:
                is_healthy = response.status == 200
                logger.info(f"Health check {self.stage.value}: {'✅' if is_healthy else '❌'}")
                return is_healthy
        except Exception as e:
            logger.warning(f"Health check failed for {self.stage.value}: {e}")
            return False
    
    async def call_endpoint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call agent endpoint with payload."""
        try:
            url = f"{self.base_url}{self.endpoint}"
            method = self.config["method"]
            
            logger.info(f"[{self.stage.value}] Calling endpoint: {url}")
            
            if method == "POST":
                async with self.session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=OrchestratorConfig.PROCESSING_TIMEOUT)
                ) as response:
                    result = await response.json()
                    logger.info(f"[{self.stage.value}] Response status: {response.status}")
                    return result
            else:
                async with self.session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=OrchestratorConfig.PROCESSING_TIMEOUT)
                ) as response:
                    result = await response.json()
                    return result
        
        except Exception as e:
            logger.error(f"Error calling {self.stage.value}: {e}")
            raise


class MasterOrchestrator:
    """
    Master orchestrator that coordinates all agents in strict order.
    
    Execution flow:
    1. Intake Agent       → Collect applicant information
    2. KYC Agent         → Verify identity documents
    3. Face Agent        → Verify face & liveness
    4. Payslip Agent     → Verify income
    5. Bank Agent        → Analyze financials
    6. Credit Agent      → Final decision
    → Return comprehensive decision
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Initialize orchestrator with LLM."""
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            logger.warning("GROQ_API_KEY not set - LLM features disabled")
        
        # Initialize LLM if available
        if self.groq_api_key:
            self.llm = ChatGroq(
                temperature=0,
                model="llama-3.1-70b-versatile",
                groq_api_key=self.groq_api_key
            )
        else:
            self.llm = None
        
        self.applications: Dict[str, Dict[str, Any]] = {}
    
    async def check_all_agents_health(self) -> Dict[str, bool]:
        """Check health of all agents."""
        logger.info("🏥 Checking health of all agents...")
        health_status = {}
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for stage in OrchestratorConfig.PROCESSING_ORDER:
                client = AgentClient(stage)
                client.session = session
                tasks.append(self._check_health(client, stage))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for stage, result in zip(OrchestratorConfig.PROCESSING_ORDER, results):
                if isinstance(result, Exception):
                    health_status[stage.value] = False
                else:
                    health_status[stage.value] = result
        
        return health_status
    
    async def _check_health(self, client: AgentClient, stage: ProcessingStage) -> bool:
        """Check single agent health."""
        try:
            return await client.health_check()
        except:
            return False
    
    async def process_application(
        self,
        application_id: str,
        applicant_data: Dict[str, Any],
        documents: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Process complete loan application through all agents IN ORDER.
        
        Args:
            application_id: Unique application ID
            applicant_data: Initial applicant information
            documents: File paths to documents
        
        Returns:
            Final decision with all evidence
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 STARTING APPLICATION PROCESSING: {application_id}")
        logger.info(f"{'='*70}\n")
        
        start_time = datetime.utcnow()
        evidence_collector = EvidenceCollector(application_id)
        
        # Store in applications
        self.applications[application_id] = {
            "status": "in_progress",
            "started_at": start_time.isoformat(),
            "applicant_data": applicant_data,
            "evidence": evidence_collector
        }
        
        try:
            # Execute each stage in strict order
            for stage in OrchestratorConfig.PROCESSING_ORDER:
                logger.info(f"\n{'─'*70}")
                logger.info(f"STAGE: {stage.value.upper()}")
                logger.info(f"{'─'*70}")
                
                try:
                    # Process this stage
                    result = await self._process_stage(
                        stage,
                        application_id,
                        applicant_data,
                        documents,
                        evidence_collector
                    )
                    
                    # Add to evidence
                    evidence_collector.add_evidence(stage, result)
                    
                    logger.info(f"✅ {stage.value} completed successfully\n")
                
                except Exception as e:
                    logger.error(f"❌ {stage.value} failed: {e}\n")
                    evidence_collector.add_error(stage, str(e))
                    
                    # Decide if we should continue or stop
                    if stage in [ProcessingStage.INTAKE, ProcessingStage.KYC, ProcessingStage.FACE]:
                        # Critical stages - stop processing
                        logger.error(f"Critical stage {stage.value} failed - stopping processing")
                        raise
            
            # All stages completed - generate final decision
            logger.info(f"\n{'='*70}")
            logger.info("FINAL DECISION")
            logger.info(f"{'='*70}\n")
            
            final_decision = await self._generate_final_decision(
                application_id,
                evidence_collector
            )
            
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Store result
            self.applications[application_id]["status"] = "completed"
            self.applications[application_id]["completed_at"] = end_time.isoformat()
            self.applications[application_id]["processing_time_seconds"] = processing_time
            self.applications[application_id]["final_decision"] = final_decision
            
            logger.info(f"✅ Application processing completed in {processing_time:.2f} seconds")
            logger.info(f"{'='*70}\n")
            
            return final_decision
        
        except Exception as e:
            logger.error(f"\n❌ Application processing failed: {e}")
            self.applications[application_id]["status"] = "failed"
            self.applications[application_id]["error"] = str(e)
            raise
    
    async def _process_stage(
        self,
        stage: ProcessingStage,
        app_id: str,
        applicant_data: Dict[str, Any],
        documents: Dict[str, str],
        evidence_collector: EvidenceCollector
    ) -> Dict[str, Any]:
        """Process a single stage."""
        
        config = OrchestratorConfig.AGENTS[stage]
        logger.info(f"Description: {config['description']}")
        logger.info(f"Endpoint: {config['url']}{config['endpoint']}")
        
        # Build payload based on stage
        payload = self._build_payload(stage, app_id, applicant_data, documents, evidence_collector)
        
        # Call agent
        async with AgentClient(stage) as client:
            result = await client.call_endpoint(payload)
            return result
    
    def _build_payload(
        self,
        stage: ProcessingStage,
        app_id: str,
        applicant_data: Dict[str, Any],
        documents: Dict[str, str],
        evidence_collector: EvidenceCollector
    ) -> Dict[str, Any]:
        """Build payload for each agent."""
        
        if stage == ProcessingStage.INTAKE:
            return {
                "application_id": app_id,
                "conversation_id": f"conv-{app_id}",
                "user_message": f"Starting loan application for {applicant_data.get('name', 'applicant')}",
                "applicant_info": applicant_data
            }
        
        elif stage == ProcessingStage.KYC:
            return {
                "application_id": app_id,
                "document_type": "aadhaar",
                "document_path": documents.get("aadhaar") if documents else "",
                "applicant_info": applicant_data
            }
        
        elif stage == ProcessingStage.FACE:
            return {
                "application_id": app_id,
                "image_path": documents.get("selfie") if documents else "",
                "applicant_info": applicant_data
            }
        
        elif stage == ProcessingStage.PAYSLIP:
            return {
                "application_id": app_id,
                "file_path": documents.get("payslip") if documents else "",
                "applicant_info": applicant_data
            }
        
        elif stage == ProcessingStage.BANK:
            return {
                "application_id": app_id,
                "file_path": documents.get("bank_statement") if documents else "",
                "applicant_info": applicant_data,
                "income_from_payslip": evidence_collector.evidence.get(ProcessingStage.PAYSLIP, {})
            }
        
        elif stage == ProcessingStage.CREDIT:
            return {
                "application_id": app_id,
                "applicant_info": applicant_data,
                "kyc_result": evidence_collector.evidence.get(ProcessingStage.KYC, {}),
                "face_result": evidence_collector.evidence.get(ProcessingStage.FACE, {}),
                "payslip_result": evidence_collector.evidence.get(ProcessingStage.PAYSLIP, {}),
                "bank_result": evidence_collector.evidence.get(ProcessingStage.BANK, {})
            }
        
        return {}
    
    async def _generate_final_decision(
        self,
        app_id: str,
        evidence_collector: EvidenceCollector
    ) -> Dict[str, Any]:
        """Generate final decision from all evidence."""
        
        summary = evidence_collector.get_summary()
        
        # Extract key decisions
        kyc_verified = summary["evidence"].get(ProcessingStage.KYC, {}).get("verified", False)
        face_verified = summary["evidence"].get(ProcessingStage.FACE, {}).get("verified", False)
        credit_result = summary["evidence"].get(ProcessingStage.CREDIT, {})
        
        # Determine final status
        if not kyc_verified or not face_verified:
            final_status = "REJECTED"
            reason = "Identity verification failed"
        elif credit_result.get("risk_level") == "High":
            final_status = "REJECTED"
            reason = "High credit risk"
        elif credit_result.get("risk_level") == "Medium":
            final_status = "MANUAL_REVIEW"
            reason = "Medium risk - requires manual review"
        else:
            final_status = "APPROVED"
            reason = "All verifications passed - Low risk"
        
        final_decision = {
            "application_id": app_id,
            "final_status": final_status,
            "reason": reason,
            "processed_at": datetime.utcnow().isoformat(),
            "evidence_summary": summary,
            "recommendation": {
                "action": final_status,
                "loan_amount": credit_result.get("recommended_loan_amount"),
                "interest_rate": credit_result.get("interest_rate"),
                "tenure_months": credit_result.get("recommended_tenure_months")
            }
        }
        
        logger.info(f"Final Status: {final_status}")
        logger.info(f"Reason: {reason}")
        logger.info(f"Loan Amount: {final_decision['recommendation']['loan_amount']}")
        logger.info(f"Interest Rate: {final_decision['recommendation']['interest_rate']}%")
        
        return final_decision
    
    def get_application_result(self, app_id: str) -> Dict[str, Any]:
        """Get complete application result."""
        app = self.applications.get(app_id)
        if not app:
            return {"error": "Application not found"}
        
        return {
            "application_id": app_id,
            "status": app["status"],
            "started_at": app.get("started_at"),
            "completed_at": app.get("completed_at"),
            "processing_time_seconds": app.get("processing_time_seconds"),
            "final_decision": app.get("final_decision"),
            "evidence": app.get("evidence").get_summary() if app.get("evidence") else None
        }


# Example usage and testing
async def main():
    """Example of using the master orchestrator."""
    
    logger.info("Initializing Master Orchestrator...")
    orchestrator = MasterOrchestrator()
    
    # Check health
    logger.info("Checking agent health...")
    health = await orchestrator.check_all_agents_health()
    
    logger.info("\nAgent Health Status:")
    for agent, status in health.items():
        logger.info(f"  {'✅' if status else '❌'} {agent.upper()}: {'Healthy' if status else 'Unhealthy'}")
    
    # Example application
    app_id = "MASTER-ORK-001"
    applicant_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+91-9876543210",
        "employment_status": "salaried",
        "annual_income": 800000,
        "current_employer": "TechCorp",
        "designation": "Engineer",
        "years_at_current_employer": 5,
        "loan_amount_requested": 500000,
        "loan_tenure_months": 60
    }
    
    documents = {
        "aadhaar": "/path/to/aadhaar.pdf",
        "selfie": "/path/to/selfie.jpg",
        "payslip": "/path/to/payslip.pdf",
        "bank_statement": "/path/to/bank_statement.pdf"
    }
    
    try:
        # Process application
        result = await orchestrator.process_application(
            app_id,
            applicant_data,
            documents
        )
        
        logger.info("\n" + "="*70)
        logger.info("FINAL RESULT")
        logger.info("="*70)
        logger.info(json.dumps(result, indent=2, default=str))
    
    except Exception as e:
        logger.error(f"Application processing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
