# Multi-Agent Orchestrator - Complete Documentation

## 📋 Overview

This is a **production-ready multi-agent orchestrator** for the MSN Loan Origination System. It coordinates 6 specialized AI agents to process loan applications end-to-end with intelligent workflow management.

### System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    LOAN ORCHESTRATOR                             │
│         (LangChain-based Agent Coordination)                     │
└─┬──────────────┬────────────────┬────────────────┬──────────────┘
  │              │                │                │
  ▼              ▼                ▼                ▼
┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐
│  Intake    │ │    KYC     │ │  Credit    │ │   Payslip    │
│  Agent     │ │   Agent    │ │   Agent    │ │    Agent     │
│ :8001      │ │  :8002     │ │  :8003     │ │   :8004      │
└────────────┘ └────────────┘ └────────────┘ └──────────────┘
       │              │                │              │
       └──────────────┴────────────────┴──────────────┘
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
  ┌──────────┐ ┌──────────┐ ┌───────────┐
  │  Bank    │ │  Face    │ │  Memory   │
  │  Agent   │ │  Agent   │ │  (Redis)  │
  │  :8005   │ │  :8006   │ └───────────┘
  └──────────┘ └──────────┘
```

## 🎯 Key Features

✅ **Complete Loan Processing Pipeline**
- End-to-end automation from intake to approval
- Parallel processing for efficiency
- Error handling and retries

✅ **6 Specialized Agents**
- Intake Agent: Conversational data collection
- KYC Agent: Document verification
- Credit Agent: Credit scoring
- Payslip Agent: Income verification
- Bank Agent: Financial analysis
- Face Agent: Identity verification

✅ **Multiple Access Methods**
- Async Python API (complete_orchestrator.py)
- Sync Python Wrapper (orchestrator_sync.py)
- Command-line Interface (orchestrator_cli.py)
- REST API ready

✅ **Production Ready**
- Health checks
- Comprehensive logging
- Error handling
- State management
- Report generation

## 📂 Files Structure

```
MSN-loan-agent/
├── complete_orchestrator.py          # Async orchestrator (core)
├── orchestrator_sync.py              # Synchronous wrapper
├── orchestrator_cli.py               # CLI tool
├── orchestrator_requirements.txt     # Dependencies
├── example_application_config.json   # Example configuration
├── ORCHESTRATOR_GUIDE.md             # Detailed documentation
├── ORCHESTRATOR_QUICKSTART.md        # Quick start guide
├── ORCHESTRATOR_README.md            # This file
└── agents/
    ├── intake_agent/                 # Conversational intake
    ├── kyc_agent/                    # Document verification
    ├── credit-agent/                 # Credit scoring
    ├── payslip-agent/                # Income verification
    ├── bank-agent/                   # Bank statement analysis
    └── face-agent/                   # Face recognition
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r orchestrator_requirements.txt
```

### 2. Start All Services

```bash
# Using Docker Compose
docker-compose up -d

# Or manually (in separate terminals)
cd agents/intake_agent && python main.py
cd agents/kyc_agent && python main.py
cd agents/credit-agent && python main.py
cd agents/payslip-agent && python main.py
cd agents/bank-agent && python main.py
cd agents/face-agent && python main.py
```

### 3. Check Health

```bash
python orchestrator_cli.py health
```

### 4. Run Demo

```bash
python orchestrator_cli.py demo
```

### 5. Process Application

```bash
python orchestrator_cli.py process APP-001 example_application_config.json
```

## 💻 Usage Examples

### Command Line

```bash
# Check agent health
python orchestrator_cli.py health

# Process application
python orchestrator_cli.py process APP-001 config.json

# Check status
python orchestrator_cli.py status APP-001

# Generate report
python orchestrator_cli.py report APP-001

# Run demo
python orchestrator_cli.py demo
```

### Python Synchronous API

```python
from orchestrator_sync import (
    SyncOrchestrator,
    create_applicant,
    create_documents,
    create_application_request
)

# Create applicant
applicant = create_applicant(
    name="John Doe",
    email="john@example.com",
    phone="+91-9876543210",
    date_of_birth="1990-05-15",
    address="123 Main Street",
    city="Bangalore",
    state="Karnataka",
    pincode="560001",
    employment_status="salaried",
    annual_income=800000,
    current_employer="TechCorp Inc",
    designation="Senior Engineer",
    years_at_current_employer=5
)

# Create documents
documents = create_documents(
    aadhaar="/path/to/aadhaar.pdf",
    selfie="/path/to/selfie.jpg",
    recent_payslip="/path/to/payslip.pdf",
    bank_statement="/path/to/bank_statement.pdf"
)

# Create application
app_request = create_application_request(
    application_id="APP-001",
    applicant_info=applicant,
    documents=documents,
    loan_amount=500000,
    loan_tenure_months=60,
    loan_purpose="Home Purchase"
)

# Process
orchestrator = SyncOrchestrator()
result = orchestrator.process_application(app_request)

print(f"Status: {result['status']}")
print(f"Credit Score: {result['results']['credit']['credit_score']}")
```

### Python Async API

```python
import asyncio
from complete_orchestrator import LoanOrchestratorV2

async def main():
    orchestrator = LoanOrchestratorV2()
    
    result = await orchestrator.process_complete_application(
        application_id="APP-001",
        applicant_info={
            "name": "John Doe",
            "email": "john@example.com",
            # ... more fields
        },
        documents={
            "aadhaar": "/path/to/aadhaar.pdf",
            "selfie": "/path/to/selfie.jpg",
            # ... more documents
        }
    )
    
    print(result)

asyncio.run(main())
```

### REST API Integration

```python
from fastapi import FastAPI
from orchestrator_sync import SyncOrchestrator

app = FastAPI()
orchestrator = SyncOrchestrator()

@app.post("/api/loan/apply")
async def apply_for_loan(data: dict):
    result = orchestrator.process_application(
        # Build from data
    )
    return result
```

## 📊 Processing Pipeline

### Stage 1: Intake
- Collect applicant information
- Validate initial data
- Prepare for document processing

### Stage 2: Verification (Parallel)
- Face verification
- KYC document processing

### Stage 3: Income Verification (Parallel)
- Payslip analysis
- Bank statement analysis

### Stage 4: Credit Assessment
- Credit scoring
- Risk evaluation
- Loan recommendation

### Stage 5: Submission
- Submit application
- Generate final record

## 🔧 Configuration

### Agent URLs

Edit `OrchestratorConfig` in `orchestrator_sync.py`:

```python
class OrchestratorConfig:
    INTAKE_URL = "http://localhost:8001"
    KYC_URL = "http://localhost:8002"
    CREDIT_URL = "http://localhost:8003"
    PAYSLIP_URL = "http://localhost:8004"
    BANK_URL = "http://localhost:8005"
    FACE_URL = "http://localhost:8006"
```

### Application Configuration

Create JSON file with applicant info and documents:

```json
{
  "application_id": "APP-001",
  "applicant_info": {
    "name": "John Doe",
    "email": "john@example.com",
    // ... more fields
  },
  "documents": {
    "aadhaar": "/path/to/aadhaar.pdf",
    "selfie": "/path/to/selfie.jpg",
    // ... more documents
  }
}
```

See `example_application_config.json` for complete example.

## 📈 Response Format

### Successful Processing

```json
{
  "status": "completed",
  "application_id": "APP-001",
  "created_at": "2024-01-15T10:30:00.000Z",
  "completed_at": "2024-01-15T10:45:00.000Z",
  "applicant_info": { ... },
  "results": {
    "intake": { ... },
    "face": {
      "verified": true,
      "liveness_score": 0.98,
      "match_confidence": 0.99
    },
    "kyc": {
      "documents_verified": ["aadhaar", "pan"],
      "verification_score": 0.99
    },
    "income": {
      "payslip": { "monthly_salary": 66666, "annual_salary": 800000 },
      "bank_statement": { "average_balance": 150000 }
    },
    "credit": {
      "credit_score": 750,
      "risk_level": "Low",
      "recommended_loan_amount": 600000,
      "interest_rate": 8.5
    }
  }
}
```

## 🛠️ Development & Testing

### Run CLI Demo

```bash
python orchestrator_cli.py demo
```

### Check Agent Health

```bash
python orchestrator_cli.py health
```

### Process Test Application

```bash
python orchestrator_cli.py process TEST-001 example_application_config.json
```

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **ORCHESTRATOR_GUIDE.md** | Complete detailed documentation |
| **ORCHESTRATOR_QUICKSTART.md** | Quick start guide with examples |
| **ORCHESTRATOR_README.md** | This file - overview |
| **orchestrator_requirements.txt** | Python dependencies |

## 🔍 Agent Details

### Intake Agent (Port 8001)
- Conversational loan application intake
- Slot filling for applicant information
- Application submission

### KYC Agent (Port 8002)
- Identity document parsing (Aadhaar, PAN, Passport)
- Document validation
- Information extraction

### Credit Agent (Port 8003)
- Credit score calculation
- Risk assessment
- Loan recommendation

### Payslip Agent (Port 8004)
- Payslip OCR and parsing
- Income extraction
- Salary verification

### Bank Agent (Port 8005)
- Bank statement parsing
- Financial behavior analysis
- Transaction analysis

### Face Agent (Port 8006)
- Face detection and recognition
- Liveness verification
- Identity matching

## 🚨 Troubleshooting

### Agents Not Starting
```bash
# Check ports in use
lsof -i :8001-8006

# Clear and restart
docker-compose down
docker-compose up -d
```

### Configuration Issues
```bash
# Validate JSON
python -m json.tool example_application_config.json
```

### Health Check Failed
```bash
python orchestrator_cli.py health
# Check individual agent logs
docker-compose logs intake_agent
```

## 📊 Monitoring

### Check Agent Health

```bash
python orchestrator_cli.py health
```

### View Application Status

```bash
python orchestrator_cli.py status APP-001
```

### Generate Report

```bash
python orchestrator_cli.py report APP-001
```

## 🔐 Security Considerations

1. **API Keys**: Store GROQ_API_KEY in environment variables
2. **Document Paths**: Ensure proper file permissions
3. **Logging**: Enable audit logging for compliance
4. **Validation**: Always validate applicant data

## 🚀 Deployment

### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes
See `docker-compose.yml` for service specifications that can be converted to K8s manifests.

### Cloud Deployment
- AWS: Use ECS with the provided Docker setup
- GCP: Deploy to Cloud Run or Cloud Functions
- Azure: Use App Service or Container Instances

## 📝 API Endpoints

### Health Check
```
GET /health
```

### Process Application
```
POST /api/loan/apply
Body: ApplicationRequest (JSON)
```

### Check Status
```
GET /api/loan/status/{application_id}
```

## 🤝 Integration Examples

- **Web Application**: FastAPI/Flask integration
- **Batch Processing**: Process multiple applications
- **Webhooks**: Status notifications
- **Databases**: Store results
- **Message Queues**: Async processing

See **ORCHESTRATOR_QUICKSTART.md** for detailed examples.

## 📞 Support & Documentation

1. **Quick Start**: [ORCHESTRATOR_QUICKSTART.md](./ORCHESTRATOR_QUICKSTART.md)
2. **Detailed Guide**: [ORCHESTRATOR_GUIDE.md](./ORCHESTRATOR_GUIDE.md)
3. **Agent Docs**: See `agents/*/README.md`
4. **Examples**: Check `example_application_config.json`

## 📋 Checklist

- [x] Clone repository
- [x] Install dependencies
- [x] Start services
- [x] Check agent health
- [x] Run demo application
- [x] Process test application
- [x] Generate reports

## 🎓 Learning Path

1. **Start**: Run `orchestrator_cli.py demo` to understand flow
2. **Explore**: Check `example_application_config.json`
3. **Learn**: Read ORCHESTRATOR_QUICKSTART.md
4. **Integrate**: Follow examples in documentation
5. **Deploy**: Configure for your environment

## 📄 License

Part of MSN Loan Origination System

## 🎉 Next Steps

1. **Start Services**: `docker-compose up -d`
2. **Check Health**: `python orchestrator_cli.py health`
3. **Run Demo**: `python orchestrator_cli.py demo`
4. **Process Application**: `python orchestrator_cli.py process APP-001 example_application_config.json`
5. **Integrate**: Follow examples in ORCHESTRATOR_QUICKSTART.md

---

**Happy Processing!** 🚀

For detailed documentation, see [ORCHESTRATOR_GUIDE.md](./ORCHESTRATOR_GUIDE.md)
For quick start, see [ORCHESTRATOR_QUICKSTART.md](./ORCHESTRATOR_QUICKSTART.md)
