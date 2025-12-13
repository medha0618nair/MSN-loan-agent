"""
Synchronous wrapper and orchestrator configuration for multi-agent system.
Provides easy-to-use synchronous API for loan application processing.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ApplicantInfo:
    """Applicant information schema."""
    name: str
    email: str
    phone: str
    date_of_birth: str
    address: str
    city: str
    state: str
    pincode: str
    employment_status: str  # 'salaried', 'self_employed', 'business'
    annual_income: float
    current_employer: str
    designation: str
    years_at_current_employer: int
    cibil_score: Optional[int] = None
    pan_number: str = None
    aadhaar_number: str = None
    loan_amount_requested: float = None
    loan_tenure_months: int = None
    loan_purpose: str = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class DocumentSet:
    """Collection of documents for application."""
    aadhaar: Optional[str] = None
    pan: Optional[str] = None
    passport: Optional[str] = None
    voter_id: Optional[str] = None
    driving_license: Optional[str] = None
    selfie: Optional[str] = None
    recent_payslip: Optional[str] = None
    payslips: Optional[List[str]] = None
    bank_statement: Optional[str] = None
    income_tax_return: Optional[str] = None
    employment_letter: Optional[str] = None
    property_documents: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ApplicationRequest:
    """Complete loan application request."""
    application_id: str
    applicant_info: ApplicantInfo
    documents: DocumentSet
    custom_fields: Optional[Dict[str, Any]] = None
    priority: str = "normal"  # 'normal', 'high', 'urgent'
    
    def to_dict(self) -> Dict:
        return {
            "application_id": self.application_id,
            "applicant_info": self.applicant_info.to_dict(),
            "documents": self.documents.to_dict(),
            "custom_fields": self.custom_fields or {},
            "priority": self.priority
        }


class OrchestratorConfig:
    """Configuration for orchestrator and agents."""
    
    # Agent URLs (can be overridden via environment)
    INTAKE_URL = "http://localhost:8001"
    KYC_URL = "http://localhost:8002"
    CREDIT_URL = "http://localhost:8003"
    PAYSLIP_URL = "http://localhost:8004"
    BANK_URL = "http://localhost:8005"
    FACE_URL = "http://localhost:8006"
    
    # Processing configuration
    PARALLEL_PROCESSING = True
    TIMEOUT_SECONDS = 60
    MAX_RETRIES = 2
    
    # Feature flags
    ENABLE_KYC = True
    ENABLE_FACE_VERIFICATION = True
    ENABLE_CREDIT_SCORING = True
    ENABLE_INCOME_VERIFICATION = True
    ENABLE_COMPLIANCE_CHECKS = True
    
    # Logging
    LOG_LEVEL = logging.INFO


class ProcessingPipeline:
    """Defines the order and dependencies of agent processing."""
    
    # Sequential stages in loan processing
    STAGES = [
        {
            "stage": 1,
            "name": "intake",
            "agents": ["intake"],
            "description": "Collect applicant information",
            "required": True
        },
        {
            "stage": 2,
            "name": "verification",
            "agents": ["face", "kyc"],
            "description": "Identity and document verification",
            "required": True,
            "parallel": True
        },
        {
            "stage": 3,
            "name": "income_verification",
            "agents": ["payslip", "bank"],
            "description": "Income and financial verification",
            "required": True,
            "parallel": True
        },
        {
            "stage": 4,
            "name": "credit_assessment",
            "agents": ["credit"],
            "description": "Credit scoring and risk assessment",
            "required": True
        },
        {
            "stage": 5,
            "name": "submission",
            "agents": ["intake"],
            "description": "Application submission",
            "required": True
        }
    ]
    
    @classmethod
    def get_stage_by_name(cls, stage_name: str) -> Optional[Dict]:
        """Get stage configuration by name."""
        for stage in cls.STAGES:
            if stage["name"] == stage_name:
                return stage
        return None
    
    @classmethod
    def get_next_stage(cls, current_stage: int) -> Optional[Dict]:
        """Get next stage after current."""
        for stage in cls.STAGES:
            if stage["stage"] == current_stage + 1:
                return stage
        return None


class SyncOrchestrator:
    """Synchronous wrapper for the async orchestrator."""
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """Initialize with optional configuration."""
        self.config = config or OrchestratorConfig()
        self._setup_logging()
        self.applications = {}
    
    def _setup_logging(self):
        """Setup logging based on config."""
        logging.basicConfig(level=self.config.LOG_LEVEL)
    
    def process_application(
        self,
        application_request: ApplicationRequest
    ) -> Dict[str, Any]:
        """
        Synchronously process a loan application.
        
        Args:
            application_request: Complete application request
        
        Returns:
            Processing result with all agent outputs
        """
        # Import here to avoid circular imports
        from complete_orchestrator import LoanOrchestratorV2
        
        try:
            # Create async orchestrator
            orchestrator = LoanOrchestratorV2()
            
            # Run async processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                orchestrator.process_complete_application(
                    application_request.application_id,
                    application_request.applicant_info.to_dict(),
                    application_request.documents.to_dict()
                )
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Application processing failed: {e}")
            return {
                "status": "failed",
                "application_id": application_request.application_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def check_agent_health(self) -> Dict[str, bool]:
        """Check health of all agents (synchronously)."""
        from complete_orchestrator import LoanOrchestratorV2
        
        try:
            orchestrator = LoanOrchestratorV2()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            health = loop.run_until_complete(
                orchestrator.check_all_agents_health()
            )
            
            return health
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"error": str(e)}
    
    def get_application_details(self, application_id: str) -> Dict:
        """Get details of a specific application."""
        return self.applications.get(
            application_id,
            {"error": "Application not found", "application_id": application_id}
        )


# Convenience functions for easy usage
def create_applicant(
    name: str,
    email: str,
    phone: str,
    date_of_birth: str,
    address: str,
    city: str,
    state: str,
    pincode: str,
    employment_status: str,
    annual_income: float,
    current_employer: str,
    designation: str,
    years_at_current_employer: int,
    **kwargs
) -> ApplicantInfo:
    """Create applicant info easily."""
    return ApplicantInfo(
        name=name,
        email=email,
        phone=phone,
        date_of_birth=date_of_birth,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        employment_status=employment_status,
        annual_income=annual_income,
        current_employer=current_employer,
        designation=designation,
        years_at_current_employer=years_at_current_employer,
        **kwargs
    )


def create_documents(
    aadhaar: Optional[str] = None,
    pan: Optional[str] = None,
    passport: Optional[str] = None,
    selfie: Optional[str] = None,
    recent_payslip: Optional[str] = None,
    bank_statement: Optional[str] = None,
    **kwargs
) -> DocumentSet:
    """Create document set easily."""
    return DocumentSet(
        aadhaar=aadhaar,
        pan=pan,
        passport=passport,
        selfie=selfie,
        recent_payslip=recent_payslip,
        bank_statement=bank_statement,
        **kwargs
    )


def create_application_request(
    application_id: str,
    applicant_info: ApplicantInfo,
    documents: DocumentSet,
    loan_amount: float = None,
    loan_tenure_months: int = None,
    loan_purpose: str = None,
    **kwargs
) -> ApplicationRequest:
    """Create complete application request."""
    # Update applicant info with loan details
    applicant_info.loan_amount_requested = loan_amount
    applicant_info.loan_tenure_months = loan_tenure_months
    applicant_info.loan_purpose = loan_purpose
    
    return ApplicationRequest(
        application_id=application_id,
        applicant_info=applicant_info,
        documents=documents,
        **kwargs
    )


# Example usage
if __name__ == "__main__":
    # Create applicant
    applicant = create_applicant(
        name="Raj Kumar",
        email="raj@example.com",
        phone="+91-9876543210",
        date_of_birth="1990-05-15",
        address="123 Main Street",
        city="Bangalore",
        state="Karnataka",
        pincode="560001",
        employment_status="salaried",
        annual_income=800000,
        current_employer="TechCorp Inc",
        designation="Senior Software Engineer",
        years_at_current_employer=5,
        cibil_score=750
    )
    
    # Create documents
    documents = create_documents(
        aadhaar="/path/to/aadhaar.pdf",
        pan="/path/to/pan.pdf",
        selfie="/path/to/selfie.jpg",
        recent_payslip="/path/to/payslip.pdf",
        bank_statement="/path/to/bank_statement.pdf"
    )
    
    # Create application request
    app_request = create_application_request(
        application_id="APP-20240101-001",
        applicant_info=applicant,
        documents=documents,
        loan_amount=500000,
        loan_tenure_months=60,
        loan_purpose="Home Purchase"
    )
    
    # Process application
    orchestrator = SyncOrchestrator()
    
    print("Checking agent health...")
    health = orchestrator.check_agent_health()
    print(json.dumps(health, indent=2))
    
    print("\nProcessing application...")
    result = orchestrator.process_application(app_request)
    print(json.dumps(result, indent=2, default=str))
