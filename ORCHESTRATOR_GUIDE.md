# Multi-Agent Orchestrator Documentation

## Overview

The orchestrator system coordinates 6 specialized agents to process loan applications end-to-end:

1. **Intake Agent** (Port 8001) - Conversational loan application intake and slot filling
2. **KYC Agent** (Port 8002) - Document verification and parsing (Aadhaar, PAN, Passport)
3. **Credit Agent** (Port 8003) - Credit scoring and financial risk assessment
4. **Payslip Agent** (Port 8004) - Income verification from payslips using OCR
5. **Bank Agent** (Port 8005) - Bank statement parsing and financial behavior analysis
6. **Face Agent** (Port 8006) - Face detection and liveness verification

## Orchestrator Implementations

### 1. Async Orchestrator (`complete_orchestrator.py`)

Full-featured async orchestrator using LangChain for intelligent agent coordination.

**Features:**
- Parallel agent processing
- Health checks for all agents
- Application state management
- Error handling and retries
- Report generation

**Usage:**
```python
import asyncio
from complete_orchestrator import LoanOrchestratorV2

async def main():
    orchestrator = LoanOrchestratorV2(groq_api_key="your-key")
    
    # Check agent health
    health = await orchestrator.check_all_agents_health()
    print(health)
    
    # Process application
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

### 2. Synchronous Wrapper (`orchestrator_sync.py`)

Easy-to-use synchronous API wrapping the async orchestrator.

**Key Classes:**
- `ApplicantInfo` - Applicant details schema
- `DocumentSet` - Collection of documents
- `ApplicationRequest` - Complete application request
- `SyncOrchestrator` - Synchronous orchestrator wrapper

**Usage:**
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
    designation="Senior Software Engineer",
    years_at_current_employer=5
)

# Create documents
documents = create_documents(
    aadhaar="/path/to/aadhaar.pdf",
    pan="/path/to/pan.pdf",
    selfie="/path/to/selfie.jpg",
    recent_payslip="/path/to/payslip.pdf",
    bank_statement="/path/to/bank_statement.pdf"
)

# Create application request
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
print(result)
```

### 3. Command-Line Interface (`orchestrator_cli.py`)

Interactive CLI for orchestrator operations.

**Commands:**

#### Health Check
```bash
python orchestrator_cli.py health
```
Output:
```
🏥 Checking agent health...

Agent Status:
--------------------------------------------------
✅ intake          - Healthy
✅ kyc             - Healthy
✅ credit          - Healthy
✅ payslip         - Healthy
✅ bank            - Healthy
✅ face            - Healthy
--------------------------------------------------

✅ All agents are healthy and ready!
```

#### Process Application
```bash
python orchestrator_cli.py process APP-001 example_application_config.json
```

#### Check Application Status
```bash
python orchestrator_cli.py status APP-001
```

#### Generate Report
```bash
python orchestrator_cli.py report APP-001
```

#### Run Demo
```bash
python orchestrator_cli.py demo
```

## Processing Pipeline

The orchestrator follows a structured processing pipeline:

### Stage 1: Intake (Parallel: No)
- Collect applicant information through conversation
- Validate initial data
- Prepare for document processing

### Stage 2: Verification (Parallel: Yes)
- **Face Agent**: Verify identity through face recognition
- **KYC Agent**: Parse and validate identity documents

### Stage 3: Income Verification (Parallel: Yes)
- **Payslip Agent**: Extract and verify salary information
- **Bank Agent**: Analyze bank statements and financial behavior

### Stage 4: Credit Assessment (Parallel: No)
- **Credit Agent**: Score based on all collected information
- Generate credit recommendation
- Calculate loan eligibility

### Stage 5: Submission (Parallel: No)
- Submit application back through intake agent
- Generate final application record

## Configuration

### Agent URLs
Configure agent endpoints in `orchestrator_sync.py`:
```python
class OrchestratorConfig:
    INTAKE_URL = "http://localhost:8001"
    KYC_URL = "http://localhost:8002"
    CREDIT_URL = "http://localhost:8003"
    PAYSLIP_URL = "http://localhost:8004"
    BANK_URL = "http://localhost:8005"
    FACE_URL = "http://localhost:8006"
```

### Processing Configuration
```python
class OrchestratorConfig:
    PARALLEL_PROCESSING = True      # Enable parallel stage processing
    TIMEOUT_SECONDS = 60            # Request timeout
    MAX_RETRIES = 2                 # Number of retries
    
    # Feature flags
    ENABLE_KYC = True
    ENABLE_FACE_VERIFICATION = True
    ENABLE_CREDIT_SCORING = True
    ENABLE_INCOME_VERIFICATION = True
```

## Application Configuration Schema

### Example: `example_application_config.json`

```json
{
  "application_id": "APP-20240115-001",
  "applicant_info": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+91-9876543210",
    "date_of_birth": "1990-05-15",
    "address": "123 Main Street",
    "city": "Bangalore",
    "state": "Karnataka",
    "pincode": "560001",
    "employment_status": "salaried",
    "annual_income": 800000,
    "current_employer": "TechCorp Inc",
    "designation": "Senior Software Engineer",
    "years_at_current_employer": 5,
    "cibil_score": 750,
    "loan_amount_requested": 500000,
    "loan_tenure_months": 60,
    "loan_purpose": "Home Purchase"
  },
  "documents": {
    "aadhaar": "/path/to/aadhaar.pdf",
    "pan": "/path/to/pan.pdf",
    "selfie": "/path/to/selfie.jpg",
    "recent_payslip": "/path/to/payslip.pdf",
    "bank_statement": "/path/to/bank_statement.pdf"
  },
  "custom_fields": {
    "preferred_branch": "Bangalore",
    "referral_code": "TECH2024"
  },
  "priority": "normal"
}
```

## Agent Communication

All agents expose REST endpoints:

### Intake Agent (Port 8001)
```
POST /converse                  - Process conversation input
POST /update-slot              - Update application slot
POST /register-upload          - Register document upload
POST /submit-application       - Submit application
GET  /health                   - Health check
```

### KYC Agent (Port 8002)
```
POST /parse-document           - Parse identity documents
GET  /health                   - Health check
```

### Credit Agent (Port 8003)
```
POST /score-application        - Score application
GET  /model-info              - Get model information
GET  /health                  - Health check
```

### Payslip Agent (Port 8004)
```
POST /payslip/verify          - Verify payslip and extract income
GET  /health                  - Health check
```

### Bank Agent (Port 8005)
```
POST /parse-bank-statement    - Parse bank statement
GET  /health                  - Health check
```

### Face Agent (Port 8006)
```
POST /verify-face             - Verify face and liveness
GET  /health                  - Health check
```

## Starting Services

### Using Docker Compose
```bash
docker-compose up -d
```

### Manual Start
```bash
# Terminal 1: Intake Agent
cd agents/intake_agent && python main.py

# Terminal 2: KYC Agent
cd agents/kyc_agent && python main.py

# Terminal 3: Credit Agent
cd agents/credit-agent && python main.py

# Terminal 4: Payslip Agent
cd agents/payslip-agent && python main.py

# Terminal 5: Bank Agent
cd agents/bank-agent && python main.py

# Terminal 6: Face Agent
cd agents/face-agent && python main.py
```

## Response Format

### Successful Application Processing
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
      "payslip": { ... },
      "bank_statement": { ... }
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

### Error Response
```json
{
  "status": "failed",
  "application_id": "APP-001",
  "error": "Error message",
  "timestamp": "2024-01-15T10:45:00.000Z"
}
```

## Error Handling

The orchestrator handles various error scenarios:

1. **Agent Unavailable**: Retries up to MAX_RETRIES times
2. **Timeout**: Requests timeout after TIMEOUT_SECONDS
3. **Invalid Data**: Validation errors are caught and logged
4. **Processing Failure**: Application status set to "failed" with error details

## Logging

Comprehensive logging at each stage:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logs include:
# - Application start/completion
# - Agent health checks
# - Processing stages
# - Errors and exceptions
```

## Performance Optimization

1. **Parallel Processing**: Stages 2 and 3 run agents in parallel
2. **Connection Pooling**: Reuses HTTP connections
3. **Timeout Configuration**: Prevents hanging requests
4. **Retry Logic**: Handles transient failures

## Troubleshooting

### Agents Not Responding
```bash
# Check agent health
python orchestrator_cli.py health

# Verify agents are running
docker-compose ps
# or
ps aux | grep python
```

### Configuration Issues
- Verify agent URLs in `OrchestratorConfig`
- Check port availability (8001-8006)
- Ensure JSON config files are valid

### Processing Failures
- Check orchestrator logs
- Verify document paths exist
- Ensure agent endpoints are correct
- Check agent logs for specific errors

## Examples

See `example_application_config.json` for a complete application configuration example.

## Advanced Usage

### Custom Agent Workflow
```python
orchestrator = LoanOrchestratorV2()

# Process specific agents only
result = await orchestrator._process_face_verification(app_id, selfie_path)
result = await orchestrator._process_kyc(app_id, doc_path)
```

### Application State Management
```python
# Get application status
status = orchestrator.get_application_status(app_id)

# Get all applications
all_apps = orchestrator.get_all_applications()

# Generate report
report = orchestrator.generate_report(app_id)
```

## Integration Points

The orchestrator can be integrated with:
- **Web Applications**: FastAPI/Flask endpoints
- **Batch Processing**: Background jobs with Celery
- **Messaging Queues**: Kafka/RabbitMQ for async processing
- **Databases**: Store application state and results
- **Webhooks**: Notify external systems of status changes

## License

This orchestrator is part of the MSN Loan Agent system.

## Support

For issues and questions, refer to:
- Agent documentation in `agents/*/README.md`
- System architecture documentation
- Agent-specific logs and outputs
