#!/usr/bin/env python3
"""
Submit Loan Application to Orchestrator
This sends your application to the orchestrator which runs ALL 6 agents
"""

import requests
import json
from datetime import datetime

ORCHESTRATOR_URL = "http://localhost:8000"

def submit_application():
    """Submit application through orchestrator"""
    
    print("\n" + "="*80)
    print("🏦 LOAN APPLICATION - ORCHESTRATOR SYSTEM")
    print("="*80 + "\n")
    
    # Get user input
    print("📝 Enter Your Information:\n")
    
    name = input("1. Full Name: ").strip() or "John Doe"
    email = input("2. Email: ").strip() or "john@example.com"
    phone = input("3. Phone: ").strip() or "+91-9876543210"
    
    print()
    
    employer = input("4. Current Employer: ").strip() or "Tech Corp"
    designation = input("5. Job Designation: ").strip() or "Engineer"
    
    try:
        years = float(input("6. Years at Current Job: ") or 3)
    except ValueError:
        years = 3
    
    try:
        annual_income = float(input("7. Annual Income (₹): ") or 5000000)
    except ValueError:
        annual_income = 5000000
    
    print()
    
    try:
        loan_amount = float(input("8. Loan Amount Needed (₹): ") or 500000)
    except ValueError:
        loan_amount = 500000
    
    try:
        tenure_months = int(input("9. Loan Duration (months): ") or 60)
    except ValueError:
        tenure_months = 60
    
    # Optional documents
    print("\n📄 Documents (optional - enter file path or press Enter to skip):\n")
    
    aadhaar_path = input("Aadhaar PDF path (or skip): ").strip() or None
    pan_path = input("PAN PDF path (or skip): ").strip() or None
    payslip_path = input("Payslip PDF path (or skip): ").strip() or None
    bank_statement_path = input("Bank Statement PDF path (or skip): ").strip() or None
    
    print("\n" + "="*80)
    print("⏳ SUBMITTING TO ORCHESTRATOR...")
    print("="*80 + "\n")
    
    # Prepare request
    payload = {
        "application_id": f"APP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "applicant_info": {
            "name": name,
            "email": email,
            "phone": phone,
            "employment_status": "salaried",
            "annual_income": annual_income,
            "current_employer": employer,
            "designation": designation,
            "years_at_current_employer": years,
            "loan_amount_requested": loan_amount,
            "loan_tenure_months": tenure_months
        },
        "documents": {
            "aadhaar": aadhaar_path,
            "pan": pan_path,
            "payslip": payslip_path,
            "bank_statement": bank_statement_path
        }
    }
    
    print(f"📤 Application ID: {payload['application_id']}")
    print(f"👤 Applicant: {name}")
    print(f"💼 Income: ₹{annual_income:,.0f}/year")
    print(f"💰 Loan Requested: ₹{loan_amount:,.0f}")
    print(f"⏱️  Duration: {tenure_months} months\n")
    
    try:
        # Send to orchestrator
        response = requests.post(
            f"{ORCHESTRATOR_URL}/process-application",
            json=payload,
            timeout=300  # 5 minute timeout for processing all agents
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "="*80)
            print("✅ DECISION RESULT")
            print("="*80 + "\n")
            
            print(f"Status: {result.get('final_status', 'N/A')}")
            print(f"Credit Score: {result.get('credit_score', 'N/A')}")
            print(f"Risk Level: {result.get('risk_level', 'N/A')}")
            print(f"Reason: {result.get('reason', 'N/A')}\n")
            
            if result.get('final_status') == 'APPROVED':
                print("✅ LOAN APPROVED!")
                print(f"   Approved Amount: ₹{result.get('approved_amount', 0):,.0f}")
                print(f"   Interest Rate: {result.get('interest_rate', 0):.2f}%")
                print(f"   Monthly EMI: ₹{result.get('monthly_emi', 0):,.0f}")
                print(f"   Total Repayment: ₹{result.get('total_repayment', 0):,.0f}\n")
            else:
                print(f"⚠️  Status: {result.get('final_status', 'N/A')}\n")
            
            # Show evidence trail
            print("📊 Evidence Trail:")
            print("-" * 80)
            evidence = result.get('evidence_trail', {})
            for stage, data in evidence.items():
                if isinstance(data, dict):
                    print(f"\n{stage.upper()}:")
                    for key, value in data.items():
                        if isinstance(value, (dict, list)):
                            print(f"  {key}: {json.dumps(value, indent=4)[:100]}...")
                        else:
                            print(f"  {key}: {value}")
            
            print("\n" + "="*80)
            print(f"Processed at: {result.get('processed_at', 'N/A')}")
            print("="*80 + "\n")
            
            # Save result
            result_file = f"application_{payload['application_id']}.json"
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"💾 Result saved to: {result_file}\n")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Details: {response.text}\n")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to orchestrator on http://localhost:8000")
        print("\n📌 Make sure you've run: bash RUN_ALL_AGENTS.sh\n")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out - agents took too long to process")
    except Exception as e:
        print(f"❌ ERROR: {e}\n")


if __name__ == "__main__":
    try:
        submit_application()
    except KeyboardInterrupt:
        print("\n\n⚠️  Application cancelled by user\n")
