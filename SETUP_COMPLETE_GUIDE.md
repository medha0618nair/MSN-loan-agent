# Complete Setup Guide - End-to-End Loan Processing

## What's the Status?

**Current:** You have orchestrator code ready but agents aren't running.
**Need:** Start all 6 agents + the API server to accept real user data.

---

## 🚀 QUICK START (5 Minutes)

### Step 1: Install All Dependencies

```bash
cd "/Users/apple/Desktop/coredited final/MSN-loan-agent"

# Install orchestrator dependencies
pip install -r orchestrator_requirements.txt

# Install each agent's dependencies
pip install -r agents/intake_agent/requirements.txt
pip install -r agents/kyc_agent/requirements.txt
pip install -r agents/face-agent/requirements.txt
pip install -r agents/payslip-agent/requirements.txt
pip install -r agents/bank-agent/requirements.txt
pip install -r agents/credit-agent/requirements.txt

# Install FastAPI for API server
pip install fastapi uvicorn
```

### Step 2: Set Up Environment Variables

Create or update `.env` file in repo root:

```bash
# .env
GROQ_API_KEY=your-groq-api-key-here
ORCHESTRATOR_PORT=8000

# Agent Configuration
INTAKE_AGENT_PORT=8001
KYC_AGENT_PORT=8002
FACE_AGENT_PORT=8003
PAYSLIP_AGENT_PORT=8004
BANK_AGENT_PORT=8005
CREDIT_AGENT_PORT=8006

# Optional
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Step 3: Start Redis (Required)

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

Or if you have it locally:
```bash
redis-server
```

### Step 4: Start All 6 Agents (Open 6 terminal windows)

**Terminal 1 - Intake Agent (Port 8001):**
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/intake_agent"
python main.py
```

**Terminal 2 - KYC Agent (Port 8002):**
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/kyc_agent"
python main.py
```

**Terminal 3 - Face Agent (Port 8003):**
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/face-agent"
python main.py
```

**Terminal 4 - Payslip Agent (Port 8004):**
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/payslip-agent"
python main.py
```

**Terminal 5 - Bank Agent (Port 8005):**
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/bank-agent"
python main.py
```

**Terminal 6 - Credit Agent (Port 8006):**
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/credit-agent"
python main.py
```

### Step 5: Start API Server (Terminal 7)

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
python run_orchestrator_server.py
```

✅ Server will be available at: **http://localhost:8000**

---

## 📝 How to Use (Submit Real User Data)

### Option A: Interactive API Docs

Go to: **http://localhost:8000/docs**
- Click "Try it out" on `/process-application`
- Fill in applicant details
- Click "Execute"

### Option B: Using curl

```bash
curl -X POST "http://localhost:8000/process-application" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_info": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+91-9123456789",
      "employment_status": "salaried",
      "annual_income": 1500000,
      "current_employer": "Tech Company",
      "designation": "Senior Developer",
      "years_at_current_employer": 5,
      "loan_amount_requested": 1000000,
      "loan_tenure_months": 60
    },
    "documents": {
      "aadhaar": "/path/to/aadhaar.pdf",
      "payslip": "/path/to/payslip.pdf",
      "bank_statement": "/path/to/bank_statement.pdf"
    }
  }'
```

### Option C: Using Python

```python
import requests
import json

url = "http://localhost:8000/process-application"

payload = {
    "applicant_info": {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "+91-9987654321",
        "annual_income": 2000000,
        "current_employer": "FinTech Corp",
        "designation": "Product Manager",
        "years_at_current_employer": 4,
        "loan_amount_requested": 750000,
        "loan_tenure_months": 60
    },
    "documents": {
        "aadhaar": "/path/to/aadhaar.pdf",
        "payslip": "/path/to/payslip.pdf",
        "bank_statement": "/path/to/bank_statement.pdf"
    }
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
```

---

## ✅ Expected Response

```json
{
  "application_id": "APP-20231215120000",
  "final_status": "APPROVED",
  "credit_score": 780,
  "risk_level": "Low",
  "approved_amount": 800000,
  "interest_rate": 8.25,
  "monthly_emi": 15853,
  "tenure_months": 60,
  "total_repayment": 990180,
  "reason": "Approved with favorable terms",
  "evidence_trail": {
    "intake": { ... },
    "kyc": { ... },
    "face": { ... },
    "payslip": { ... },
    "bank": { ... },
    "credit": { ... }
  },
  "processed_at": "2023-12-15T12:00:00.000000"
}
```

---

## 🔍 Check System Status

### Check all agents are running:
```bash
curl http://localhost:8000/agents/health
```

### Check orchestrator health:
```bash
curl http://localhost:8000/health
```

### Run demo test:
```bash
curl -X POST http://localhost:8000/demo
```

---

## ⚠️ Troubleshooting

**Problem: "Agent not reachable on port XXXX"**
- Check that all 6 agents are running
- Verify ports: 8001-8006 are not blocked

**Problem: "GROQ_API_KEY is missing"**
- Add your GROQ API key to `.env` file
- Agents need this to process with LLM

**Problem: "Redis connection refused"**
- Start Redis: `docker run -d -p 6379:6379 redis:7-alpine`
- Intake agent requires Redis for memory

**Problem: "ModuleNotFoundError"**
- Ensure you installed all requirements
- Run: `pip install -r orchestrator_requirements.txt`

---

## 📊 Data Flow (What Happens When User Submits)

```
1. User submits data to /process-application
   ↓
2. API receives applicant info + documents
   ↓
3. Orchestrator starts processing (6 agents in sequence):
   ✓ Intake Agent - Collects & validates info
   ✓ KYC Agent - Verifies identity documents
   ✓ Face Agent - Checks face liveness & identity match
   ✓ Payslip Agent - Extracts income from payslip
   ✓ Bank Agent - Analyzes bank statements
   ✓ Credit Agent - Calculates credit score & makes decision
   ↓
4. Final decision generated with complete evidence
   ↓
5. Response sent to user: APPROVED/REJECTED/MANUAL_REVIEW
```

---

## 📄 API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API documentation |
| `/health` | GET | Check orchestrator & agents health |
| `/process-application` | POST | **MAIN** - Submit loan application |
| `/application-status/{app_id}` | GET | Check application status |
| `/agents/health` | GET | Individual agent health |
| `/demo` | POST | Test with demo data |

---

## Next Steps

1. ✅ Install dependencies (orchestrator + agents)
2. ✅ Set up `.env` with GROQ API key
3. ✅ Start Redis
4. ✅ Start all 6 agents
5. ✅ Start API server
6. ✅ Submit user data via API

**Then it will work!** The system is ready to accept real user input.
