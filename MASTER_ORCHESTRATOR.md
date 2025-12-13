# Master Orchestrator Agent - Complete Integration

## 🎯 Overview

The **Master Orchestrator Agent** coordinates all 6 specialized agents to process loan applications in a strict sequential order, collecting evidence at each stage and generating a final decision.

### Execution Order (SEQUENTIAL)

```
1️⃣  Intake Agent    (:8001)  → Collect applicant information
2️⃣  KYC Agent       (:8002)  → Verify identity documents
3️⃣  Face Agent      (:8003)  → Verify face & liveness
4️⃣  Payslip Agent   (:8004)  → Verify income from payslip
5️⃣  Bank Agent      (:8005)  → Analyze bank statements
6️⃣  Credit Agent    (:8006)  → Final credit decision
                    ⬇️
           FINAL DECISION (APPROVED/REJECTED/MANUAL)
```

## 📂 Repository Structure

```
MSN-loan-agent/
│
├── 🤖 AGENTS (6 independent services)
│   ├── intake_agent/           (:8001) Conversational intake
│   ├── kyc_agent/              (:8002) Document verification
│   ├── face-agent/             (:8003) Face recognition
│   ├── payslip-agent/          (:8004) Income verification
│   ├── bank-agent/             (:8005) Financial analysis
│   └── credit-agent/           (:8006) Credit scoring
│
├── 🔗 ORCHESTRATOR
│   ├── orchestrator_agent.py        Master orchestrator (core logic)
│   ├── orchestrator_agent_cli.py    CLI tool
│   └── ORCHESTRATOR_WORKFLOW.md     Detailed workflow
│
├── 📚 DOCUMENTATION
│   ├── README.md                Main project README
│   ├── ORCHESTRATOR_README.md   Orchestrator overview
│   ├── ORCHESTRATOR_WORKFLOW.md Execution flow diagram
│   └── DOCUMENTATION_INDEX.md   Navigation guide
│
├── 🐳 DOCKER
│   └── docker-compose.yml       Start all services
│
└── ⚙️ CONFIG
    └── example_application_config.json
```

## 🚀 Quick Start

### 1. Start All Services

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or start manually (6 terminals needed)
cd agents/intake_agent && python main.py
cd agents/kyc_agent && python main.py
cd agents/face-agent && python main.py
cd agents/payslip-agent && python main.py
cd agents/bank-agent && python main.py
cd agents/credit-agent && python main.py
```

### 2. Check Agent Health

```bash
python orchestrator_agent_cli.py health
```

Output:
```
🏥 CHECKING AGENT HEALTH

Agent Status:
──────────────────────────────────────
✅ INTAKE    - HEALTHY
✅ KYC       - HEALTHY
✅ FACE      - HEALTHY
✅ PAYSLIP   - HEALTHY
✅ BANK      - HEALTHY
✅ CREDIT    - HEALTHY
──────────────────────────────────────

✅ All agents are healthy and ready!
```

### 3. Process Application

```bash
python orchestrator_agent_cli.py process APP-001 example_application_config.json
```

### 4. Run Demo

```bash
python orchestrator_agent_cli.py demo
```

## 📊 Processing Workflow

### Stage 1: Intake Agent (:8001)
**Purpose**: Conversational data collection and validation

**Input**:
```json
{
  "application_id": "APP-001",
  "conversation_id": "conv-APP-001",
  "user_message": "Starting loan application",
  "applicant_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+91-9876543210"
  }
}
```

**Output**:
```json
{
  "conversation_id": "conv-APP-001",
  "slots_filled": ["name", "email", "phone", "employment"],
  "completion_percentage": 80
}
```

### Stage 2: KYC Agent (:8002)
**Purpose**: Identity document verification

**Input**: Document path + intake data

**Output**:
```json
{
  "kyc_verified": true,
  "verification_score": 0.99,
  "extracted_name": "John Doe",
  "extracted_dob": "1990-05-15",
  "name_match": true
}
```

### Stage 3: Face Agent (:8003)
**Purpose**: Face identity verification & liveness check

**Input**: Selfie image + applicant info

**Output**:
```json
{
  "face_verified": true,
  "liveness_score": 0.98,
  "match_confidence": 0.97,
  "comparison": "MATCH"
}
```

### Stage 4: Payslip Agent (:8004)
**Purpose**: Income verification through payslip

**Input**: Payslip file

**Output**:
```json
{
  "monthly_salary": 66666.67,
  "annual_salary": 800000,
  "basic_pay": 50000,
  "hra": 16666.67,
  "deductions": 3333.33,
  "confidence": 0.95
}
```

### Stage 5: Bank Agent (:8005)
**Purpose**: Financial analysis through bank statements

**Input**: Bank statement + payslip data

**Output**:
```json
{
  "average_balance": 150000,
  "transaction_volume": 2400000,
  "spending_ratio": 0.45,
  "risk_indicators": ["low_savings"],
  "financial_health": "GOOD"
}
```

### Stage 6: Credit Agent (:8006)
**Purpose**: Final credit scoring and decision

**Input**: All prior evidence

**Output**:
```json
{
  "credit_score": 750,
  "risk_level": "Low",
  "recommended_loan_amount": 600000,
  "interest_rate": 8.5,
  "tenure_months": 60,
  "decision": "APPROVED"
}
```

## 📋 Final Decision

After all 6 agents complete, orchestrator generates:

```json
{
  "application_id": "APP-001",
  "final_status": "APPROVED",
  "reason": "All verifications passed - Low risk",
  "processed_at": "2024-01-15T10:45:00Z",
  "recommendation": {
    "action": "APPROVED",
    "loan_amount": 600000,
    "interest_rate": 8.5,
    "tenure_months": 60
  },
  "evidence_summary": {
    "intake": { ... },
    "kyc": { ... },
    "face": { ... },
    "payslip": { ... },
    "bank": { ... },
    "credit": { ... }
  }
}
```

## 💻 Using the Orchestrator

### Python Async API

```python
import asyncio
from orchestrator_agent import MasterOrchestrator

async def main():
    orchestrator = MasterOrchestrator()
    
    result = await orchestrator.process_application(
        application_id="APP-001",
        applicant_data={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+91-9876543210",
            "employment_status": "salaried",
            "annual_income": 800000
        },
        documents={
            "aadhaar": "/path/to/aadhaar.pdf",
            "selfie": "/path/to/selfie.jpg",
            "payslip": "/path/to/payslip.pdf",
            "bank_statement": "/path/to/bank_statement.pdf"
        }
    )
    
    print(f"Status: {result['final_status']}")
    print(f"Loan Amount: ₹{result['recommendation']['loan_amount']:,.0f}")

asyncio.run(main())
```

### CLI Usage

```bash
# Check health
python orchestrator_agent_cli.py health

# Process application
python orchestrator_agent_cli.py process APP-001 config.json

# Check status
python orchestrator_agent_cli.py status APP-001

# Run demo
python orchestrator_agent_cli.py demo
```

## 🔄 Data Flow Diagram

```
┌──────────────┐
│ Application  │
│   Request    │
└──────┬───────┘
       │
       ├─► [INTAKE] (Port 8001)
       │   └─ Output: conversation_id, slots
       │
       ├─► [KYC] (Port 8002)
       │   └─ Output: verified, score, extracted_data
       │
       ├─► [FACE] (Port 8003)
       │   └─ Output: verified, liveness, match
       │
       ├─► [PAYSLIP] (Port 8004)
       │   └─ Output: salary, deductions, annual_income
       │
       ├─► [BANK] (Port 8005)
       │   └─ Output: balance, transactions, risk
       │
       ├─► [CREDIT] (Port 8006)
       │   └─ Output: score, risk_level, decision
       │
       └─► [FINAL DECISION]
           └─ APPROVED / REJECTED / MANUAL_REVIEW
```

## ⚙️ Configuration

### Agent Endpoints

```python
AGENTS = {
    ProcessingStage.INTAKE: {
        "url": "http://localhost:8001",
        "endpoint": "/converse"
    },
    ProcessingStage.KYC: {
        "url": "http://localhost:8002",
        "endpoint": "/parse-document"
    },
    ProcessingStage.FACE: {
        "url": "http://localhost:8003",
        "endpoint": "/verify-face"
    },
    ProcessingStage.PAYSLIP: {
        "url": "http://localhost:8004",
        "endpoint": "/payslip/verify"
    },
    ProcessingStage.BANK: {
        "url": "http://localhost:8005",
        "endpoint": "/parse-bank-statement"
    },
    ProcessingStage.CREDIT: {
        "url": "http://localhost:8006",
        "endpoint": "/score-application"
    }
}
```

### Timeouts & Retries

```python
HEALTH_CHECK_TIMEOUT = 5          # Health check timeout
PROCESSING_TIMEOUT = 60           # Per-agent timeout
MAX_RETRIES = 2                   # Retry attempts
```

## 🛠️ Troubleshooting

### Agents Not Starting
```bash
# Check if ports are in use
lsof -i :8001-8006

# Kill existing processes
pkill -f "python main.py"

# Restart
docker-compose down
docker-compose up -d
```

### Agent Offline
```bash
# Check which agents are down
python orchestrator_agent_cli.py health

# Check logs
docker-compose logs <agent_name>

# Restart specific agent
docker-compose restart <agent_name>
```

### Processing Timeout
- Check network connectivity
- Verify agent is responding
- Check agent logs for errors
- Increase timeout if needed

## 📊 Metrics & Monitoring

### Processing Time
- **Total**: ~2-3 minutes
- **Per-stage**: 10-30 seconds

### Success Criteria
- ✅ All 6 agents complete
- ✅ All evidence collected
- ✅ Final decision generated
- ✅ Complete audit trail

## 🔐 Security

- ✓ Input validation at each stage
- ✓ Data sanitization
- ✓ Error handling with logging
- ✓ Timeout protection
- ✓ Retry logic for transient failures

## 📚 Files

| File | Purpose |
|------|---------|
| `orchestrator_agent.py` | Core orchestrator logic |
| `orchestrator_agent_cli.py` | Command-line interface |
| `ORCHESTRATOR_WORKFLOW.md` | Detailed workflow diagram |
| `example_application_config.json` | Example configuration |

## 🎯 Next Steps

1. **Read**: [ORCHESTRATOR_WORKFLOW.md](./ORCHESTRATOR_WORKFLOW.md)
2. **Start**: `docker-compose up -d`
3. **Check**: `python orchestrator_agent_cli.py health`
4. **Demo**: `python orchestrator_agent_cli.py demo`
5. **Process**: `python orchestrator_agent_cli.py process APP-001 config.json`

---

**All 6 agents coordinated into a powerful workflow!** 🚀

For detailed documentation, see [ORCHESTRATOR_WORKFLOW.md](./ORCHESTRATOR_WORKFLOW.md)
