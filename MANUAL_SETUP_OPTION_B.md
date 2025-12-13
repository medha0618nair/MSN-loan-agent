# Manual Setup - Step by Step (Option B)

## ✅ Your API Key is Set!

Your GROQ API key has been added to `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

---

## 📋 Step-by-Step Instructions

### STEP 1: Install All Dependencies

Run this command once to install everything:

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"

# Install main requirements
pip install -r orchestrator_requirements.txt

# Install FastAPI for API server
pip install fastapi uvicorn

# Install dependencies for each agent
pip install -r agents/intake_agent/requirements.txt
pip install -r agents/kyc_agent/requirements.txt
pip install -r agents/face-agent/requirements.txt
pip install -r agents/payslip-agent/requirements.txt
pip install -r agents/bank-agent/requirements.txt
pip install -r agents/credit-agent/requirements.txt
```

---

### STEP 2: Start Redis

**In Terminal 1, run:**

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

Wait for it to print a container ID (means it started successfully).

Check it's running:
```bash
docker ps | grep redis
```

Should show:
```
CONTAINER ID ... redis:7-alpine
```

---

### STEP 3: Start Intake Agent (Terminal 2)

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/intake_agent"
python main.py
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

✅ Intake Agent is running on Port 8001

---

### STEP 4: Start KYC Agent (Terminal 3)

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/kyc_agent"
python main.py
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8002
```

✅ KYC Agent is running on Port 8002

---

### STEP 5: Start Face Agent (Terminal 4)

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/face-agent"
python main.py
```

Wait for port 8003 message.

✅ Face Agent is running on Port 8003

---

### STEP 6: Start Payslip Agent (Terminal 5)

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/payslip-agent"
python main.py
```

Wait for port 8004 message.

✅ Payslip Agent is running on Port 8004

---

### STEP 7: Start Bank Agent (Terminal 6)

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/bank-agent"
python main.py
```

Wait for port 8005 message.

✅ Bank Agent is running on Port 8005

---

### STEP 8: Start Credit Agent (Terminal 7)

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/credit-agent"
python main.py
```

Wait for port 8006 message.

✅ Credit Agent is running on Port 8006

---

### STEP 9: Start API Server (Terminal 8)

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
python run_orchestrator_server.py
```

Wait for:
```
🚀 Starting Orchestrator API Server on port 8000
📖 Docs available at http://localhost:8000/docs
```

✅ **ALL SYSTEMS RUNNING!**

---

## ✅ Verify Everything is Running

In a new terminal, check health:

```bash
curl http://localhost:8000/health
```

Should show:
```json
{
  "status": "healthy",
  "orchestrator": "ready",
  "agents": {
    "intake": true,
    "kyc": true,
    "face": true,
    "payslip": true,
    "bank": true,
    "credit": true
  }
}
```

---

## 📋 Submit Real User Data

### Option A: Interactive API Docs (Easiest)

1. Open browser: **http://localhost:8000/docs**
2. Look for `/process-application` endpoint
3. Click "Try it out"
4. Fill in the form:
   - Name: `John Doe`
   - Email: `john@example.com`
   - Phone: `+91-9123456789`
   - Annual Income: `1500000`
   - Employer: `Tech Company`
   - Designation: `Manager`
   - Years: `3`
   - Loan Amount: `1000000`
   - Tenure: `60`
5. Click "Execute"
6. See the result!

### Option B: Using Python

```python
import requests

payload = {
    "applicant_info": {
        "name": "Rajesh Kumar",
        "email": "rajesh@example.com",
        "phone": "+91-9876543210",
        "employment_status": "salaried",
        "annual_income": 2000000,
        "current_employer": "Tech Solutions",
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
}

response = requests.post("http://localhost:8000/process-application", json=payload)
print(response.json())
```

### Option C: Using curl

```bash
curl -X POST "http://localhost:8000/process-application" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_info": {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "phone": "+91-9876543210",
      "annual_income": 1500000,
      "current_employer": "FinTech Corp",
      "designation": "Product Manager",
      "years_at_current_employer": 4,
      "loan_amount_requested": 750000,
      "loan_tenure_months": 60
    }
  }'
```

---

## 📊 Expected Response

```json
{
  "application_id": "APP-20231215143022",
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
  "processed_at": "2023-12-15T14:30:22.123456"
}
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Port 8001 already in use" | Kill process: `lsof -ti:8001 \| xargs kill -9` |
| "Redis connection refused" | Make sure Docker is running: `docker ps` |
| "ModuleNotFoundError" | Reinstall dependencies: `pip install -r orchestrator_requirements.txt` |
| "GROQ_API_KEY not found" | Check `.env` file has your API key |
| "Agent not reachable" | Verify agent is running: `curl http://localhost:8001/health` |

---

## 📋 Terminal Setup Overview

```
Terminal 1: redis-server
Terminal 2: intake_agent (:8001)
Terminal 3: kyc_agent (:8002)
Terminal 4: face_agent (:8003)
Terminal 5: payslip_agent (:8004)
Terminal 6: bank_agent (:8005)
Terminal 7: credit_agent (:8006)
Terminal 8: orchestrator_api (:8000) ← Send user data here
```

---

## ✨ What Happens

When you submit user data:
1. API receives the application
2. Orchestrator starts processing
3. Each agent processes in order (1→2→3→4→5→6)
4. Final decision generated with complete evidence
5. Response sent back to you: APPROVED/REJECTED/MANUAL_REVIEW

**Total time:** ~2-3 minutes per application

---

## 🎯 Next

1. Run Step 1 (install dependencies)
2. Run Step 2 (start Redis)
3. Run Steps 3-9 (start all agents and API)
4. Use any option to submit user data

**Let me know when you get stuck!**
