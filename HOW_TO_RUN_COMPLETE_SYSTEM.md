# 🚀 START THE COMPLETE SYSTEM (All Services Running)

## One Command to Start Everything

```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
bash START_ALL_SERVICES.sh
```

**This will start:**
- ✅ Intake Agent (8001)
- ✅ Orchestrator (9000)
- ✅ KYC Agent (8002)
- ✅ Face Agent (8003)
- ✅ Payslip Agent (8004)
- ✅ Bank Agent (8005)
- ✅ Credit Agent (8006)

**All services run permanently in the background** and will be available for your RAG agentic model.

---

## Verify Services Are Running

```bash
curl http://localhost:9000/agents/status
```

Expected output:
```json
{
  "intake": "RUNNING",
  "kyc": "RUNNING",
  "face": "RUNNING",
  "payslip": "RUNNING",
  "bank": "RUNNING",
  "credit": "RUNNING",
  "orchestrator": "RUNNING"
}
```

---

## Submit an Application

**In a new terminal:**
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
python3 submit_application_v2.py
```

Then answer all 17 questions. The system will automatically:
1. Validate each answer
2. Save to database
3. Submit to orchestrator
4. Call all agents
5. Return decision

---

## Stop All Services

```bash
bash STOP_SYSTEM.sh
```

---

## Monitor Logs

```bash
# Watch intake agent
tail -f logs/intake.log

# Watch orchestrator
tail -f logs/orchestrator.log

# Watch other agents
tail -f logs/kyc.log
tail -f logs/face.log
tail -f logs/payslip.log
tail -f logs/bank.log
tail -f logs/credit.log
```

---

## Architecture

```
All services running permanently on background:

Intake (8001) ←→ Orchestrator (9000) ←→ KYC (8002)
                                     ←→ Face (8003)
                                     ←→ Payslip (8004)
                                     ←→ Bank (8005)
                                     ←→ Credit (8006)

RAG Agentic Model can call any endpoint anytime
```

---

## For Your RAG Agentic Model

All endpoints available:

**Intake Agent:**
- POST http://localhost:8001/start
- POST http://localhost:8001/message
- GET http://localhost:8001/state/{app_id}

**Orchestrator:**
- POST http://localhost:9000/orchestrate
- GET http://localhost:9000/status/{job_id}
- GET http://localhost:9000/agents/status

**All agents on their respective ports (8002-8006)**

---

## Quick Start

```bash
# Terminal 1: Start all services
bash START_ALL_SERVICES.sh

# Terminal 2: Test with submission
python3 submit_application_v2.py

# Terminal 3: Monitor
tail -f logs/intake.log
```

**That's it! All services running 24/7!** ✅
