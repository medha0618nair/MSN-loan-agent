"""
Orchestrator Configuration v2 - Docker Version
Uses internal Docker service names for inter-service communication
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration for each agent"""
    name: str
    url: str
    endpoint: str
    timeout: int = 30
    retries: int = 2

class OrchestratorConfigV2Docker:
    """Docker-aware orchestrator configuration"""
    
    # Use environment variables with fallbacks for local development
    INTAKE_URL = os.getenv("INTAKE_URL", "http://intake:8000")
    KYC_URL = os.getenv("KYC_URL", "http://kyc:8000")
    FACE_URL = os.getenv("FACE_URL", "http://face:8000")
    PAYSLIP_URL = os.getenv("PAYSLIP_URL", "http://payslip:8000")
    BANK_URL = os.getenv("BANK_URL", "http://bank:8000")
    CREDIT_URL = os.getenv("CREDIT_URL", "http://credit:8000")
    
    # Orchestrator settings
    ORCHESTRATOR_PORT = 9000
    ORCHESTRATOR_HOST = "0.0.0.0"
    
    # Intake Agent
    INTAKE_AGENT = AgentConfig(
        name="intake",
        url=INTAKE_URL,
        endpoint="/start"
    )
    
    # Parallel agents (after intake)
    PARALLEL_AGENTS = {
        "kyc": AgentConfig(
            name="kyc",
            url=KYC_URL,
            endpoint="/kyc/parse"
        ),
        "face": AgentConfig(
            name="face",
            url=FACE_URL,
            endpoint="/face/verify"
        ),
        "payslip": AgentConfig(
            name="payslip",
            url=PAYSLIP_URL,
            endpoint="/extract"
        ),
        "bank": AgentConfig(
            name="bank",
            url=BANK_URL,
            endpoint="/bank/parse"
        ),
    }
    
    # Final agent
    CREDIT_AGENT = AgentConfig(
        name="credit",
        url=CREDIT_URL,
        endpoint="/score"
    )
    
    # All agents
    ALL_AGENTS = {
        "intake": INTAKE_AGENT,
        **PARALLEL_AGENTS,
        "credit": CREDIT_AGENT
    }
    
    # Timeouts
    HEALTH_CHECK_TIMEOUT = 5
    AGENT_TIMEOUT = 30
    
    # Paths
    AUDIT_DIR = "./audit"
    JOBS_DIR = "./jobs"
