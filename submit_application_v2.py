#!/usr/bin/env python3
"""
Loan Application Client v2
Submit application through Intake Agent
Intake automatically sends to Orchestrator
"""

import sys
import requests
import json
from datetime import datetime

INTAKE_URL = "http://localhost:8001"

def start_conversation():
    """Start new conversation"""
    try:
        response = requests.post(f"{INTAKE_URL}/start", json={})
        if response.status_code != 200:
            print(f"❌ Error starting conversation: {response.status_code}")
            return None
        return response.json()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Intake Agent on http://localhost:8001")
        print("\n📌 Make sure you've run: bash START_SYSTEM_V2.sh\n")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def send_message(app_id: str, message: str):
    """Send user message"""
    try:
        response = requests.post(
            f"{INTAKE_URL}/message",
            json={"application_id": app_id, "user_message": message}
        )
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return None
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("\n" + "="*80)
    print("🏦 LOAN APPLICATION CLIENT v2")
    print("="*80 + "\n")
    
    # Start conversation
    print("📞 Starting conversation with Intake Agent...\n")
    response = start_conversation()
    
    if not response:
        return
    
    app_id = response["application_id"]
    print(f"✅ Application ID: {app_id}\n")
    
    # Conversation loop
    while True:
        print(f"Bot: {response['bot_message']}")
        
        if response.get("completed"):
            print("\n✅ Application processing complete!")
            if response.get("status") == "SUBMITTED":
                print("   Submitted to orchestrator for verification.")
            break
        
        print()
        user_input = input("You: ").strip()
        
        if not user_input:
            print("Please enter a response.\n")
            continue
        
        # Send message
        response = send_message(app_id, user_input)
        
        if not response:
            print("❌ Error sending message\n")
            break
        
        print()
    
    # Show summary
    print("\n" + "="*80)
    print("📊 APPLICATION SUMMARY")
    print("="*80 + "\n")
    
    if response and response.get("collected_data"):
        data = response["collected_data"]
        print(f"👤 Name: {data.get('full_name')}")
        print(f"📧 Email: {data.get('email')}")
        print(f"💼 Employment: {data.get('employment_type')}")
        print(f"💰 Income: ₹{data.get('monthly_income', 0):,.0f}/month")
        print(f"🏦 Loan Amount: ₹{data.get('loan_amount', 0):,.0f}")
        print(f"⏱️  Duration: {data.get('tenure_months')} months")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Application cancelled by user\n")

