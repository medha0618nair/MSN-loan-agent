# 🚀 RUN FULL SYSTEM - All 6 Real Agents Orchestrated

## Prerequisites

- macOS/Linux
- Python 3.11+ available as `python3` or `python3.11`
- Groq API key configured in `.env`

## ONE-TIME SETUP

Run this once to install all dependencies:

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
bash SETUP_ALL_AGENTS.sh
```

This will:
- ✅ Create virtual environment for each of the 6 agents
- ✅ Create virtual environment for orchestrator
- ✅ Install all dependencies (Pillow, mediapipe, opencv, etc.)
- ✅ Fix Python 3.13 compatibility issues

**Time**: ~5-10 minutes (first time only)

---

## START ALL AGENTS

Open terminal and run:

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
bash RUN_ALL_AGENTS.sh
```

This will start (in order):
1. ✅ **Intake Agent** (port 8001) - Collects applicant info with strict sequential flow
2. ✅ **KYC Agent** (port 8002) - Verifies identity documents
3. ✅ **Face Agent** (port 8003) - Runs face verification & liveness
4. ✅ **Payslip Agent** (port 8004) - Verifies salary slip & income
5. ✅ **Bank Agent** (port 8005) - Analyzes bank statements
6. ✅ **Credit Agent** (port 8006) - Final credit decision & scoring
7. ✅ **Orchestrator API** (port 8000) - Coordinates all agents

You should see:
```
================================================
✅ ALL AGENTS STARTED
================================================

Agent Status:
  🟢 INTAKE AGENT  - http://localhost:8001
  🟢 KYC AGENT     - http://localhost:8002
  🟢 FACE AGENT    - http://localhost:8003
  🟢 PAYSLIP AGENT - http://localhost:8004
  🟢 BANK AGENT    - http://localhost:8005
  🟢 CREDIT AGENT  - http://localhost:8006

================================================
✅ ORCHESTRATOR STARTED
================================================

🟢 ORCHESTRATOR API - http://localhost:8000
```

---

## SUBMIT LOAN APPLICATION

### **Option 1: Interactive CLI (Easiest)**

Open **NEW terminal** and run:

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/intake_agent"
python3 -c "
import requests
import json

# Start conversation with intake agent
resp = requests.post('http://localhost:8001/start', json={'application_id': 'APP-REAL-001'})
print(json.dumps(resp.json(), indent=2))

# It will ask for loan type
# Send answer
resp = requests.post('http://localhost:8001/message', json={
    'application_id': 'APP-REAL-001',
    'user_message': 'personal'
})
print(json.dumps(resp.json(), indent=2))
# ... continue for each question
"
```

### **Option 2: HTTP API with cURL**

```bash
curl -X POST http://localhost:8000/process-application \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_info": {
      "name": "Rahul Kumar",
      "email": "rahul@example.com",
      "phone": "+91-9876543210",
      "employment_status": "salaried",
      "annual_income": 4500000,
      "current_employer": "TechCorp India",
      "designation": "Senior Manager",
      "years_at_current_employer": 5,
      "loan_amount_requested": 500000,
      "loan_tenure_months": 60
    },
    "documents": {
      "aadhaar": "/path/to/aadhaar.pdf",
      "pan": "/path/to/pan.pdf",
      "payslip": "/path/to/payslip.pdf",
      "bank_statement": "/path/to/bank_statement.pdf"
    }
  }'
```

### **Option 3: Swagger UI**

Open browser: **http://localhost:8000/docs**

Click on `/process-application` and submit form directly.

---

## EXECUTION FLOW

When you submit an application, the orchestrator will:

```
1️⃣ INTAKE AGENT (Port 8001)
   └─ Collects all required information:
      • Loan type (personal/home/auto/education)
      • Full name, DOB, phone, email, PAN
      • Employment type, employer, designation, years
      • Monthly income, loan amount, tenure
      • Optional: Documents (Aadhaar, PAN, payslip, etc.)

2️⃣ KYC AGENT (Port 8002)
   └─ Processes documents:
      • OCR parsing of identity documents
      • Face detection in submitted photos
      • Data extraction & validation

3️⃣ FACE AGENT (Port 8003)
   └─ Verifies identity:
      • Face liveness detection
      • Matches face with ID document
      • Anti-spoofing checks

4️⃣ PAYSLIP AGENT (Port 8004)
   └─ Verifies income:
      • Extracts salary information
      • Validates income claims
      • Detects payslip authenticity

5️⃣ BANK AGENT (Port 8005)
   └─ Analyzes finances:
      • Parses bank statements
      • Checks transaction history
      • Calculates account health score

6️⃣ CREDIT AGENT (Port 8006)
   └─ Makes final decision:
      • Combines evidence from all agents
      • Calculates credit score (300-900)
      • Returns: APPROVED / REJECTED / MANUAL_REVIEW
      • Calculates EMI, interest rate, total repayment
```

---

## SAMPLE RESPONSE

```json
{
  "application_id": "APP-REAL-001",
  "final_status": "APPROVED",
  "credit_score": 742,
  "risk_level": "LOW",
  "approved_amount": 500000,
  "interest_rate": 8.5,
  "monthly_emi": 10247,
  "tenure_months": 60,
  "total_repayment": 614820,
  "reason": "Applicant meets all requirements with strong financial profile",
  "evidence_trail": {
    "intake": { "collected_data": {...} },
    "kyc": { "verification_status": "VERIFIED", "documents": {...} },
    "face": { "liveness": "PASSED", "match_score": 0.98 },
    "payslip": { "verified_income": 375000, "confidence": 0.95 },
    "bank": { "account_health": 0.87, "transaction_analysis": {...} },
    "credit": { "score": 742, "risk_factors": [...] }
  },
  "processed_at": "2025-12-13T10:30:45Z"
}
```

---

## MONITOR AGENTS

### Watch all logs in real-time:

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
tail -f logs_*.log
```

### Check individual agent logs:

```bash
# Intake agent
tail -f logs_INTAKE_AGENT.log

# KYC agent
tail -f logs_KYC_AGENT.log

# Orchestrator
tail -f logs_orchestrator.log
```

---

## STOP ALL AGENTS

### Kill all at once:

```bash
pkill -f "python.*main.py"
```

### Or individually:

```bash
kill $(cat INTAKE_AGENT.pid KYC_AGENT.pid FACE_AGENT.pid PAYSLIP_AGENT.pid BANK_AGENT.pid CREDIT_AGENT.pid ORCHESTRATOR.pid)
```

---

## TROUBLESHOOTING

### **Issue: "Module not found" error**

```bash
# Reinstall dependencies
bash SETUP_ALL_AGENTS.sh
```

### **Issue: Port already in use**

```bash
# Find process using port 8001
lsof -i :8001

# Kill it
kill -9 <PID>
```

### **Issue: Agents not responding**

```bash
# Check if agents are running
curl -I http://localhost:8001/health
curl -I http://localhost:8002/health
curl -I http://localhost:8000/health

# Check logs
tail -f logs_*.log
```

---

## WHAT'S DIFFERENT NOW?

| Before | After |
|--------|-------|
| ❌ No real agents | ✅ All 6 real agents |
| ❌ Simulated decisions | ✅ Real document parsing & ML |
| ❌ Skipped questions | ✅ Strict sequential intake flow |
| ❌ No persistence | ✅ State saved, can resume |
| ❌ Not orchestrated | ✅ Full orchestration with evidence trail |

---

## NEXT STEPS

1. Run setup: `bash SETUP_ALL_AGENTS.sh`
2. Start agents: `bash RUN_ALL_AGENTS.sh`
3. Submit application via API/Swagger
4. Monitor logs: `tail -f logs_*.log`
5. View results with complete evidence trail

**You now have a fully functional, real multi-agent loan orchestration system! 🎉**
