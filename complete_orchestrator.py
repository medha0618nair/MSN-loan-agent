"""
Complete Multi-Agent Orchestrator for Loan Origination System.

Orchestrates 6 agents:
1. Intake Agent - Conversational loan application intake
2. KYC Agent - Document verification and parsing
3. Credit Agent - Credit scoring and evaluation
4. Payslip Agent - Income verification from payslips
5. Bank Agent - Bank statement parsing and analysis
6. Face Agent - Face detection and liveness verification
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import aiohttp

from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_community.chat_message_histories import ChatMessageHistory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentType_Enum(str, Enum):
    INTAKE = "intake"
    KYC = "kyc"
    CREDIT = "credit"
    PAYSLIP = "payslip"
    BANK = "bank"
    FACE = "face"


class AgentConfig:
    """Configuration for each agent microservice."""
    
    AGENTS = {
        AgentType_Enum.INTAKE: {
            "url": "http://localhost:8001",
            "endpoints": {
                "health": "/health",
                "converse": "/converse",
                "update_slot": "/update-slot",
                "register_upload": "/register-upload",
                "submit_application": "/submit-application"
            }
        },
        AgentType_Enum.KYC: {
            "url": "http://localhost:8002",
            "endpoints": {
                "health": "/health",
                "parse_document": "/parse-document"
            }
        },
        AgentType_Enum.CREDIT: {
            "url": "http://localhost:8003",
            "endpoints": {
                "health": "/health",
                "score_application": "/score-application",
                "get_model_info": "/model-info"
            }
        },
        AgentType_Enum.PAYSLIP: {
            "url": "http://localhost:8004",
            "endpoints": {
                "health": "/health",
                "verify_payslip": "/payslip/verify"
            }
        },
        AgentType_Enum.BANK: {
            "url": "http://localhost:8005",
            "endpoints": {
                "health": "/health",
                "parse_bank_statement": "/parse-bank-statement"
            }
        },
        AgentType_Enum.FACE: {
            "url": "http://localhost:8006",
            "endpoints": {
                "health": "/health",
                "verify_face": "/verify-face"
            }
        }
    }


class AgentClient:
    """HTTP client for agent communication."""
    
    def __init__(self, agent_type: AgentType_Enum):
        self.agent_type = agent_type
        self.config = AgentConfig.AGENTS[agent_type]
        self.base_url = self.config["url"]
        self.endpoints = self.config["endpoints"]
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
            url = f"{self.base_url}{self.endpoints['health']}"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"Health check failed for {self.agent_type}: {e}")
            return False
    
    async def call_endpoint(self, endpoint_name: str, method: str = "POST", data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict:
        """Call an agent endpoint."""
        try:
            endpoint = self.endpoints.get(endpoint_name)
            if not endpoint:
                raise ValueError(f"Unknown endpoint: {endpoint_name}")
            
            url = f"{self.base_url}{endpoint}"
            
            if method == "GET":
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    return await response.json()
            elif method == "POST":
                if files:
                    async with self.session.post(url, data=data, files=files, timeout=aiohttp.ClientTimeout(total=60)) as response:
                        return await response.json()
                else:
                    async with self.session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        return await response.json()
        except Exception as e:
            logger.error(f"Error calling {self.agent_type}.{endpoint_name}: {e}")
            raise


class LoanOrchestratorV2:
    """
    Advanced orchestrator coordinating 6 agents for complete loan processing.
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Initialize orchestrator with LLM and agent clients."""
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not provided")
        
        # Initialize LLM
        self.llm = ChatGroq(
            temperature=0,
            model="llama-3.1-70b-versatile",
            groq_api_key=self.groq_api_key
        )
        
        # Track application state
        self.applications: Dict[str, Dict[str, Any]] = {}
        
        # Initialize tools
        self._setup_tools()
    
    def _setup_tools(self) -> None:
        """Setup LangChain tools for each agent."""
        self.tools = [
            Tool(
                name="IntakeAgent",
                func=self._call_intake_agent,
                description="Handle conversational loan intake, slot filling, and application submission"
            ),
            Tool(
                name="KYCAgent",
                func=self._call_kyc_agent,
                description="Parse and validate identity documents (Aadhaar, PAN, Passport)"
            ),
            Tool(
                name="CreditAgent",
                func=self._call_credit_agent,
                description="Score credit application based on credit history and financial metrics"
            ),
            Tool(
                name="PayslipAgent",
                func=self._call_payslip_agent,
                description="Extract income information from payslips and verify employment"
            ),
            Tool(
                name="BankAgent",
                func=self._call_bank_agent,
                description="Parse bank statements and analyze financial behavior"
            ),
            Tool(
                name="FaceAgent",
                func=self._call_face_agent,
                description="Verify face identity and perform liveness detection"
            )
        ]
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _call_intake_agent(self, instruction: str) -> str:
        """Wrapper for intake agent calls."""
        return f"[INTAKE_AGENT] Processing: {instruction}"
    
    def _call_kyc_agent(self, instruction: str) -> str:
        """Wrapper for KYC agent calls."""
        return f"[KYC_AGENT] Processing: {instruction}"
    
    def _call_credit_agent(self, instruction: str) -> str:
        """Wrapper for credit agent calls."""
        return f"[CREDIT_AGENT] Processing: {instruction}"
    
    def _call_payslip_agent(self, instruction: str) -> str:
        """Wrapper for payslip agent calls."""
        return f"[PAYSLIP_AGENT] Processing: {instruction}"
    
    def _call_bank_agent(self, instruction: str) -> str:
        """Wrapper for bank agent calls."""
        return f"[BANK_AGENT] Processing: {instruction}"
    
    def _call_face_agent(self, instruction: str) -> str:
        """Wrapper for face agent calls."""
        return f"[FACE_AGENT] Processing: {instruction}"
    
    async def check_all_agents_health(self) -> Dict[str, bool]:
        """Check health of all agents."""
        health_status = {}
        
        tasks = []
        async with aiohttp.ClientSession() as session:
            for agent_type in AgentType_Enum:
                config = AgentConfig.AGENTS[agent_type]
                url = f"{config['url']}{config['endpoints']['health']}"
                tasks.append(self._check_health(session, agent_type, url))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for agent_type, result in zip(AgentType_Enum, results):
                if isinstance(result, Exception):
                    health_status[agent_type.value] = False
                else:
                    health_status[agent_type.value] = result
        
        return health_status
    
    async def _check_health(self, session, agent_type, url) -> bool:
        """Check single agent health."""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                return response.status == 200
        except:
            return False
    
    async def process_complete_application(
        self,
        application_id: str,
        applicant_info: Dict[str, Any],
        documents: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Process complete loan application through all relevant agents.
        
        Args:
            application_id: Unique application identifier
            applicant_info: Initial applicant information
            documents: File paths to documents (payslip, bank_statement, id, selfie)
        
        Returns:
            Complete application result with all agent outputs
        """
        logger.info(f"Starting complete application processing: {application_id}")
        
        # Initialize application state
        self.applications[application_id] = {
            "status": "in_progress",
            "created_at": datetime.utcnow().isoformat(),
            "applicant_info": applicant_info,
            "results": {}
        }
        
        try:
            # Step 1: Intake Agent - Collect basic information
            logger.info(f"[{application_id}] Step 1: Starting intake conversation")
            intake_result = await self._process_intake(application_id, applicant_info)
            self.applications[application_id]["results"]["intake"] = intake_result
            
            # Step 2: Face Verification
            if documents and "selfie" in documents:
                logger.info(f"[{application_id}] Step 2: Verifying face identity")
                face_result = await self._process_face_verification(application_id, documents["selfie"])
                self.applications[application_id]["results"]["face"] = face_result
            
            # Step 3: KYC Document Processing
            if documents and "id_document" in documents:
                logger.info(f"[{application_id}] Step 3: Processing KYC documents")
                kyc_result = await self._process_kyc(application_id, documents["id_document"])
                self.applications[application_id]["results"]["kyc"] = kyc_result
            
            # Step 4: Income Verification (Payslip + Bank Statement)
            income_results = {}
            
            if documents and "payslip" in documents:
                logger.info(f"[{application_id}] Step 4a: Processing payslip for income verification")
                payslip_result = await self._process_payslip(application_id, documents["payslip"])
                income_results["payslip"] = payslip_result
            
            if documents and "bank_statement" in documents:
                logger.info(f"[{application_id}] Step 4b: Processing bank statement")
                bank_result = await self._process_bank_statement(application_id, documents["bank_statement"])
                income_results["bank_statement"] = bank_result
            
            self.applications[application_id]["results"]["income"] = income_results
            
            # Step 5: Credit Scoring
            logger.info(f"[{application_id}] Step 5: Performing credit scoring")
            credit_result = await self._process_credit_scoring(
                application_id,
                applicant_info,
                income_results
            )
            self.applications[application_id]["results"]["credit"] = credit_result
            
            # Step 6: Final submission
            logger.info(f"[{application_id}] Step 6: Submitting application")
            submission_result = await self._submit_application(application_id)
            
            # Mark as complete
            self.applications[application_id]["status"] = "completed"
            self.applications[application_id]["completed_at"] = datetime.utcnow().isoformat()
            
            return self.applications[application_id]
        
        except Exception as e:
            logger.error(f"[{application_id}] Application processing failed: {e}")
            self.applications[application_id]["status"] = "failed"
            self.applications[application_id]["error"] = str(e)
            raise
    
    async def _process_intake(self, app_id: str, applicant_info: Dict) -> Dict:
        """Process through intake agent."""
        async with AgentClient(AgentType_Enum.INTAKE) as client:
            if not await client.health_check():
                raise Exception("Intake agent unavailable")
            
            payload = {
                "conversation_id": f"conv-{app_id}",
                "user_message": f"Starting loan application intake for {applicant_info.get('name', 'applicant')}",
                "application_id": app_id
            }
            
            result = await client.call_endpoint("converse", data=payload)
            return result
    
    async def _process_face_verification(self, app_id: str, selfie_path: str) -> Dict:
        """Process face verification."""
        async with AgentClient(AgentType_Enum.FACE) as client:
            if not await client.health_check():
                raise Exception("Face agent unavailable")
            
            # In real implementation, would read file and send as multipart
            payload = {
                "application_id": app_id,
                "image_path": selfie_path
            }
            
            result = await client.call_endpoint("verify_face", data=payload)
            return result
    
    async def _process_kyc(self, app_id: str, doc_path: str) -> Dict:
        """Process KYC documents."""
        async with AgentClient(AgentType_Enum.KYC) as client:
            if not await client.health_check():
                raise Exception("KYC agent unavailable")
            
            payload = {
                "application_id": app_id,
                "document_type": "aadhaar",
                "document_path": doc_path
            }
            
            result = await client.call_endpoint("parse_document", data=payload)
            return result
    
    async def _process_payslip(self, app_id: str, payslip_path: str) -> Dict:
        """Process payslip."""
        async with AgentClient(AgentType_Enum.PAYSLIP) as client:
            if not await client.health_check():
                raise Exception("Payslip agent unavailable")
            
            # In real implementation, would read file and send as multipart
            payload = {
                "application_id": app_id,
                "file_path": payslip_path
            }
            
            result = await client.call_endpoint("verify_payslip", data=payload)
            return result
    
    async def _process_bank_statement(self, app_id: str, statement_path: str) -> Dict:
        """Process bank statement."""
        async with AgentClient(AgentType_Enum.BANK) as client:
            if not await client.health_check():
                raise Exception("Bank agent unavailable")
            
            payload = {
                "application_id": app_id,
                "file_path": statement_path
            }
            
            result = await client.call_endpoint("parse_bank_statement", data=payload)
            return result
    
    async def _process_credit_scoring(self, app_id: str, applicant_info: Dict, income_data: Dict) -> Dict:
        """Process credit scoring."""
        async with AgentClient(AgentType_Enum.CREDIT) as client:
            if not await client.health_check():
                raise Exception("Credit agent unavailable")
            
            payload = {
                "application_id": app_id,
                "applicant_info": applicant_info,
                "income_verification": income_data
            }
            
            result = await client.call_endpoint("score_application", data=payload)
            return result
    
    async def _submit_application(self, app_id: str) -> Dict:
        """Submit application through intake agent."""
        async with AgentClient(AgentType_Enum.INTAKE) as client:
            if not await client.health_check():
                raise Exception("Intake agent unavailable")
            
            payload = {
                "application_id": app_id,
                "conversation_id": f"conv-{app_id}"
            }
            
            result = await client.call_endpoint("submit_application", data=payload)
            return result
    
    def get_application_status(self, application_id: str) -> Dict:
        """Get current application status."""
        return self.applications.get(application_id, {"error": "Application not found"})
    
    def get_all_applications(self) -> Dict:
        """Get all applications being processed."""
        return self.applications
    
    def generate_report(self, application_id: str) -> str:
        """Generate comprehensive application report."""
        app = self.applications.get(application_id)
        if not app:
            return "Application not found"
        
        report = f"""
        ============================================
        LOAN APPLICATION REPORT
        ============================================
        
        Application ID: {application_id}
        Status: {app['status']}
        Created: {app['created_at']}
        
        Applicant Information:
        {json.dumps(app['applicant_info'], indent=2)}
        
        Processing Results:
        """
        
        for agent_name, result in app['results'].items():
            report += f"\n{agent_name.upper()} Agent:\n{json.dumps(result, indent=2)}\n"
        
        return report


# Example usage
async def main():
    """Example of using the complete orchestrator."""
    
    # Initialize orchestrator
    orchestrator = LoanOrchestratorV2()
    
    # Check agent health
    print("Checking agent health...")
    health_status = await orchestrator.check_all_agents_health()
    print(f"Agent Status: {json.dumps(health_status, indent=2)}")
    
    # Example application
    app_id = "APP-20240101-001"
    applicant_info = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+91-9876543210",
        "employment_status": "salaried",
        "loan_amount_requested": 500000,
        "loan_tenure_months": 60
    }
    
    documents = {
        "id_document": "/path/to/aadhaar.pdf",
        "selfie": "/path/to/selfie.jpg",
        "payslip": "/path/to/payslip.pdf",
        "bank_statement": "/path/to/bank_statement.pdf"
    }
    
    # Process application
    try:
        result = await orchestrator.process_complete_application(
            app_id,
            applicant_info,
            documents
        )
        print(f"\nApplication processed successfully!")
        print(json.dumps(result, indent=2))
        
        # Generate report
        report = orchestrator.generate_report(app_id)
        print(report)
    
    except Exception as e:
        print(f"Error processing application: {e}")


if __name__ == "__main__":
    asyncio.run(main())
