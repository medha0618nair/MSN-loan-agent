#!/usr/bin/env python3
"""
Test Credit Agent with Real Data from All Agents
Shows how credit scoring uses intake, KYC, bank, and payslip data
"""

import json
import requests
from datetime import datetime

print("="*80)
print("CREDIT AGENT - COMPREHENSIVE TEST WITH REAL DATA")
print("="*80)

# Real data from bank agent (already tested)
BANK_DATA = {
    "avg_salary": int(41851.72),  # Convert to integer
    "median_salary": int(41851.72),  # Convert to integer
    "months_salary_detected": 2,
    "payroll_consistency": 0.8178,
    "salary_share_of_credits": 0.2351,
    "confidence": 0.8644,
    "bank_salary_detected": True
}

# Simulated payslip data (would come from payslip OCR agent)
PAYSLIP_DATA = {
    "net_pay_payslip": 35000,
    "gross_pay_payslip": 42000,
    "monthly_income": 35000,
    "income_confidence": 0.95,
    "employment_status": "salaried"
}

# Simulated KYC data (from document OCR)
KYC_DATA = {
    "pan_number": "DIJPN7537R",
    "name_extracted": "NITHIN J",
    "kyc_confidence": 0.95,
    "doc_type": "PAN"
}

# Simulated face verification data
FACE_DATA = {
    "face_verified": True,
    "match_confidence": 0.98,
    "liveness_score": 0.97
}

# Intake data (from user input)
INTAKE_DATA = {
    "applicant_name": "Nithin J",
    "email": "nithin.j@email.com",
    "phone": "9876543210",
    "loan_amount": 3000000,
    "loan_purpose": "home",
    "pan": "DIJPN7537R"
}

# Loan request
LOAN_REQUEST = {
    "loan_amount": 3000000,
    "tenure_months": 60,
    "monthly_emi_estimate": 50000
}

# Calculate credit score request
credit_request = {
    "application_id": "APP-CREDIT-TEST-001",
    "evidence": {
        "intake": INTAKE_DATA,
        "kyc": KYC_DATA,
        "face": FACE_DATA,
        "payslip": PAYSLIP_DATA,
        "bank": BANK_DATA,
        "fraud": {
            "fraud_score": 0.05,
            "reasons": [],
            "suspicious_keywords": []
        }
    },
    "loan_request": LOAN_REQUEST,
    "app_metadata": {
        "submission_ts": datetime.utcnow().isoformat(),
        "source": "web"
    }
}

print("\n📤 SENDING TO CREDIT AGENT (Port 8006)...")
print(f"   Application ID: {credit_request['application_id']}")
print(f"   Loan Amount: ₹{LOAN_REQUEST['loan_amount']:,}")
print(f"   Tenure: {LOAN_REQUEST['tenure_months']} months")
print(f"   Monthly EMI: ₹{LOAN_REQUEST['monthly_emi_estimate']:,.0f}")

try:
    response = requests.post(
        "http://localhost:8006/score",
        json=credit_request,
        timeout=30
    )
    
    print(f"\n✅ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "="*80)
        print("CREDIT SCORING RESULTS")
        print("="*80)
        
        # Application info
        print(f"\n📋 APPLICATION:")
        print(f"   ID: {result.get('application_id')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Timestamp: {result.get('ts')}")
        
        # Credit Decision
        print(f"\n⭐ CREDIT DECISION:")
        print(f"   Decision: {result.get('decision')}")
        print(f"   Risk Tier: {result.get('risk_tier')}")
        print(f"   PD Score: {result.get('pd_score'):.4f}" if 'pd_score' in result else "   PD Score: N/A")
        
        # Income Analysis
        if 'income_analysis' in result:
            inc = result['income_analysis']
            print(f"\n💰 INCOME ANALYSIS:")
            print(f"   Monthly Income: ₹{inc.get('monthly_income', 'N/A'):,}" if isinstance(inc.get('monthly_income'), int) else f"   Monthly Income: {inc.get('monthly_income', 'N/A')}")
            print(f"   Income Source: {inc.get('income_source', 'N/A')}")
            print(f"   Income Confidence: {inc.get('income_confidence', 'N/A')}")
        
        # Debt Analysis
        if 'debt_analysis' in result:
            debt = result['debt_analysis']
            print(f"\n📊 DEBT ANALYSIS:")
            print(f"   Monthly EMI: ₹{debt.get('monthly_emi', 'N/A'):,.0f}" if isinstance(debt.get('monthly_emi'), int) else f"   Monthly EMI: {debt.get('monthly_emi', 'N/A')}")
            print(f"   DTI Ratio: {debt.get('dti_ratio', 'N/A'):.2%}" if isinstance(debt.get('dti_ratio'), float) else f"   DTI Ratio: {debt.get('dti_ratio', 'N/A')}")
            print(f"   Loan to Income: {debt.get('loan_to_income', 'N/A'):.2f}x" if isinstance(debt.get('loan_to_income'), float) else f"   Loan to Income: {debt.get('loan_to_income', 'N/A')}")
        
        # Identity Verification
        if 'identity_verification' in result:
            identity = result['identity_verification']
            print(f"\n🆔 IDENTITY VERIFICATION:")
            print(f"   Face Match: {identity.get('face_verified', 'N/A')}")
            print(f"   Face Confidence: {identity.get('face_confidence', 'N/A')}")
            print(f"   KYC Confidence: {identity.get('kyc_confidence', 'N/A')}")
            print(f"   Overall: {identity.get('identity_status', 'N/A')}")
        
        # Employment Verification
        if 'employment_verification' in result:
            emp = result['employment_verification']
            print(f"\n💼 EMPLOYMENT VERIFICATION:")
            print(f"   Status: {emp.get('employment_status', 'N/A')}")
            print(f"   Salary Consistency: {emp.get('payroll_consistency', 'N/A'):.1%}" if isinstance(emp.get('payroll_consistency'), float) else f"   Salary Consistency: {emp.get('payroll_consistency', 'N/A')}")
            print(f"   Months Detected: {emp.get('months_salary_detected', 'N/A')}")
        
        # Recommendation
        print(f"\n📝 RECOMMENDATION:")
        if 'recommendation' in result:
            print(f"   {result['recommendation']}")
        
        # Reason
        if 'reason' in result:
            print(f"\n✍️ REASON:")
            print(f"   {result['reason']}")
        
        print("\n" + "="*80)
        print("✅ CREDIT AGENT SUCCESSFULLY SCORED APPLICATION")
        print("="*80)
    
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n❌ Credit Agent not responding on port 8006")
    print("Please ensure credit agent is running: cd agents/credit-agent && python3 main.py")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
