"""
Integration tests and validation for the multi-agent orchestrator.

Run with: pytest test_orchestrator.py -v
"""

import pytest
import asyncio
import json
from pathlib import Path
from typing import Dict, Any

# Test configuration
TEST_APP_ID = "TEST-INTEGRATION-001"
TEST_TIMEOUT = 30


class TestOrchestratorConfiguration:
    """Test orchestrator configuration and setup."""
    
    def test_import_sync_orchestrator(self):
        """Test importing synchronous orchestrator."""
        from orchestrator_sync import SyncOrchestrator, OrchestratorConfig
        assert SyncOrchestrator is not None
        assert OrchestratorConfig is not None
    
    def test_import_async_orchestrator(self):
        """Test importing async orchestrator."""
        from complete_orchestrator import LoanOrchestratorV2, AgentConfig
        assert LoanOrchestratorV2 is not None
        assert AgentConfig is not None
    
    def test_import_cli(self):
        """Test importing CLI module."""
        from orchestrator_cli import OrchestratorCLI
        assert OrchestratorCLI is not None
    
    def test_example_config_valid(self):
        """Test example configuration is valid JSON."""
        config_file = Path("example_application_config.json")
        assert config_file.exists(), "example_application_config.json not found"
        
        with open(config_file) as f:
            config = json.load(f)
        
        assert "application_id" in config
        assert "applicant_info" in config
        assert "documents" in config
    
    def test_orchestrator_config(self):
        """Test orchestrator configuration."""
        from orchestrator_sync import OrchestratorConfig
        
        assert OrchestratorConfig.INTAKE_URL
        assert OrchestratorConfig.KYC_URL
        assert OrchestratorConfig.CREDIT_URL
        assert OrchestratorConfig.PAYSLIP_URL
        assert OrchestratorConfig.BANK_URL
        assert OrchestratorConfig.FACE_URL


class TestDataModels:
    """Test data models and schemas."""
    
    def test_applicant_info_creation(self):
        """Test creating applicant info."""
        from orchestrator_sync import ApplicantInfo
        
        applicant = ApplicantInfo(
            name="Test User",
            email="test@example.com",
            phone="+91-9876543210",
            date_of_birth="1990-01-01",
            address="123 Test Street",
            city="Test City",
            state="Test State",
            pincode="123456",
            employment_status="salaried",
            annual_income=500000,
            current_employer="Test Corp",
            designation="Test Engineer",
            years_at_current_employer=3
        )
        
        assert applicant.name == "Test User"
        assert applicant.email == "test@example.com"
        assert applicant.annual_income == 500000
    
    def test_applicant_info_to_dict(self):
        """Test converting applicant info to dict."""
        from orchestrator_sync import ApplicantInfo
        
        applicant = ApplicantInfo(
            name="Test User",
            email="test@example.com",
            phone="+91-9876543210",
            date_of_birth="1990-01-01",
            address="123 Test Street",
            city="Test City",
            state="Test State",
            pincode="123456",
            employment_status="salaried",
            annual_income=500000,
            current_employer="Test Corp",
            designation="Test Engineer",
            years_at_current_employer=3
        )
        
        data = applicant.to_dict()
        assert isinstance(data, dict)
        assert data["name"] == "Test User"
        assert "cibil_score" not in data  # None values excluded
    
    def test_document_set_creation(self):
        """Test creating document set."""
        from orchestrator_sync import DocumentSet
        
        docs = DocumentSet(
            aadhaar="/path/to/aadhaar.pdf",
            selfie="/path/to/selfie.jpg"
        )
        
        assert docs.aadhaar == "/path/to/aadhaar.pdf"
        assert docs.selfie == "/path/to/selfie.jpg"
        assert docs.pan is None
    
    def test_document_set_to_dict(self):
        """Test converting document set to dict."""
        from orchestrator_sync import DocumentSet
        
        docs = DocumentSet(
            aadhaar="/path/to/aadhaar.pdf",
            selfie="/path/to/selfie.jpg"
        )
        
        data = docs.to_dict()
        assert isinstance(data, dict)
        assert len(data) == 2
        assert "pan" not in data  # None values excluded
    
    def test_application_request_creation(self):
        """Test creating application request."""
        from orchestrator_sync import (
            ApplicantInfo,
            DocumentSet,
            ApplicationRequest
        )
        
        applicant = ApplicantInfo(
            name="Test User",
            email="test@example.com",
            phone="+91-9876543210",
            date_of_birth="1990-01-01",
            address="123 Test Street",
            city="Test City",
            state="Test State",
            pincode="123456",
            employment_status="salaried",
            annual_income=500000,
            current_employer="Test Corp",
            designation="Test Engineer",
            years_at_current_employer=3
        )
        
        docs = DocumentSet(
            aadhaar="/path/to/aadhaar.pdf",
            selfie="/path/to/selfie.jpg"
        )
        
        request = ApplicationRequest(
            application_id="TEST-001",
            applicant_info=applicant,
            documents=docs
        )
        
        assert request.application_id == "TEST-001"
        assert request.applicant_info.name == "Test User"
        assert request.documents.aadhaar == "/path/to/aadhaar.pdf"


class TestConvenienceFunctions:
    """Test convenience functions for easy model creation."""
    
    def test_create_applicant(self):
        """Test create_applicant convenience function."""
        from orchestrator_sync import create_applicant
        
        applicant = create_applicant(
            name="Test User",
            email="test@example.com",
            phone="+91-9876543210",
            date_of_birth="1990-01-01",
            address="123 Test Street",
            city="Test City",
            state="Test State",
            pincode="123456",
            employment_status="salaried",
            annual_income=500000,
            current_employer="Test Corp",
            designation="Test Engineer",
            years_at_current_employer=3
        )
        
        assert applicant.name == "Test User"
    
    def test_create_documents(self):
        """Test create_documents convenience function."""
        from orchestrator_sync import create_documents
        
        docs = create_documents(
            aadhaar="/path/to/aadhaar.pdf",
            selfie="/path/to/selfie.jpg"
        )
        
        assert docs.aadhaar == "/path/to/aadhaar.pdf"
    
    def test_create_application_request(self):
        """Test create_application_request convenience function."""
        from orchestrator_sync import (
            create_applicant,
            create_documents,
            create_application_request
        )
        
        applicant = create_applicant(
            name="Test User",
            email="test@example.com",
            phone="+91-9876543210",
            date_of_birth="1990-01-01",
            address="123 Test Street",
            city="Test City",
            state="Test State",
            pincode="123456",
            employment_status="salaried",
            annual_income=500000,
            current_employer="Test Corp",
            designation="Test Engineer",
            years_at_current_employer=3
        )
        
        docs = create_documents(
            aadhaar="/path/to/aadhaar.pdf"
        )
        
        request = create_application_request(
            application_id="TEST-001",
            applicant_info=applicant,
            documents=docs,
            loan_amount=500000,
            loan_tenure_months=60
        )
        
        assert request.application_id == "TEST-001"
        assert applicant.loan_amount_requested == 500000


class TestProcessingPipeline:
    """Test processing pipeline configuration."""
    
    def test_pipeline_stages(self):
        """Test pipeline stages are defined."""
        from orchestrator_sync import ProcessingPipeline
        
        assert len(ProcessingPipeline.STAGES) > 0
        assert ProcessingPipeline.STAGES[0]["name"] == "intake"
    
    def test_get_stage_by_name(self):
        """Test getting stage by name."""
        from orchestrator_sync import ProcessingPipeline
        
        stage = ProcessingPipeline.get_stage_by_name("intake")
        assert stage is not None
        assert stage["name"] == "intake"
    
    def test_get_next_stage(self):
        """Test getting next stage."""
        from orchestrator_sync import ProcessingPipeline
        
        next_stage = ProcessingPipeline.get_next_stage(1)
        assert next_stage is not None
        assert next_stage["stage"] == 2


class TestOrchestratorInitialization:
    """Test orchestrator initialization."""
    
    def test_sync_orchestrator_init(self):
        """Test initializing synchronous orchestrator."""
        from orchestrator_sync import SyncOrchestrator, OrchestratorConfig
        
        config = OrchestratorConfig()
        orchestrator = SyncOrchestrator(config)
        
        assert orchestrator is not None
        assert orchestrator.config is not None
    
    def test_sync_orchestrator_default_config(self):
        """Test sync orchestrator with default config."""
        from orchestrator_sync import SyncOrchestrator
        
        orchestrator = SyncOrchestrator()
        assert orchestrator is not None


class TestDocumentation:
    """Test that all documentation files exist."""
    
    def test_orchestrator_guide_exists(self):
        """Test ORCHESTRATOR_GUIDE.md exists."""
        guide_file = Path("ORCHESTRATOR_GUIDE.md")
        assert guide_file.exists(), "ORCHESTRATOR_GUIDE.md not found"
    
    def test_orchestrator_quickstart_exists(self):
        """Test ORCHESTRATOR_QUICKSTART.md exists."""
        quickstart_file = Path("ORCHESTRATOR_QUICKSTART.md")
        assert quickstart_file.exists(), "ORCHESTRATOR_QUICKSTART.md not found"
    
    def test_orchestrator_readme_exists(self):
        """Test ORCHESTRATOR_README.md exists."""
        readme_file = Path("ORCHESTRATOR_README.md")
        assert readme_file.exists(), "ORCHESTRATOR_README.md not found"
    
    def test_orchestrator_requirements_exists(self):
        """Test orchestrator_requirements.txt exists."""
        req_file = Path("orchestrator_requirements.txt")
        assert req_file.exists(), "orchestrator_requirements.txt not found"


class TestValidation:
    """Test validation functions."""
    
    def test_valid_applicant_info(self):
        """Test valid applicant information."""
        from orchestrator_sync import ApplicantInfo
        
        # Should not raise
        applicant = ApplicantInfo(
            name="John Doe",
            email="john@example.com",
            phone="+91-9876543210",
            date_of_birth="1990-01-01",
            address="123 Main St",
            city="Bangalore",
            state="Karnataka",
            pincode="560001",
            employment_status="salaried",
            annual_income=800000,
            current_employer="TechCorp",
            designation="Engineer",
            years_at_current_employer=5
        )
        
        assert applicant is not None
    
    def test_invalid_missing_required_field(self):
        """Test validation of missing required field."""
        from orchestrator_sync import ApplicantInfo
        
        with pytest.raises(TypeError):
            ApplicantInfo(
                name="John Doe"
                # Missing required fields
            )


# Mock tests for health checks (without running actual services)
class TestMockHealthCheck:
    """Test mock health check responses."""
    
    def test_health_check_response_format(self):
        """Test health check response format."""
        health_response = {
            "intake": True,
            "kyc": True,
            "credit": True,
            "payslip": True,
            "bank": True,
            "face": True
        }
        
        assert isinstance(health_response, dict)
        assert all(isinstance(v, bool) for v in health_response.values())
        assert len(health_response) == 6


# Run tests with: pytest test_orchestrator.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
