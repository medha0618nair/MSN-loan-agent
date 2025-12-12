"""
LangChain Tool wrapper for Intake Agent.
Allows orchestrator to call intake agent as a LangChain tool.
"""
from langchain.tools import tool
from typing import Dict, Any
import requests
import json
import logging

logger = logging.getLogger(__name__)

INTAKE_SERVICE_URL = "http://localhost:8001"


@tool("intake_converse")
def intake_converse_tool(input_data: str) -> str:
    """
    Conversational intake agent tool for loan application.
    
    Args:
        input_data: JSON string with keys: application_id, conversation_id, user_message
        
    Returns:
        JSON string with structured response including slots, actions, and assistant reply
    """
    try:
        data = json.loads(input_data)
        
        response = requests.post(
            f"{INTAKE_SERVICE_URL}/chat/converse",
            json={
                "application_id": data["application_id"],
                "conversation_id": data["conversation_id"],
                "user_message": data["user_message"],
                "context": data.get("context", {})
            },
            timeout=30
        )
        
        response.raise_for_status()
        return json.dumps(response.json())
        
    except Exception as e:
        logger.error(f"Intake converse tool error: {e}")
        return json.dumps({"error": str(e)})


@tool("intake_update_slot")
def intake_update_slot_tool(input_data: str) -> str:
    """
    Update a specific slot in the intake agent.
    
    Args:
        input_data: JSON string with keys: application_id, conversation_id, slot_name, slot_value
        
    Returns:
        JSON string with updated slots and actions
    """
    try:
        data = json.loads(input_data)
        
        response = requests.post(
            f"{INTAKE_SERVICE_URL}/chat/slot",
            json={
                "application_id": data["application_id"],
                "conversation_id": data["conversation_id"],
                "slot_name": data["slot_name"],
                "slot_value": data["slot_value"]
            },
            timeout=30
        )
        
        response.raise_for_status()
        return json.dumps(response.json())
        
    except Exception as e:
        logger.error(f"Intake slot update tool error: {e}")
        return json.dumps({"error": str(e)})


@tool("intake_submit")
def intake_submit_tool(input_data: str) -> str:
    """
    Submit the completed intake application.
    
    Args:
        input_data: JSON string with keys: application_id, conversation_id
        
    Returns:
        JSON string with submission status and next steps
    """
    try:
        data = json.loads(input_data)
        
        response = requests.post(
            f"{INTAKE_SERVICE_URL}/chat/submit",
            json={
                "application_id": data["application_id"],
                "conversation_id": data["conversation_id"]
            },
            timeout=30
        )
        
        response.raise_for_status()
        return json.dumps(response.json())
        
    except Exception as e:
        logger.error(f"Intake submit tool error: {e}")
        return json.dumps({"error": str(e)})


@tool("intake_upload")
def intake_upload_tool(input_data: str) -> str:
    """
    Register an uploaded document and trigger KYC parsing.
    Args: JSON string with keys: application_id, conversation_id, doc_type, file_path, evidence_id (optional)
    """
    try:
        data = json.loads(input_data)

        response = requests.post(
            f"{INTAKE_SERVICE_URL}/chat/upload",
            json={
                "application_id": data["application_id"],
                "conversation_id": data["conversation_id"],
                "doc_type": data["doc_type"],
                "file_path": data["file_path"],
                "evidence_id": data.get("evidence_id"),
            },
            timeout=60,
        )

        response.raise_for_status()
        return json.dumps(response.json())

    except Exception as e:
        logger.error(f"Intake upload tool error: {e}")
        return json.dumps({"error": str(e)})


# Export tools list for orchestrator
INTAKE_TOOLS = [
    intake_converse_tool,
    intake_update_slot_tool,
    intake_submit_tool,
    intake_upload_tool
]
