"""
Intake Agent - Storage Layer v2
Persist conversation state to database
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

class ConversationStorageV2:
    """Manages conversation state persistence"""
    
    def __init__(self, db_dir: str = "./data/conversations"):
        self.db_dir = db_dir
        os.makedirs(db_dir, exist_ok=True)
    
    def get_filepath(self, application_id: str) -> str:
        """Get filepath for application"""
        return os.path.join(self.db_dir, f"{application_id}.json")
    
    def initialize_conversation(self, application_id: str) -> Dict[str, Any]:
        """Start new conversation"""
        state = {
            "application_id": application_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "current_stage": "loan_type",
            "collected_data": {},
            "messages": [],
            "completed": False
        }
        self.save_conversation(application_id, state)
        return state
    
    def load_conversation(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation from disk"""
        filepath = self.get_filepath(application_id)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def save_conversation(self, application_id: str, state: Dict[str, Any]) -> None:
        """Save conversation to disk"""
        filepath = self.get_filepath(application_id)
        state["last_updated"] = datetime.utcnow().isoformat()
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def update_stage(self, application_id: str, stage: str) -> None:
        """Update current stage"""
        state = self.load_conversation(application_id)
        if state:
            state["current_stage"] = stage
            self.save_conversation(application_id, state)
    
    def add_answer(self, application_id: str, field_name: str, value: Any) -> None:
        """Add user answer to collected data"""
        state = self.load_conversation(application_id)
        if state:
            state["collected_data"][field_name] = value
            self.save_conversation(application_id, state)
    
    def add_message(self, application_id: str, role: str, content: str) -> None:
        """Add message to conversation history"""
        state = self.load_conversation(application_id)
        if state:
            state["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.save_conversation(application_id, state)
    
    def mark_completed(self, application_id: str) -> None:
        """Mark conversation as completed"""
        state = self.load_conversation(application_id)
        if state:
            state["completed"] = True
            state["completed_at"] = datetime.utcnow().isoformat()
            self.save_conversation(application_id, state)
    
    def get_collected_data(self, application_id: str) -> Dict[str, Any]:
        """Get all collected data"""
        state = self.load_conversation(application_id)
        return state.get("collected_data", {}) if state else {}
    
    def get_current_stage(self, application_id: str) -> Optional[str]:
        """Get current stage"""
        state = self.load_conversation(application_id)
        return state.get("current_stage") if state else None
