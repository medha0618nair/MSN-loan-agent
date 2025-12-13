#!/usr/bin/env python3
"""
Conversational Intake Agent - True Chat Experience
Makes the interaction feel natural and engaging
"""

import requests
import json
from datetime import datetime

INTAKE_URL = "http://localhost:8001"

# Conversational responses
BOT_RESPONSES = {
    "welcome": [
        "Hey there! 👋 Welcome to our loan application process.",
        "I'm here to help you with your loan application.",
        "Don't worry, this will be quick and easy!",
        "Let me ask you a few questions to get started."
    ],
    "great": [
        "Great! ✅",
        "Perfect! 👍",
        "Got it! 📝",
        "Nice! 😊",
        "Thanks for that!"
    ],
    "next": [
        "Moving on...",
        "Next question...",
        "Alright, here's the next one...",
        "Got it, let me ask you this..."
    ],
    "end": [
        "Awesome! We're almost done.",
        "Just a few more questions...",
        "You're doing great! Final stretch.",
        "Almost there!"
    ]
}

def print_bot_message(message: str):
    """Print bot message with formatting"""
    print(f"\n🤖 Agent: {message}\n")

def print_user_prompt(stage: int, total: int):
    """Show progress"""
    progress = f"[{stage}/{total}]"
    print(f"👤 You {progress}: ", end="")

def start_conversation():
    """Start the conversation"""
    try:
        response = requests.post(f"{INTAKE_URL}/start", json={})
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return None
        return response.json()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Intake Agent on http://localhost:8001")
        print("Make sure services are running: the agents should be started first")
        return None

def send_message(app_id: str, message: str):
    """Send user message"""
    try:
        response = requests.post(
            f"{INTAKE_URL}/message",
            json={"application_id": app_id, "user_message": message}
        )
        if response.status_code != 200:
            return None
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("\n" + "="*70)
    print("💬 CONVERSATIONAL LOAN APPLICATION")
    print("="*70 + "\n")
    
    # Start conversation
    print_bot_message("Hey there! 👋 Welcome to our loan application process. I'm here to help you with your loan. This should be quick and easy!")
    print("(Starting conversation with agent...)\n")
    
    response = start_conversation()
    if not response:
        return
    
    app_id = response["application_id"]
    print(f"✅ Application ID: {app_id}\n")
    
    question_count = 0
    total_questions = 17
    
    # Main conversation loop
    while True:
        # Get bot message
        bot_msg = response.get('bot_message', '')
        
        # Extract just the question part
        if "What" in bot_msg or "Please" in bot_msg:
            # It's a question
            question_count += 1
            
            # Add conversational filler
            if question_count > 1 and question_count < 14:
                print(f"{BOT_RESPONSES['next'][question_count % len(BOT_RESPONSES['next'])]}")
            elif question_count >= 14:
                print(BOT_RESPONSES['end'][question_count % len(BOT_RESPONSES['end'])])
            
            print_bot_message(bot_msg)
        else:
            print_bot_message(bot_msg)
        
        # Check if completed
        if response.get("completed"):
            print("\n" + "="*70)
            print("✅ APPLICATION COMPLETE!")
            print("="*70 + "\n")
            print_bot_message("Awesome! 🎉 Your application is complete. Let me submit this for processing...")
            
            # Show summary
            if response.get("collected_data"):
                print("\n📋 APPLICATION SUMMARY")
                print("-" * 70)
                data = response["collected_data"]
                print(f"  👤 Name: {data.get('full_name')}")
                print(f"  📧 Email: {data.get('email')}")
                print(f"  💼 Employment: {data.get('employment_type')}")
                print(f"  💰 Monthly Income: ₹{data.get('monthly_income', 0):,.0f}")
                print(f"  🏦 Loan Amount: ₹{data.get('loan_amount', 0):,.0f}")
                print(f"  ⏱️  Duration: {data.get('tenure_months')} months")
                print("-" * 70)
            
            print_bot_message("Your application has been saved! ✅ Thank you for using our service!")
            break
        
        # Get user input
        print_user_prompt(question_count, total_questions)
        user_input = input().strip()
        
        if not user_input:
            print("Please enter a response.\n")
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n❌ Application cancelled.\n")
            break
        
        # Send message
        response = send_message(app_id, user_input)
        
        if not response:
            print("❌ Error sending message\n")
            break
        
        # Show feedback on answer
        if "❌" in response.get('bot_message', ''):
            print("\n⚠️  That didn't work, let me ask again...")
        else:
            random_idx = (question_count) % len(BOT_RESPONSES['great'])
            print(f"\n{BOT_RESPONSES['great'][random_idx]}")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Application cancelled by user\n")
