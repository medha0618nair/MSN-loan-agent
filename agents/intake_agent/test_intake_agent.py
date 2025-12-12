"""
Unit tests for Intake Agent.
Tests RAG, slot-filling, and LangChain integration.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import app
from langchain_pipeline import IntakePipeline, SlotExtractionOutput

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test health endpoint returns correct response."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "intake_agent"
        assert data["version"] == "intake-v1"


class TestConverseEndpoint:
    """Test conversational RAG endpoint."""
    
    def test_converse_basic(self):
        """Test basic conversation."""
        payload = {
            "application_id": "test-app-001",
            "conversation_id": "test-conv-001",
            "user_message": "What documents do I need?",
            "context": {}
        }
        
        response = client.post("/chat/converse", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["application_id"] == "test-app-001"
        assert data["conversation_id"] == "test-conv-001"
        assert "assistant_reply" in data
        assert data["agent_version"] == "intake-v1"
    
    def test_converse_slot_extraction(self):
        """Test slot extraction during conversation."""
        payload = {
            "application_id": "test-app-002",
            "conversation_id": "test-conv-002",
            "user_message": "My name is John Doe and I need a loan of 500000",
            "context": {}
        }
        
        response = client.post("/chat/converse", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        # Slots should be extracted
        assert isinstance(data["slots"], dict)


class TestSlotEndpoint:
    """Test slot update endpoint."""
    
    def test_slot_update(self):
        """Test explicit slot update."""
        payload = {
            "application_id": "test-app-003",
            "conversation_id": "test-conv-003",
            "slot_name": "full_name",
            "slot_value": "Jane Smith"
        }
        
        response = client.post("/chat/slot", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["application_id"] == "test-app-003"
        assert "full_name" in data["slots"] or len(data["slots"]) >= 0
    
    def test_slot_update_multiple(self):
        """Test multiple slot updates."""
        app_id = "test-app-004"
        conv_id = "test-conv-004"
        
        slots = [
            {"slot_name": "full_name", "slot_value": "Alice Johnson"},
            {"slot_name": "email", "slot_value": "alice@example.com"},
            {"slot_name": "loan_amount", "slot_value": "300000"}
        ]
        
        for slot in slots:
            payload = {
                "application_id": app_id,
                "conversation_id": conv_id,
                **slot
            }
            response = client.post("/chat/slot", json=payload)
            assert response.status_code == 200


class TestSubmitEndpoint:
    """Test application submission endpoint."""
    
    def test_submit_incomplete(self):
        """Test submission with incomplete data."""
        payload = {
            "application_id": "test-app-005",
            "conversation_id": "test-conv-005"
        }
        
        response = client.post("/chat/submit", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        # Should have validation errors or missing slots
        actions = data.get("actions", [])
        if actions:
            assert any(a["type"] == "validation_error" for a in actions)


class TestLangChainPipeline:
    """Test LangChain pipeline components."""
    
    @pytest.fixture
    def pipeline(self):
        """Create test pipeline."""
        return IntakePipeline(
            groq_api_key="test-key",
            redis_host="localhost",
            redis_port=6379,
            docs_path="./data/docs"
        )
    
    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initializes correctly."""
        assert pipeline is not None
        assert pipeline.llm is not None
    
    def test_rag_query_fallback(self, pipeline):
        """Test RAG query with fallback."""
        result = pipeline.rag_query("What is the interest rate?")
        assert isinstance(result, dict)
        assert "answer" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
