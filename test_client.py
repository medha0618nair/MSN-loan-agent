#!/usr/bin/env python3
"""
Test Client - Send real user data to orchestrator API
Usage: python test_client.py
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health():
    """Check if orchestrator is healthy"""
    print("\n" + "="*60)
    print("🔍 CHECKING ORCHESTRATOR HEALTH")
    print("="*60 + "\n")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the orchestrator server is running!")
        return False

def test_agents():
    """Check individual agent health"""
    print("\n" + "="*60)
    print("🔍 CHECKING AGENT HEALTH")
    print("="*60 + "\n")
    
    try:
        response = requests.get(f"{BASE_URL}/agents/health", timeout=5)
        agents = response.json()
        
        for agent, status in agents.items():
            status_icon = "✅" if status["healthy"] else "❌"
            print(f"{status_icon} {agent:20s} Port {status['port']}: {'Healthy' if status['healthy'] else 'Down'}")
        
        return all(status["healthy"] for status in agents.values())
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_demo():
    """Run demo test"""
    print("\n" + "="*60)
    print("🎬 RUNNING DEMO TEST")
    print("="*60 + "\n")
    
    try:
        response = requests.post(f"{BASE_URL}/demo", timeout=300)
        result = response.json()
        
        print(f"📋 Application ID: {result['application_id']}")
        print(f"🎯 Decision: {result['final_status']}")
        print(f"💳 Credit Score: {result['credit_score']}")
        print(f"⚠️  Risk Level: {result['risk_level']}")
        
        if result.get('approved_amount'):
            print(f"💰 Approved Amount: ₹{result['approved_amount']:,.0f}")
            print(f"📊 Interest Rate: {result['interest_rate']}%")
            print(f"💵 Monthly EMI: ₹{result['monthly_emi']:,.0f}")
            print(f"⏱️  Tenure: {result['tenure_months']} months")
        
        print(f"\n📝 Reason: {result['reason']}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_real_application():
    """Submit a real application"""
    print("\n" + "="*60)
    print("📋 SUBMITTING REAL APPLICATION")
    print("="*60 + "\n")
    
    applicant_data = {
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@email.com",
        "phone": "+91-9876543210",
        "employment_status": "salaried",
        "annual_income": 1500000,
        "current_employer": "Tech Solutions Ltd",
        "designation": "Senior Software Engineer",
        "years_at_current_employer": 5,
        "loan_amount_requested": 1000000,
        "loan_tenure_months": 60
    }
    
    documents_data = {
        "aadhaar": "/path/to/aadhaar.pdf",
        "pan": "/path/to/pan.pdf",
        "payslip": "/path/to/payslip.pdf",
        "bank_statement": "/path/to/bank_statement.pdf",
        "selfie": "/path/to/selfie.jpg"
    }
    
    payload = {
        "applicant_info": applicant_data,
        "documents": documents_data
    }
    
    print(f"👤 Applicant: {applicant_data['name']}")
    print(f"💼 Employer: {applicant_data['current_employer']}")
    print(f"💰 Annual Income: ₹{applicant_data['annual_income']:,}")
    print(f"🏦 Loan Request: ₹{applicant_data['loan_amount_requested']:,}")
    print("\nSubmitting application...\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/process-application",
            json=payload,
            timeout=300
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        
        print("="*60)
        print("✅ APPLICATION PROCESSED")
        print("="*60 + "\n")
        
        print(f"📋 Application ID: {result['application_id']}")
        print(f"🎯 Decision: {result['final_status']}")
        print(f"💳 Credit Score: {result['credit_score']}")
        print(f"⚠️  Risk Level: {result['risk_level']}\n")
        
        if result.get('approved_amount'):
            print("💰 LOAN APPROVED")
            print(f"  • Approved Amount: ₹{result['approved_amount']:,.0f}")
            print(f"  • Interest Rate: {result['interest_rate']}%")
            print(f"  • Monthly EMI: ₹{result['monthly_emi']:,.0f}")
            print(f"  • Tenure: {result['tenure_months']} months")
            print(f"  • Total Repayment: ₹{result['total_repayment']:,.0f}")
        else:
            print("❌ LOAN REJECTED")
        
        print(f"\n📝 Reason: {result['reason']}")
        
        # Show evidence trail
        print("\n" + "="*60)
        print("📊 EVIDENCE TRAIL")
        print("="*60 + "\n")
        
        evidence = result.get('evidence_trail', {})
        for stage, data in evidence.items():
            print(f"\n{stage.upper()}:")
            print(json.dumps(data, indent=2))
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 ORCHESTRATOR API CLIENT")
    print("="*60)
    
    # Test health
    if not test_health():
        print("\n❌ Orchestrator server is not running!")
        print("Start it with: python run_orchestrator_server.py")
        return
    
    # Test agents
    if not test_agents():
        print("\n⚠️  Some agents are not running!")
        print("Make sure all 6 agents are started on ports 8001-8006")
        print("Or run: python start_all.py")
        return
    
    # Run demo
    if test_demo():
        print("\n✅ Demo test passed!")
    
    # Run real application
    if test_real_application():
        print("\n✅ Real application test passed!")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
