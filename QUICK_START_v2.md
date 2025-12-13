# Quick Reference - System v2

## 🎯 One-Liner Start

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent" && bash START_SYSTEM_V2.sh
```

## 🧪 In Another Terminal

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent" && python3 submit_application_v2.py
```

---

## 📡 Ports

| Service | Port | Purpose |
|---------|------|---------|
| Intake Agent | 8001 | Conversational Q&A |
| KYC Agent | 8002 | Document verification |
| Face Agent | 8003 | Face verification |
| Payslip Agent | 8004 | Income verification |
| Bank Agent | 8005 | Financial analysis |
| Credit Agent | 8006 | Final decision |
| **Orchestrator** | **9000** | Multi-agent coordination |

---

## 🔌 Key Endpoints

### Intake Agent (8001)
```
POST /start                 → Start conversation
POST /message              → Send answer
GET /state/{app_id}        → Get state
GET /health                → Health check
```

### Orchestrator (9000)
```
POST /orchestrate          → Process application
GET /status/{job_id}       → Get job status
GET /agents/status         → All agents status
GET /health                → Health check
```

---

## 📝 Conversation Flow

```
Question 1:  What type of loan? → personal/home/auto/education
Question 2:  Full name? → John Doe
Question 3:  Date of birth? → YYYY-MM-DD
Question 4:  Phone? → 10 digits
Question 5:  Email? → valid@email.com
Question 6:  PAN? → AAAAA9999A
Question 7:  Employment? → salaried/self-employed/student
Question 8:  Employer? (if salaried)
Question 9:  Designation? (if salaried)
Question 10: Years at job? (if salaried)
Question 11: Monthly income? → number
Question 12: Loan amount? → number
Question 13: Tenure? → months
Question 14: KYC file? (REQUIRED) → file path
Question 15: Selfie? (REQUIRED) → file path
Question 16: Payslip? (if salaried) → file path
Question 17: Bank statement? (optional) → file path
```

---

## 🔍 Monitoring

### Watch Logs
```bash
tail -f logs/intake.log
tail -f logs/orchestrator.log
```

### Check Health
```bash
curl http://localhost:9000/agents/status
```

### View Results
```bash
cat audit/JOB-*.json
```

---

## 🐛 Troubleshooting

### Port in use?
```bash
lsof -ti:9000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
```

### Agent not responding?
```bash
curl http://localhost:8001/health
curl http://localhost:9000/health
```

### Missing dependencies?
```bash
pip install fastapi uvicorn pydantic httpx requests
```

---

## 📊 Architecture in 3 Steps

1. **INTAKE** (8001) - Asks 17 questions, saves state
2. **AUTO-SUBMIT** - Sends to orchestrator when done
3. **ORCHESTRATOR** (9000) - Calls all agents, merges, returns decision

---

## ✅ Success Indicators

- ✅ All 6 agents show "RUNNING" in `/agents/status`
- ✅ Intake asks questions one by one (no skipping)
- ✅ Answers are validated (invalid ones re-asked)
- ✅ After last question, auto-submits to orchestrator
- ✅ Job ID returned with status
- ✅ Audit JSON file created in `./audit/`

---

## 🚀 Files to Remember

| File | Purpose |
|------|---------|
| `START_SYSTEM_V2.sh` | Start all services |
| `submit_application_v2.py` | Client app |
| `agents/intake_agent/main_v2.py` | Intake server |
| `orchestrator_agent/main_v2.py` | Orchestrator server |
| `orchestrator_agent/config_v2.py` | Configuration |
| `SYSTEM_v2_README.md` | Full documentation |

---

## 📞 Testing Workflow

```bash
# Terminal 1: Start services
bash START_SYSTEM_V2.sh

# Terminal 2: Check health
curl http://localhost:9000/agents/status

# Terminal 3: Submit application
python3 submit_application_v2.py

# Answer all 17 questions
# ↓
# Auto-submits to orchestrator
# ↓
# Returns job_id
# ↓
# Check results
curl http://localhost:9000/status/JOB-ABC123...
```

---

## 💡 System Flow Summary

```
User Input
    ↓
Intake Agent (8001)
  - Question 1-13: Personal info
  - Question 14-17: File uploads
  - Validate each answer
  - Save to DB
    ↓
Auto-Submit to Orchestrator (9000)
    ↓
Orchestrator Calls Parallel Agents:
  ├─ KYC (8002)
  ├─ Face (8003)
  ├─ Payslip (8004)
  └─ Bank (8005)
    ↓
Merge Results
    ↓
Call Credit Agent (8006)
    ↓
Save Audit JSON
    ↓
Return Decision
```

---

**Ready to go! Start with:** `bash START_SYSTEM_V2.sh`
