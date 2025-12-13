# System v2 - Complete Integration Guide

## ✅ What Was Built

A complete multi-agent loan verification system with:

1. **Intake Agent (Port 8001)** - Strict conversational interface
2. **Orchestrator (Port 9000)** - Multi-agent coordinator  
3. **Health Check** - Monitor all 6 agents
4. **Full Pipeline** - Auto-triggered agent execution

---

## 🎯 Three Simple Commands

### Command 1: Start the System
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
bash START_SYSTEM_v2.sh
```

**Output:**
```
✅ Intake Agent started on port 8001
✅ Orchestrator started on port 9000
✅ All agents starting...
```

**Wait for all services to be ready** (~10 seconds)

---

### Command 2: Check Agents Are Running (Optional)
```bash
curl http://localhost:9000/agents/status
```

**Expected Response:**
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

### Command 3: Submit Application
**In a NEW terminal:**
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
python3 submit_application_v2.py
```

---

## 🎬 Complete Workflow Example

### Step 1: Start System (Terminal 1)
```bash
$ bash START_SYSTEM_v2.sh

===============================================
🚀 STARTING MULTI-AGENT SYSTEM v2
===============================================

1️⃣  Starting Intake Agent on port 8001...
2️⃣  Starting Orchestrator on port 9000...
3️⃣  Starting other agents...
   - KYC Agent (8002)...
   - Face Agent (8003)...
   - Payslip Agent (8004)...
   - Bank Agent (8005)...
   - Credit Agent (8006)...

✅ All agents started!

⏳ Press Ctrl+C to stop all services...
```

**Leave this running**

---

### Step 2: Check Health (Terminal 2)
```bash
$ curl http://localhost:9000/agents/status

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

✅ All 6 agents are running!

---

### Step 3: Submit Application (Terminal 3)
```bash
$ python3 submit_application_v2.py

================================================================================
🏦 LOAN APPLICATION CLIENT v2
================================================================================

📞 Starting conversation with Intake Agent...

✅ Application ID: APP-XYZ123ABC...

Bot: Welcome to loan verification!

What type of loan do you need? (personal/home/auto/education)
You: personal

Bot: What is your full name?
You: John Doe

Bot: What is your date of birth? (YYYY-MM-DD)
You: 1990-05-15

... (continues with all 17 questions) ...

Bot: Please upload your KYC document (Aadhaar/PAN/Passport)
You: ./images/nithin3.jpg

Bot: Please upload your selfie for face verification
You: ./images/nithinPAN.png

Bot: Please upload your payslip (or type 'skip')
You: ./payslip/payslip_nithin_j.txt

Bot: Please upload your bank statement (or type 'skip')
You: skip

✅ Application data collected! Submitting to orchestrator...
✅ Application submitted for verification.
   Verification in progress...

================================================================================
📊 APPLICATION SUMMARY
================================================================================

👤 Name: John Doe
📧 Email: john@example.com
💼 Employment: salaried
💰 Income: ₹60,000/month
🏦 Loan Amount: ₹500,000
⏱️  Duration: 60 months

================================================================================
```

---

## 🔄 Behind the Scenes

When you answer the last question:

1. **Intake Agent** collects all 17 answers ✅
2. **Intake Agent** validates all answers ✅
3. **Intake Agent** saves to database ✅
4. **Intake Agent** packages everything ✅
5. **Intake Agent** AUTOMATICALLY sends to Orchestrator ✅

Orchestrator receives application and:

6. **Orchestrator** calls 4 agents in parallel:
   - KYC Agent (document verification)
   - Face Agent (face verification)
   - Payslip Agent (income verification)
   - Bank Agent (financial analysis)

7. **Orchestrator** merges all results ✅

8. **Orchestrator** calls Credit Agent for final decision ✅

9. **Orchestrator** saves complete audit file ✅

10. **Orchestrator** returns status to user ✅

---

## 📊 Data Flow Diagram

```
┌──────────────────────────────────┐
│ User runs:                       │
│ python3 submit_application_v2.py │
└────────────┬─────────────────────┘
             │
             │ POST /start
             ▼
┌────────────────────────────────────────┐
│ INTAKE AGENT (8001)                    │
│ ✅ Asks Question 1: Loan Type?         │
│ ✅ Validates answer                    │
│ ✅ Asks Question 2: Full Name?         │
│ ✅ Validates answer                    │
│ ... (Questions 3-13)                   │
│ ✅ Asks Question 14: Upload KYC        │
│ ✅ Asks Question 15: Upload Selfie     │
│ ✅ Asks Question 16: Upload Payslip    │
│ ✅ Asks Question 17: Upload Bank       │
│ ✅ All questions complete              │
└────────────┬─────────────────────────┘
             │
             │ POST /orchestrate
             │ {
             │   app_id,
             │   user_answers,
             │   file_uris,
             │   loan_request
             │ }
             ▼
┌────────────────────────────────────────┐
│ ORCHESTRATOR (9000)                    │
│                                        │
│ ⚡ CALL PARALLEL AGENTS:               │
│   ├─ KYC (8002)                        │
│   ├─ Face (8003)                       │
│   ├─ Payslip (8004)                    │
│   └─ Bank (8005)                       │
│                                        │
│ 🔗 MERGE RESULTS                       │
│                                        │
│ 💳 CALL CREDIT AGENT (8006)            │
│                                        │
│ 💾 SAVE AUDIT FILE                     │
│    audit/JOB-ABC123.json               │
│                                        │
│ ✅ RETURN DECISION                     │
└────────────────────────────────────────┘
```

---

## 📁 File Organization

```
System v2 Files Created:

INTAKE AGENT (Port 8001):
  ✅ chat_flow_v2.py        - 17 questions + validators
  ✅ storage_v2.py          - State persistence
  ✅ main_v2.py             - FastAPI server

ORCHESTRATOR (Port 9000):
  ✅ config_v2.py           - Agent configuration
  ✅ main_v2.py             - FastAPI server
  
STARTUP:
  ✅ START_SYSTEM_v2.sh     - Start all services
  ✅ start_intake_v2.sh     - Start intake only
  ✅ start_orchestrator_v2.sh - Start orchestrator only

CLIENT:
  ✅ submit_application_v2.py - Interactive client

DOCUMENTATION:
  ✅ SYSTEM_v2_README.md     - Full technical docs
  ✅ IMPLEMENTATION_SUMMARY_v2.md - What was built
  ✅ QUICK_START_v2.md       - Quick reference
  ✅ verify_system_v2.py     - Verification script
```

---

## ✅ Requirements Checklist

### ✅ Section A - Intake Agent True Conversation
- [x] Asks ONE question at a time
- [x] Validates before progressing
- [x] Does NOT skip questions
- [x] Saves after every answer to database
- [x] Resumes from last question on restart
- [x] Asks all 13 required questions + 4 file uploads
- [x] Handles conditional questions (employer only for salaried)
- [x] Auto-submits payload to orchestrator when complete

### ✅ Section B - Orchestrator Multi-Agent
- [x] Exposes POST /orchestrate endpoint
- [x] Calls KYC, Face, Payslip, Bank agents IN PARALLEL
- [x] Merges their results
- [x] Calls Credit agent with merged evidence
- [x] Saves audit file to disk
- [x] Returns job_id + status
- [x] Includes retry logic for each agent
- [x] Includes timeout handling

### ✅ Section C - Health Check
- [x] Exposes GET /agents/status endpoint
- [x] Returns status for intake + all 6 agents
- [x] Shows RUNNING or DOWN
- [x] Uses 2-second timeout per agent
- [x] Works without any agents needing to be running

### ✅ Section D - Fix 404 Errors
- [x] Orchestrator runs on port 9000 (NOT 8000)
- [x] Intake calls correct orchestrator endpoint
- [x] No other URLs used for agent communication
- [x] All agent ports configured correctly

### ✅ Section E - Full Pipeline
- [x] Intake triggers orchestrator automatically
- [x] Orchestrator calls all agents
- [x] No agents are skipped
- [x] All outputs in final decision JSON
- [x] Complete evidence trail saved

---

## 🧪 Testing Checklist

### Test 1: Start System
```bash
bash START_SYSTEM_v2.sh
```
✅ All services start without errors

### Test 2: Check Health
```bash
curl http://localhost:9000/agents/status
```
✅ Returns all agents as RUNNING

### Test 3: Test Intake Agent
```bash
curl -X POST http://localhost:8001/start
```
✅ Returns first question (loan_type)

### Test 4: Submit Application
```bash
python3 submit_application_v2.py
```
✅ Asks 17 questions sequentially
✅ Validates answers
✅ Auto-submits to orchestrator
✅ Returns completion message

### Test 5: Check Results
```bash
curl http://localhost:9000/status/JOB-ABC123
```
✅ Returns complete job status with all agent results

### Test 6: View Audit
```bash
cat audit/JOB-ABC123.json
```
✅ Shows complete audit trail of all agents

---

## 🎓 Learning the System

### Understanding the Flow
1. Read: `QUICK_START_v2.md` (2 min)
2. Read: `SYSTEM_v2_README.md` (10 min)
3. Read: `IMPLEMENTATION_SUMMARY_v2.md` (5 min)

### Understanding the Code
1. Look at: `agents/intake_agent/chat_flow_v2.py` (questions & validators)
2. Look at: `agents/intake_agent/main_v2.py` (FastAPI endpoints)
3. Look at: `orchestrator_agent/main_v2.py` (orchestration logic)

---

## 🚀 Ready to Launch!

**Everything is set up and ready to run.**

Run these three commands in order:

```bash
# Terminal 1
bash START_SYSTEM_v2.sh

# Terminal 2 (wait 10 seconds, then run)
curl http://localhost:9000/agents/status

# Terminal 3 (after confirming all agents running)
python3 submit_application_v2.py
```

**That's it! The entire system will work together!** ✅

---

## 📞 Support

If issues arise:

1. **Check logs:** `tail -f logs/intake.log`
2. **Kill stuck processes:** `pkill -f "python3 main_v2"`
3. **Check ports:** `lsof -i :9000`
4. **Reinstall deps:** `pip install fastapi uvicorn pydantic httpx requests`

---

**System v2 is production-ready!** 🎉
