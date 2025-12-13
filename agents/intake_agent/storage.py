"""
Storage module for persisting conversation state
Uses JSON files or Redis for state management
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

class ConversationStorage:
    """Manages persistence of conversation state"""
    
    def __init__(self, storage_dir: str = "./data/conversations"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_filepath(self, application_id: str) -> str:
        """Get filepath for an application's conversation data"""
        return os.path.join(self.storage_dir, f"{application_id}.json")
    
    def save_conversation_state(self, application_id: str, state: Dict[str, Any]) -> bool:
        """Save conversation state to storage"""
        try:
            filepath = self._get_filepath(application_id)
            state["last_updated"] = datetime.utcnow().isoformat()
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving conversation state: {e}")
            return False
    
    def load_conversation_state(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation state from storage"""
        try:
            filepath = self._get_filepath(application_id)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading conversation state: {e}")
            return None
    
    def initialize_conversation(self, application_id: str, conversation_id: str) -> Dict[str, Any]:
        """Initialize a new conversation"""
        state = {
            "application_id": application_id,
            "conversation_id": conversation_id,
            "created_at": datetime.utcnow().isoformat(),
            "current_question_id": "loan_type",
            "collected_slots": {},
            "completed": False,
            "messages": []
        }
        
        self.save_conversation_state(application_id, state)
        return state
    
    def update_collected_slots(self, application_id: str, field_name: str, value: Any) -> bool:
        """Update a collected slot and save state"""
        state = self.load_conversation_state(application_id)
        
        if not state:
            return False
        
        state["collected_slots"][field_name] = value
        state["last_updated"] = datetime.utcnow().isoformat()
        
        return self.save_conversation_state(application_id, state)
    
    def set_current_question(self, application_id: str, question_id: str) -> bool:
        """Set the current question ID"""
        state = self.load_conversation_state(application_id)
        
        if not state:
            return False
        
        state["current_question_id"] = question_id
        state["last_updated"] = datetime.utcnow().isoformat()
        
        return self.save_conversation_state(application_id, state)
    
    def mark_completed(self, application_id: str) -> bool:
        """Mark conversation as completed"""
        state = self.load_conversation_state(application_id)
        
        if not state:
            return False
        
        state["completed"] = True
        state["completed_at"] = datetime.utcnow().isoformat()
        state["last_updated"] = datetime.utcnow().isoformat()
        
        return self.save_conversation_state(application_id, state)
    
    def add_message(self, application_id: str, role: str, content: str) -> bool:
        """Add a message to conversation history"""
        state = self.load_conversation_state(application_id)
        
        if not state:
            return False
        
        state["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        state["last_updated"] = datetime.utcnow().isoformat()
        
        return self.save_conversation_state(application_id, state)
    
    def get_collected_slots(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get all collected slots"""
        state = self.load_conversation_state(application_id)
        
        if not state:
            return None
        
        return state.get("collected_slots", {})
