# ✅ Quick Checklist - Manual Setup (Option B)

## Status: ✅ API Key Configured

Your GROQ API key has been set in `.env`

---

## Follow These Steps:

### Phase 1: Setup (Do Once)
- [ ] Step 1: Install all dependencies (pip install...)
- [ ] Step 2: Start Redis (docker run...)

### Phase 2: Start All Services (8 Terminals)
- [ ] Terminal 1: Start Redis
- [ ] Terminal 2: Start Intake Agent (:8001)
- [ ] Terminal 3: Start KYC Agent (:8002)
- [ ] Terminal 4: Start Face Agent (:8003)
- [ ] Terminal 5: Start Payslip Agent (:8004)
- [ ] Terminal 6: Start Bank Agent (:8005)
- [ ] Terminal 7: Start Credit Agent (:8006)
- [ ] Terminal 8: Start API Server (:8000)

### Phase 3: Test & Use
- [ ] Verify all running: `curl http://localhost:8000/health`
- [ ] Submit user data via API
- [ ] Get loan decision

---

## 📍 Current Status

✅ `.env` created with your GROQ API key
✅ `run_orchestrator_server.py` ready (API server)
✅ All 6 agents available
✅ Redis needed

---

## Start Here

Open the detailed guide:
```
MANUAL_SETUP_OPTION_B.md
```

Or jump to specific steps:
- **Step 1**: Install dependencies
- **Step 2**: Start Redis
- **Steps 3-9**: Start each service

---

## Quick Command: Install Everything

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
pip install -r orchestrator_requirements.txt
pip install fastapi uvicorn
for agent in agents/*/; do pip install -r "$agent/requirements.txt"; done
```

---

## Once Running

Access at:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Demo**: http://localhost:8000/demo (POST)

Submit data to:
- **POST** http://localhost:8000/process-application

---

**Ready to start?** Open MANUAL_SETUP_OPTION_B.md
