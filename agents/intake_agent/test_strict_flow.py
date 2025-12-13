#!/usr/bin/env python3
"""
Test Client for Intake Agent - Strict Conversational Flow
Demonstrates the sequential question-answer interaction
"""

import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8001"

def test_strict_conversation_flow():
    """Test the strict conversational flow"""
    
    application_id = f"APP-{uuid4().hex[:8]}"
    print(f"\n{'='*70}")
    print(f"🎯 TESTING STRICT CONVERSATIONAL FLOW")
    print(f"Application ID: {application_id}")
    print(f"{'='*70}\n")
    
    # Step 1: Start conversation
    print("1️⃣  Starting conversation...\n")
    start_response = requests.post(
        f"{BASE_URL}/start",
        json={"application_id": application_id}
    ).json()
    
    print(f"Bot: {start_response['bot_message']}")
    print(f"Current Question ID: {start_response['next_question_id']}\n")
    
    # Step 2: Answer questions in sequence
    conversation_data = [
        ("personal", "loan_type"),
        ("John Doe", "full_name"),
        ("1990-05-15", "date_of_birth"),
        ("9876543210", "phone"),
        ("john.doe@example.com", "email"),
        ("ABCDE1234F", "pan"),
        ("salaried", "employment_type"),
        ("TechCorp Inc", "employer_name"),
        ("Senior Developer", "designation"),
        ("5", "years_at_job"),
        ("75000", "monthly_income"),
        ("500000", "loan_amount"),
        ("60", "tenure_months"),
    ]
    
    for user_input, expected_field in conversation_data:
        print(f"2️⃣  Sending answer: {user_input}")
        
        response = requests.post(
            f"{BASE_URL}/message",
            json={
                "application_id": application_id,
                "user_message": user_input
            }
        ).json()
        
        print(f"Bot: {response['bot_message']}")
        print(f"Collected: {response['collected_slots']}")
        print(f"Completed: {response['completed']}\n")
        
        if response['completed']:
            print(f"✅ Application complete!")
            break
    
    # Step 3: Get final state
    print("\n3️⃣  Getting final conversation state...\n")
    final_state = requests.get(f"{BASE_URL}/state/{application_id}").json()
    
    print("FINAL COLLECTED DATA:")
    print(json.dumps(final_state['collected_slots'], indent=2))
    
    print(f"\nTotal messages: {len(final_state['messages'])}")
    print(f"Completed: {final_state['completed']}")
    print(f"\n{'='*70}")

def test_validation_failures():
    """Test that validation failures don't skip questions"""
    
    application_id = f"APP-INVALID-{uuid4().hex[:8]}"
    print(f"\n{'='*70}")
    print(f"🔴 TESTING VALIDATION FAILURES")
    print(f"Application ID: {application_id}")
    print(f"{'='*70}\n")
    
    # Start conversation
    response = requests.post(
        f"{BASE_URL}/start",
        json={"application_id": application_id}
    ).json()
    
    print(f"Bot: {response['bot_message']}\n")
    
    # Try invalid loan type
    print("Sending invalid loan type: 'xyz'")
    response = requests.post(
        f"{BASE_URL}/message",
        json={
            "application_id": application_id,
            "user_message": "xyz"
        }
    ).json()
    
    print(f"Bot: {response['bot_message']}")
    print(f"Next Question ID (should still be loan_type): {response['next_question_id']}")
    print(f"Completed: {response['completed']}\n")
    
    # Now send valid loan type
    print("Sending valid loan type: 'personal'")
    response = requests.post(
        f"{BASE_URL}/message",
        json={
            "application_id": application_id,
            "user_message": "personal"
        }
    ).json()
    
    print(f"Bot: {response['bot_message']}")
    print(f"Next Question ID (should be full_name): {response['next_question_id']}")
    print(f"Collected: {response['collected_slots']}\n")

if __name__ == "__main__":
    print("\n🚀 INTAKE AGENT - STRICT FLOW TEST CLIENT\n")
    
    try:
        # Test main flow
        test_strict_conversation_flow()
        
        # Test validation
        test_validation_failures()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\nMake sure the intake agent is running:")
        print(f"  python3 main_strict_flow.py")
