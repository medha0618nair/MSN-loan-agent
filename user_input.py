#!/usr/bin/env python3
"""
Simple User Input - Enter your loan details
Run: python3 user_input.py
"""

from datetime import datetime
import json

print("\n" + "="*70)
print("🏦 LOAN ORCHESTRATOR - USER INPUT")
print("="*70 + "\n")

# Get basic info
name = input("1. Your Full Name: ").strip() or "John Doe"
email = input("2. Your Email: ").strip() or "user@example.com"
phone = input("3. Your Phone: ").strip() or "+91-9876543210"

print()

# Get employment info
employer = input("4. Current Employer: ").strip() or "XYZ Corp"
designation = input("5. Your Designation: ").strip() or "Manager"
try:
    years = float(input("6. Years at Current Job: ") or 3)
except:
    years = 3
    
try:
    income = float(input("7. Annual Income (₹): ") or 1000000)
except:
    income = 1000000

print()

# Get loan details
try:
    loan_amt = float(input("8. Loan Amount Needed (₹): ") or 500000)
except:
    loan_amt = 500000
    
try:
    months = int(input("9. Loan Duration (months): ") or 60)
except:
    months = 60

print("\n" + "="*70)
print("⏳ PROCESSING YOUR APPLICATION...")
print("="*70 + "\n")

# Process
monthly_income = income / 12 if income > 0 else 83333
monthly_payment = loan_amt / months
dti = (monthly_payment / monthly_income) * 100

print(f"Monthly Income: ₹{monthly_income:,.0f}")
print(f"Monthly Payment: ₹{monthly_payment:,.0f}")
print(f"Debt-to-Income Ratio: {dti:.1f}%\n")

# Decision logic
if income == 0 or dti > 100:
    decision = "REJECTED"
    reason = "Insufficient income or excessive loan amount"
    score = 300
elif dti > 50:
    decision = "MANUAL_REVIEW"
    reason = "High debt-to-income ratio, requires manual review"
    score = 500
elif years < 1:
    decision = "MANUAL_REVIEW"
    reason = "Insufficient employment history"
    score = 550
else:
    decision = "APPROVED"
    reason = "Application approved based on credit profile"
    score = min(900, int(650 + (years * 10) - (dti / 2)))

# Calculate EMI if approved
if decision == "APPROVED":
    interest_rate = 7.5 if dti < 30 else 9.5
    monthly_rate = interest_rate / 100 / 12
    num_payments = months
    emi = (loan_amt * monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    total_int = (emi * months) - loan_amt
else:
    interest_rate = None
    emi = None
    total_int = None

# Display result
print("\n" + "="*70)
print("✅ DECISION RESULT")
print("="*70 + "\n")

print(f"Applicant: {name}")
print(f"Status: {decision}")
print(f"Credit Score: {score}")
print()

if decision == "APPROVED":
    print(f"✅ APPROVED FOR: ₹{loan_amt:,.0f}")
    print(f"   • Interest Rate: {interest_rate}%")
    print(f"   • Monthly EMI: ₹{emi:,.0f}")
    print(f"   • Tenure: {months} months")
    print(f"   • Total Interest: ₹{total_int:,.0f}")
    print(f"   • Total Repayment: ₹{loan_amt + total_int:,.0f}")
elif decision == "MANUAL_REVIEW":
    print(f"⚠️  MANUAL REVIEW NEEDED")
    print(f"   {reason}")
else:
    print(f"❌ REJECTED: {reason}")

print(f"\nReason: {reason}")
print("\n" + "="*70 + "\n")

# Save
app_id = f"APP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
result = {
    "application_id": app_id,
    "applicant_name": name,
    "status": decision,
    "credit_score": score,
    "loan_amount": loan_amt,
    "annual_income": income,
    "dti_ratio": dti,
    "reason": reason
}

if decision == "APPROVED":
    result.update({
        "approved_amount": loan_amt,
        "interest_rate": interest_rate,
        "monthly_emi": emi,
        "total_interest": total_int,
        "total_repayment": loan_amt + total_int
    })

filename = f"application_{app_id}.json"
with open(filename, 'w') as f:
    json.dump(result, f, indent=2)

print(f"💾 Saved to: {filename}\n")
