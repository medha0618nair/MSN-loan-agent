"""
Orchestrator Configuration v2
Defines all agent endpoints and settings
"""

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

class OrchestratorConfigV2:
    """Master orchestrator configuration"""
    
    # Orchestrator settings
    ORCHESTRATOR_PORT = 9000
    ORCHESTRATOR_HOST = "0.0.0.0"
    
    # Intake Agent
    INTAKE_AGENT = AgentConfig(
        name="intake",
        url="http://localhost:8001",
        endpoint="/start"
    )
    
    # Parallel agents (after intake)
    PARALLEL_AGENTS = {
        "kyc": AgentConfig(
            name="kyc",
            url="http://localhost:8002",
            endpoint="/kyc/parse"
        ),
        "face": AgentConfig(
            name="face",
            url="http://localhost:8003",
            endpoint="/face/verify"
        ),
        "payslip": AgentConfig(
            name="payslip",
            url="http://localhost:8004",
            endpoint="/payslip/parse"
        ),
        "bank": AgentConfig(
            name="bank",
            url="http://localhost:8005",
            endpoint="/bank/parse"
        ),
    }
    
    # Final decision agent
    CREDIT_AGENT = AgentConfig(
        name="credit",
        url="http://localhost:8006",
        endpoint="/score"
    )
    
    # All agents for health check
    ALL_AGENTS = {
        "intake": INTAKE_AGENT,
        "kyc": PARALLEL_AGENTS["kyc"],
        "face": PARALLEL_AGENTS["face"],
        "payslip": PARALLEL_AGENTS["payslip"],
        "bank": PARALLEL_AGENTS["bank"],
        "credit": CREDIT_AGENT,
    }
    
    # Processing settings
    PARALLEL_TIMEOUT = 60  # timeout for parallel agent calls
    CREDIT_TIMEOUT = 30    # timeout for credit agent
    HEALTH_CHECK_TIMEOUT = 2
    
    # Storage
    AUDIT_DIR = "./audit"
    JOBS_DIR = "./jobs"
    
    @classmethod
    def get_agent_url(cls, agent_name: str) -> str:
        """Get full URL for agent"""
        if agent_name in cls.PARALLEL_AGENTS:
            config = cls.PARALLEL_AGENTS[agent_name]
        elif agent_name == "credit":
            config = cls.CREDIT_AGENT
        else:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        return f"{config.url}{config.endpoint}"
