# Orchestrator Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Start All Services

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or start manually in separate terminals
cd agents/intake_agent && python main.py &
cd agents/kyc_agent && python main.py &
cd agents/credit-agent && python main.py &
cd agents/payslip-agent && python main.py &
cd agents/bank-agent && python main.py &
cd agents/face-agent && python main.py &
```

### 2. Check Agent Health

```bash
python orchestrator_cli.py health
```

Expected output:
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

### 3. Run Demo

```bash
python orchestrator_cli.py demo
```

This runs a complete demo application through all agents with simulated responses.

### 4. Process Real Application

```bash
# Create or edit example_application_config.json with your data
python orchestrator_cli.py process APP-001 example_application_config.json
```

### 5. Check Status and Reports

```bash
python orchestrator_cli.py status APP-001
python orchestrator_cli.py report APP-001
```

## 💻 Python Integration

### Synchronous Usage (Simplest)

```python
from orchestrator_sync import (
    SyncOrchestrator,
    create_applicant,
    create_documents,
    create_application_request
)

# Create applicant
applicant = create_applicant(
    name="Jane Smith",
    email="jane@example.com",
    phone="+91-9876543210",
    date_of_birth="1992-08-20",
    address="456 Oak Avenue",
    city="Mumbai",
    state="Maharashtra",
    pincode="400001",
    employment_status="salaried",
    annual_income=1000000,
    current_employer="FinTech Corp",
    designation="Product Manager",
    years_at_current_employer=3
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
    application_id="APP-002",
    applicant_info=applicant,
    documents=documents,
    loan_amount=750000,
    loan_tenure_months=60,
    loan_purpose="Vehicle Purchase"
)

# Process
orchestrator = SyncOrchestrator()
result = orchestrator.process_application(app_request)

print(f"Status: {result['status']}")
print(f"Credit Score: {result['results']['credit']['credit_score']}")
print(f"Interest Rate: {result['results']['credit']['interest_rate']}%")
```

### Asynchronous Usage (Advanced)

```python
import asyncio
from complete_orchestrator import LoanOrchestratorV2

async def process_multiple_applications():
    orchestrator = LoanOrchestratorV2()
    
    applications = [
        {
            "id": "APP-101",
            "info": {...},
            "docs": {...}
        },
        {
            "id": "APP-102",
            "info": {...},
            "docs": {...}
        }
    ]
    
    # Process in parallel
    tasks = [
        orchestrator.process_complete_application(
            app["id"],
            app["info"],
            app["docs"]
        )
        for app in applications
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# Run
results = asyncio.run(process_multiple_applications())
```

## 🌐 REST API Integration

### Using FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from orchestrator_sync import SyncOrchestrator, create_application_request

app = FastAPI()
orchestrator = SyncOrchestrator()

class LoanApplicationRequest(BaseModel):
    application_id: str
    applicant_name: str
    applicant_email: str
    applicant_phone: str
    annual_income: float
    loan_amount: float
    loan_tenure_months: int

@app.post("/api/loan/apply")
async def apply_for_loan(request: LoanApplicationRequest):
    """Submit a loan application."""
    try:
        # Create applicant from request
        from orchestrator_sync import create_applicant, create_documents
        
        applicant = create_applicant(
            name=request.applicant_name,
            email=request.applicant_email,
            phone=request.applicant_phone,
            date_of_birth="1990-01-01",  # Collect from request
            address="",  # Collect from request
            city="",
            state="",
            pincode="",
            employment_status="salaried",
            annual_income=request.annual_income,
            current_employer="",
            designation="",
            years_at_current_employer=0
        )
        
        # Create empty documents (would be uploaded separately)
        documents = create_documents()
        
        # Create application request
        app_request = create_application_request(
            application_id=request.application_id,
            applicant_info=applicant,
            documents=documents,
            loan_amount=request.loan_amount,
            loan_tenure_months=request.loan_tenure_months
        )
        
        # Process
        result = orchestrator.process_application(app_request)
        
        return {
            "status": "success",
            "application_id": request.application_id,
            "result": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/loan/status/{application_id}")
async def get_application_status(application_id: str):
    """Get application status."""
    status = orchestrator.get_application_details(application_id)
    return status
```

### Using Flask

```python
from flask import Flask, request, jsonify
from orchestrator_sync import SyncOrchestrator

app = Flask(__name__)
orchestrator = SyncOrchestrator()

@app.route('/api/loan/apply', methods=['POST'])
def apply_for_loan():
    """Submit a loan application."""
    try:
        data = request.json
        
        # Process application
        result = orchestrator.process_application(
            # Build application request from data
        )
        
        return jsonify({
            "status": "success",
            "result": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/loan/status/<application_id>', methods=['GET'])
def get_status(application_id):
    """Get application status."""
    status = orchestrator.get_application_details(application_id)
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True)
```

## 📦 Batch Processing

### Process Multiple Applications

```python
import json
from orchestrator_sync import SyncOrchestrator

def process_batch(batch_file):
    """Process batch of applications."""
    with open(batch_file, 'r') as f:
        applications = json.load(f)
    
    orchestrator = SyncOrchestrator()
    results = []
    
    for app_config in applications:
        try:
            result = orchestrator.process_application(app_config)
            results.append({
                "application_id": app_config["application_id"],
                "status": "completed",
                "result": result
            })
        except Exception as e:
            results.append({
                "application_id": app_config["application_id"],
                "status": "failed",
                "error": str(e)
            })
    
    # Save results
    with open("batch_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

# Run
results = process_batch("batch_applications.json")
print(f"Processed {len(results)} applications")
```

### Batch Configuration File (`batch_applications.json`)

```json
[
  {
    "application_id": "BATCH-001",
    "applicant_info": {...},
    "documents": {...}
  },
  {
    "application_id": "BATCH-002",
    "applicant_info": {...},
    "documents": {...}
  }
]
```

## 🔍 Monitoring and Logging

### Enable Debug Logging

```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Starting application processing")
```

### Monitor Agent Health Periodically

```python
import asyncio
import logging
from complete_orchestrator import LoanOrchestratorV2

async def monitor_agents():
    """Monitor agent health every 5 minutes."""
    orchestrator = LoanOrchestratorV2()
    
    while True:
        health = await orchestrator.check_all_agents_health()
        
        for agent, is_healthy in health.items():
            status = "✅ UP" if is_healthy else "❌ DOWN"
            logging.info(f"{agent}: {status}")
        
        await asyncio.sleep(300)  # Check every 5 minutes

# Run in background
asyncio.run(monitor_agents())
```

## 📊 Analyzing Results

### Extract Credit Score

```python
def get_credit_decision(result):
    """Get credit decision from processing result."""
    if result['status'] != 'completed':
        return "Processing failed"
    
    credit_result = result['results']['credit']
    score = credit_result['credit_score']
    risk = credit_result['risk_level']
    recommended_amount = credit_result['recommended_loan_amount']
    interest_rate = credit_result['interest_rate']
    
    return {
        "approved": risk == "Low",
        "credit_score": score,
        "risk_level": risk,
        "max_loan_amount": recommended_amount,
        "interest_rate": interest_rate
    }

decision = get_credit_decision(result)
print(f"Approval: {'✅ APPROVED' if decision['approved'] else '❌ REJECTED'}")
print(f"Credit Score: {decision['credit_score']}")
print(f"Interest Rate: {decision['interest_rate']}%")
```

### Compare Income Sources

```python
def compare_income(result):
    """Compare income from payslip vs bank statement."""
    income = result['results']['income']
    
    payslip_income = income['payslip']['annual_salary']
    bank_income = income['bank_statement']['transaction_volume'] / 12
    
    return {
        "payslip_annual": payslip_income,
        "bank_monthly_avg": bank_income,
        "consistency": abs(payslip_income - (bank_income * 12)) / payslip_income < 0.1
    }

income_comparison = compare_income(result)
print(f"Payslip Income: ₹{income_comparison['payslip_annual']:,.0f}")
print(f"Bank Statement Income: ₹{income_comparison['bank_monthly_avg']:,.0f}/month")
print(f"Consistent: {income_comparison['consistency']}")
```

## 🛠️ Troubleshooting

### Agents Not Starting

```bash
# Check if ports are in use
lsof -i :8001-8006

# Kill existing processes
pkill -f "python main.py"

# Start fresh
docker-compose down
docker-compose up -d
```

### Invalid Configuration

```python
# Validate configuration before processing
from orchestrator_sync import ApplicationRequest

try:
    app_request = ApplicationRequest(...)
    # If this succeeds, config is valid
except Exception as e:
    print(f"Invalid configuration: {e}")
```

### Debugging Agent Failures

```python
# Enable verbose logging
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Check individual agent responses
orchestrator = SyncOrchestrator()
health = orchestrator.check_agent_health()

for agent, status in health.items():
    if not status:
        print(f"⚠️  {agent} is not responding!")
```

## 📚 Next Steps

1. **Read**: [ORCHESTRATOR_GUIDE.md](./ORCHESTRATOR_GUIDE.md) for detailed documentation
2. **Explore**: Agent-specific documentation in `agents/*/README.md`
3. **Customize**: Modify `OrchestratorConfig` for your use case
4. **Integrate**: Use in your application with provided examples
5. **Monitor**: Set up logging and health checks

## ✅ Checklist

- [ ] All services running (`orchestrator_cli.py health`)
- [ ] Configuration file prepared
- [ ] Example application processed
- [ ] Results analyzed
- [ ] Integration with your system

## 📞 Support

For issues and questions:
1. Check logs: `docker-compose logs <service>`
2. Verify configuration files
3. Ensure all agents are healthy
4. Check example configurations

Happy processing! 🎉
