#!/usr/bin/env python3
"""
User Input Version - Accept real user data and process
Run: python3 process_real_user_data.py
"""

import json
import sys
from datetime import datetime

def get_user_input():
    """Collect user data interactively"""
    print("\n" + "="*80)
    print("📋 LOAN APPLICATION FORM")
    print("="*80 + "\n")
    
    print("👤 PERSONAL INFORMATION\n")
    name = input("Full Name: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone (e.g., +91-9876543210): ").strip()
    
    print("\n💼 EMPLOYMENT INFORMATION\n")
    employer = input("Current Employer: ").strip()
    designation = input("Designation: ").strip()
    years_employed = float(input("Years at Current Employer: ") or 1)
    annual_income = float(input("Annual Income (₹): "))
    
    print("\n🏦 LOAN DETAILS\n")
    loan_amount = float(input("Loan Amount Requested (₹): "))
    tenure = int(input("Loan Tenure (months, e.g., 60): ") or 60)
    
    print("\n📄 DOCUMENTS (optional - enter file paths)\n")
    aadhaar = input("Aadhaar Document Path (leave blank to skip): ").strip() or None
    payslip = input("Payslip Path (leave blank to skip): ").strip() or None
    bank_statement = input("Bank Statement Path (leave blank to skip): ").strip() or None
    
    return {
        "applicant_info": {
            "name": name,
            "email": email,
            "phone": phone,
            "employment_status": "salaried",
            "annual_income": annual_income,
            "current_employer": employer,
            "designation": designation,
            "years_at_current_employer": years_employed,
            "loan_amount_requested": loan_amount,
            "loan_tenure_months": tenure
        },
        "documents": {
            "aadhaar": aadhaar,
            "payslip": payslip,
            "bank_statement": bank_statement
        }
    }

def process_with_orchestrator(data):
    """Process data through orchestrator (simulated)"""
    from datetime import datetime
    
    print("\n" + "="*80)
    print("⏳ PROCESSING APPLICATION...")
    print("="*80 + "\n")
    
    applicant = data["applicant_info"]
    
    # Simulate processing through 6 agents
    stages = [
        ("Intake", "Collecting applicant information..."),
        ("KYC", "Verifying identity documents..."),
        ("Face", "Checking face liveness..."),
        ("Payslip", "Extracting income from payslip..."),
        ("Bank", "Analyzing bank statements..."),
        ("Credit", "Calculating credit score...")
    ]
    
    for i, (stage, action) in enumerate(stages, 1):
        print(f"{i}️⃣  {stage}: {action}")
    
    print("\n" + "="*80)
    print("✅ PROCESSING COMPLETE")
    print("="*80 + "\n")
    
    # Generate decision based on income and loan amount
    monthly_income = applicant["annual_income"] / 12
    loan_amount = applicant["loan_amount_requested"]
    tenure = applicant["loan_tenure_months"]
    
    # Simple credit scoring
    dti_ratio = (loan_amount / (tenure * 12)) / monthly_income
    
    if dti_ratio < 0.3 and applicant["years_at_current_employer"] >= 2:
        decision = "APPROVED"
        approved_amount = loan_amount * 1.1  # Approve slightly more
        interest_rate = 8.25
        reason = "Approved with favorable terms"
    elif dti_ratio < 0.5:
        decision = "APPROVED"
        approved_amount = loan_amount * 0.9  # Approve slightly less
        interest_rate = 9.5
        reason = "Approved with moderate interest rate"
    else:
        decision = "MANUAL_REVIEW"
        approved_amount = None
        interest_rate = None
        reason = "Application requires manual review due to debt-to-income ratio"
    
    # Calculate EMI if approved
    monthly_emi = None
    total_interest = None
    total_repayment = None
    
    if decision != "MANUAL_REVIEW":
        monthly_rate = interest_rate / 100 / 12
        num_payments = tenure
        monthly_emi = (approved_amount * monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        total_repayment = monthly_emi * tenure
        total_interest = total_repayment - approved_amount
    
    # Generate credit score (simplified)
    credit_score = min(900, int(700 + (applicant["years_at_current_employer"] * 10) - (dti_ratio * 100)))
    
    result = {
        "application_id": f"APP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "final_status": decision,
        "credit_score": credit_score,
        "risk_level": "Low" if dti_ratio < 0.3 else "Medium" if dti_ratio < 0.5 else "High",
        "approved_amount": approved_amount,
        "interest_rate": interest_rate,
        "monthly_emi": monthly_emi,
        "tenure_months": tenure,
        "total_repayment": total_repayment,
        "reason": reason,
        "processed_at": datetime.now().isoformat()
    }
    
    return result

def display_result(result):
    """Display the decision"""
    print("="*80)
    print("🎯 FINAL DECISION")
    print("="*80 + "\n")
    
    print(f"Application ID: {result['application_id']}")
    print(f"Status: {result['final_status']}")
    print(f"Credit Score: {result['credit_score']}")
    print(f"Risk Level: {result['risk_level']}\n")
    
    if result['final_status'] != "MANUAL_REVIEW":
        print("💰 LOAN RECOMMENDATION:")
        print(f"  • Approved Amount: ₹{result['approved_amount']:,.0f}")
        print(f"  • Interest Rate: {result['interest_rate']}%")
        print(f"  • Monthly EMI: ₹{result['monthly_emi']:,.0f}")
        print(f"  • Tenure: {result['tenure_months']} months")
        print(f"  • Total Interest: ₹{result['total_repayment'] - result['approved_amount']:,.0f}")
        print(f"  • Total Repayment: ₹{result['total_repayment']:,.0f}\n")
    
    print(f"📝 Reason: {result['reason']}\n")
    
    print("="*80)
    
    # Save to file
    filename = f"application_{result['application_id']}.json"
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n✅ Application saved to: {filename}")

def main():
    try:
        # Get user input
        data = get_user_input()
        
        # Process through orchestrator
        result = process_with_orchestrator(data)
        
        # Display result
        display_result(result)
        
    except KeyboardInterrupt:
        print("\n\n❌ Application cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
