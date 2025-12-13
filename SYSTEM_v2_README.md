# Multi-Agent Loan Verification System v2

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ USER CLIENT (submit_application_v2.py)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ INTAKE AGENT (8001)   │
         │ - Sequential Q&A      │
         │ - File uploads        │
         │ - State persistence   │
         └───────────┬───────────┘
                     │
              (auto-submits)
                     │
                     ▼
      ┌──────────────────────────────┐
      │ ORCHESTRATOR (9000)          │
      │ /orchestrate                 │
      │ POST with application data   │
      └──────────┬───────────────────┘
                 │
    ┌────────────┼────────────┐
    │     PARALLEL AGENTS      │
    │   (all called at once)  │
    ▼         ▼         ▼         ▼
  KYC(2)  FACE(3)  PAYSLIP(4) BANK(5)
  
         (results merged)
         
              ▼
         CREDIT AGENT (6)
         (final decision)
         
              ▼
      (audit file saved)
```

## File Structure

### Intake Agent v2
- `agents/intake_agent/chat_flow_v2.py` - Conversation flow + validators
- `agents/intake_agent/storage_v2.py` - State persistence
- `agents/intake_agent/main_v2.py` - FastAPI server (port 8001)

### Orchestrator v2
- `orchestrator_agent/config_v2.py` - Agent configuration
- `orchestrator_agent/main_v2.py` - Main orchestrator (port 9000)

### Client
- `submit_application_v2.py` - Interactive client
- `START_SYSTEM_V2.sh` - Start all services

---

## Quick Start

### Step 1: Make scripts executable
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
chmod +x START_SYSTEM_V2.sh start_intake_v2.sh start_orchestrator_v2.sh submit_application_v2.py
```

### Step 2: Start all agents
```bash
bash START_SYSTEM_V2.sh
```

Output:
```
✅ Intake Agent started on port 8001
✅ Orchestrator started on port 9000
✅ Other agents starting...
```

### Step 3: In another terminal, submit application
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
python3 submit_application_v2.py
```

---

## Workflow

### 1️⃣ Intake Agent (Port 8001)

Asks questions one by one in strict order:

```
1. What type of loan? (personal/home/auto/education)
2. Full name?
3. Date of birth? (YYYY-MM-DD)
4. Phone? (10 digits)
5. Email?
6. PAN? (AAAAA9999A)
7. Employment type? (salaried/self-employed/student)
8. Employer name? (only if salaried)
9. Designation? (only if salaried)
10. Years at job? (only if salaried)
11. Monthly income?
12. Loan amount?
13. Tenure? (months)
14. Upload KYC file (REQUIRED)
15. Upload selfie (REQUIRED)
16. Upload payslip (required if salaried)
17. Upload bank statement (optional)
```

**Endpoints:**
- `POST /start` - Start conversation
- `POST /message` - Send answer
- `GET /state/{app_id}` - Get state
- `GET /health` - Health check

**Example:**
```bash
# Start
curl -X POST http://localhost:8001/start

# Answer
curl -X POST http://localhost:8001/message \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-...",
    "user_message": "personal"
  }'
```

### 2️⃣ Orchestrator (Port 9000)

Receives application from Intake → Calls agents in parallel → Merges → Calls credit agent

**Endpoints:**
- `POST /orchestrate` - Process application
- `GET /status/{job_id}` - Get job status
- `GET /agents/status` - Health of all agents
- `GET /health` - Orchestrator health

**Request:**
```json
{
  "application_id": "APP-...",
  "user_answers": {...},
  "file_uris": {
    "kyc_file": "./images/aadhaar.jpg",
    "selfie_file": "./images/selfie.jpg",
    "payslip_file": "./payslip/file.txt",
    "bank_statement_file": null
  },
  "loan_request": {
    "loan_amount": 500000,
    "tenure_months": 60
  }
}
```

**Response:**
```json
{
  "job_id": "JOB-ABC123",
  "application_id": "APP-XYZ",
  "status": "COMPLETED",
  "message": "Orchestration completed. Status: APPROVED"
}
```

### 3️⃣ Parallel Agents

All called simultaneously:
- **KYC Agent (8002)** - Verify documents
- **Face Agent (8003)** - Face verification
- **Payslip Agent (8004)** - Income verification
- **Bank Agent (8005)** - Financial analysis

Results merged into single evidence object.

### 4️⃣ Credit Agent (8006)

Makes final decision based on merged evidence:
- Credit score
- Approval status
- Loan amount
- Interest rate
- EMI

---

## Key Features

✅ **Strict Sequential Flow** - No skipping questions
✅ **Validation** - Each answer validated before proceeding
✅ **State Persistence** - Resume from last question
✅ **Conditional Questions** - Skip non-applicable questions
✅ **File Uploads** - KYC, selfie, payslip, bank statements
✅ **Parallel Processing** - 4 agents called simultaneously
✅ **Auto-submission** - Intake auto-submits to orchestrator
✅ **Health Checks** - Monitor all agent status
✅ **Audit Trail** - JSON file for each job

---

## Testing

### Check agent health
```bash
curl http://localhost:9000/agents/status
```

Response:
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

### Get job status
```bash
curl http://localhost:9000/status/JOB-ABC123
```

### View audit trail
```bash
cat ./audit/JOB-ABC123.json
```

---

## Troubleshooting

### Port already in use
```bash
# Kill process using port 8001
lsof -ti:8001 | xargs kill -9

# Kill process using port 9000
lsof -ti:9000 | xargs kill -9
```

### Agent connection errors
```bash
# Check if agent is running
curl http://localhost:8001/health
curl http://localhost:9000/health

# View logs
tail -f ./logs/intake.log
tail -f ./logs/orchestrator.log
```

### Missing dependencies
```bash
pip install fastapi uvicorn pydantic httpx requests
```

---

## Configuration

Edit `orchestrator_agent/config_v2.py`:
- Agent URLs/ports
- Timeouts
- Retry logic
- Storage directories

---

## Logs

Logs saved to `./logs/`:
- `intake.log` - Intake agent logs
- `orchestrator.log` - Orchestrator logs
- `kyc.log`, `face.log`, etc. - Agent logs

---

## Audit Files

Saved to `./audit/`:
- `JOB-ABC123.json` - Complete job audit including all agent results

---

## Next Steps

1. ✅ Ensure all agents running on correct ports (8001-8006)
2. ✅ Start system: `bash START_SYSTEM_V2.sh`
3. ✅ Submit app: `python3 submit_application_v2.py`
4. ✅ Check status: `curl http://localhost:9000/agents/status`
5. ✅ View results: `cat ./audit/JOB-*.json`
