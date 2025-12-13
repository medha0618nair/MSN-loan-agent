#!/usr/bin/env python3
"""
Test Bank Agent with Real Bank Statement CSV
"""

import json
import requests
import pandas as pd
import base64

# Bank agent URL
BANK_AGENT_URL = "http://localhost:8003"

# Read CSV file
csv_path = "/Users/apple/Desktop/codered final/MSN-loan-agent/bank-statement/bank_transactions_ACC1001.csv"
df = pd.read_csv(csv_path)

print("="*70)
print("TESTING BANK AGENT WITH REAL BANK STATEMENT")
print("="*70)

print(f"\n📊 Input Data:")
print(f"  CSV File: {csv_path}")
print(f"  Total Rows: {len(df)}")
print(f"  Columns: {', '.join(df.columns.tolist())}")
print(f"  Date Range: {df['date'].min()} to {df['date'].max()}")

# Prepare request
print(f"\n📤 Sending request to Bank Agent (port 8003)...")

request_payload = {
    "application_id": "APP-TEST-BANK-001",
    "evidence_id": "BANK-STATEMENT-001",
    "file_uri": csv_path,  # Correct field name
}

try:
    # Try direct CSV file path endpoint
    response = requests.post(
        f"{BANK_AGENT_URL}/bank/parse",
        json=request_payload,
        timeout=30
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n✅ BANK STATEMENT ANALYSIS RESULTS:")
        print("="*70)
        
        # Display key results
        if "salary_info" in result:
            print(f"\n💰 SALARY INFORMATION:")
            salary = result["salary_info"]
            print(f"  Detected Salary: ₹{salary.get('avg_salary', 'N/A'):,}")
            print(f"  Frequency: {salary.get('frequency', 'N/A')}")
            print(f"  Consistency: {salary.get('consistency_score', 'N/A')}%")
            print(f"  Transactions: {salary.get('num_transactions', 'N/A')}")
        
        if "income_metrics" in result:
            print(f"\n📈 INCOME METRICS:")
            income = result["income_metrics"]
            print(f"  Total Income: ₹{income.get('total_income', 'N/A'):,}")
            print(f"  Monthly Average: ₹{income.get('monthly_avg_income', 'N/A'):,}")
        
        if "expense_metrics" in result:
            print(f"\n💸 EXPENSE METRICS:")
            expense = result["expense_metrics"]
            print(f"  Total Expenses: ₹{expense.get('total_expenses', 'N/A'):,}")
            print(f"  Monthly Average: ₹{expense.get('monthly_avg_expense', 'N/A'):,}")
        
        if "credit_score_details" in result:
            print(f"\n⭐ CREDIT SCORE:")
            score = result["credit_score_details"]
            print(f"  Overall Score: {score.get('overall_score', 'N/A')}")
            print(f"  Salary Consistency: {score.get('salary_consistency', 'N/A')}")
            print(f"  Payment Behavior: {score.get('payment_behavior', 'N/A')}")
            print(f"  Financial Health: {score.get('financial_health', 'N/A')}")
        
        if "risk_assessment" in result:
            print(f"\n⚠️ RISK ASSESSMENT:")
            risk = result["risk_assessment"]
            print(f"  Risk Level: {risk.get('risk_level', 'N/A')}")
            print(f"  Recommendation: {risk.get('recommendation', 'N/A')}")
        
        if "recommendation" in result:
            print(f"\n📋 RECOMMENDATION:")
            print(f"  {result['recommendation']}")
        
        print("\n" + "="*70)
        print("✅ Bank Agent Successfully Processed Statement")
        print("="*70)
    
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n❌ Bank Agent not responding on port 8004")
    print("Please start the bank agent first with: cd agents/bank-agent && python3 main.py")
except Exception as e:
    print(f"\n❌ Error: {e}")
