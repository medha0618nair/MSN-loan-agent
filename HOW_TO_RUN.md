# 🚀 HOW TO RUN - Simple Step by Step

## 📋 ONE-TIME SETUP

Open Terminal and run:

```bash
bash "/Users/apple/Desktop/codered final/MSN-loan-agent/STEP_1_INSTALL.sh"
```

Wait for: `✅ All dependencies installed`

---

## 🎯 START EVERYTHING (Need 8 Terminal Windows)

### Terminal 1: Start Redis
```bash
bash "/Users/apple/Desktop/codered final/MSN-loan-agent/STEP_2_REDIS.sh"
```
Should show: `✅ Redis started`

---

### Terminal 2: Start Intake Agent
```bash
bash "/Users/apple/Desktop/codered final/MSN-loan-agent/STEP_3_INTAKE.sh"
```
Wait for: `INFO:     Uvicorn running on http://0.0.0.0:8001`

---

### Terminal 3: Start KYC Agent
```bash
bash "/Users/apple/Desktop/codered final/MSN-loan-agent/STEP_4_KYC.sh"
```
Wait for: `INFO:     Uvicorn running on http://0.0.0.0:8002`

---

### Terminal 4: Start Face Agent
```bash
bash "/Users/apple/Desktop/codered final/MSN-loan-agent/STEP_5_FACE.sh"
```
Wait for: `INFO:     Uvicorn running on http://0.0.0.0:8003`

---

### Terminal 5: Start Payslip Agent
```bash
bash "/Users/apple/Desktop/codered final/MSN-loan-agent/STEP_6_PAYSLIP.sh"
```
Wait for: `INFO:     Uvicorn running on http://0.0.0.0:8004`

---

### Terminal 6: Start Bank Agent
```bash
bash "/Users/apple/Desktop/codered final/MSN-loan-agent/STEP_7_BANK.sh"
```
Wait for: `INFO:     Uvicorn running on http://0.0.0.0:8005`

---

### Terminal 7: Start Credit Agent
```bash
bash "/Users/apple/Desktop/codered final/MSN-loan-agent/STEP_8_CREDIT.sh"
```
Wait for: `INFO:     Uvicorn running on http://0.0.0.0:8006`

---

### Terminal 8: Start API Server
```bash
bash "/Users/apple/Desktop/codered final/MSN-loan-agent/STEP_9_API_SERVER.sh"
```
Wait for: `📖 Docs available at http://localhost:8000/docs`

---

## ✅ Verify All Running

In a new Terminal, run:
```bash
curl http://localhost:8000/health
```

Should show all agents healthy (true):
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

## 📝 SUBMIT USER DATA

### Option 1: Web Interface (Easiest)
Open browser → http://localhost:8000/docs
- Click `/process-application`
- Click "Try it out"
- Fill in details (name, email, phone, income, etc.)
- Click "Execute"
- Get decision!

### Option 2: Using curl
```bash
curl -X POST "http://localhost:8000/process-application" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_info": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+91-9123456789",
      "annual_income": 1500000,
      "current_employer": "Tech Company",
      "designation": "Manager",
      "years_at_current_employer": 3,
      "loan_amount_requested": 1000000,
      "loan_tenure_months": 60
    }
  }'
```

### Option 3: Using Python
```python
import requests

data = {
    "applicant_info": {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "+91-9876543210",
        "annual_income": 2000000,
        "current_employer": "FinTech Corp",
        "designation": "Senior Manager",
        "years_at_current_employer": 5,
        "loan_amount_requested": 1500000,
        "loan_tenure_months": 60
    }
}

response = requests.post("http://localhost:8000/process-application", json=data)
print(response.json())
```

---

## 📊 YOU'LL GET BACK

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
  "evidence_trail": { ... }
}
```

---

## 🛑 TO STOP EVERYTHING

In each Terminal, press: `Ctrl + C`

Or kill by port:
```bash
lsof -ti:8000,8001,8002,8003,8004,8005,8006,6379 | xargs kill -9
```

---

## 📞 QUICK COMMANDS

| Command | What it does |
|---------|-------------|
| `curl http://localhost:8000/health` | Check if everything works |
| `curl http://localhost:8000/demo` | Run demo test |
| `curl http://localhost:8000/agents/health` | Check each agent |
| http://localhost:8000/docs | Interactive API docs |

---

## ⚠️ Common Issues

| Error | Fix |
|-------|-----|
| "Port 8001 already in use" | `lsof -ti:8001 \| xargs kill -9` |
| "Redis connection refused" | Make sure Terminal 1 (Redis) is running |
| "ModuleNotFoundError" | Run STEP_1_INSTALL.sh again |
| "GROQ_API_KEY not found" | Check `.env` file has API key |

---

## 📋 Summary

1. **ONCE:** Run `STEP_1_INSTALL.sh`
2. **THEN:** Run STEP_2 through STEP_9 (each in own terminal)
3. **VERIFY:** `curl http://localhost:8000/health`
4. **USE:** Submit data to http://localhost:8000/docs

**That's it!**
