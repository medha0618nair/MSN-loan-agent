# Master Orchestrator - Execution Workflow

## 📋 Sequential Processing Order

The master orchestrator processes loan applications in this **strict sequential order**:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  APPLICATION RECEIVED                               │
│  ├─ Application ID: APP-XXXXX                      │
│  ├─ Applicant Info: Name, Email, Phone, etc       │
│  └─ Documents: Aadhaar, Selfie, Payslip, etc      │
│                                                     │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────▼──────────────┐
        │                          │
        │  1️⃣  INTAKE AGENT (:8001)  │
        │                          │
        │ • Conversational intake  │
        │ • Collect applicant info │
        │ • Validate basic data    │
        │ • Return conversation ID │
        │                          │
        └───────────────┬──────────┘
                        │ Evidence: conversation_id, slots_filled
                        │
        ┌───────────────▼──────────────┐
        │                              │
        │  2️⃣  KYC AGENT (:8002)        │
        │                              │
        │ • Parse identity document   │
        │ • Extract: Name, DOB, PAN   │
        │ • Validate document         │
        │ • Compare with intake data  │
        │ • Return verification score │
        │                              │
        └───────────────┬──────────────┘
                        │ Evidence: kyc_verified, score, extracted_data
                        │
        ┌───────────────▼──────────────┐
        │                              │
        │  3️⃣  FACE AGENT (:8003)       │
        │                              │
        │ • Detect face in image      │
        │ • Check liveness            │
        │ • Match with document photo │
        │ • Return confidence scores  │
        │                              │
        └───────────────┬──────────────┘
                        │ Evidence: face_verified, liveness_score, match_score
                        │
        ┌───────────────▼──────────────┐
        │                              │
        │  4️⃣  PAYSLIP AGENT (:8004)    │
        │                              │
        │ • OCR extraction            │
        │ • Parse salary structure    │
        │ • Extract: Basic, HRA, etc  │
        │ • Calculate annual income   │
        │ • Verify against claimed    │
        │                              │
        └───────────────┬──────────────┘
                        │ Evidence: monthly_salary, annual_salary, deductions
                        │
        ┌───────────────▼──────────────┐
        │                              │
        │  5️⃣  BANK AGENT (:8005)       │
        │                              │
        │ • Parse bank statements     │
        │ • Extract transactions      │
        │ • Calculate average balance │
        │ • Analyze spending patterns │
        │ • Cross-verify income       │
        │ • Return risk indicators    │
        │                              │
        └───────────────┬──────────────┘
                        │ Evidence: avg_balance, transaction_volume, risk_score
                        │
        ┌───────────────▼──────────────┐
        │                              │
        │  6️⃣  CREDIT AGENT (:8006)     │
        │                              │
        │ • Receive all prior evidence │
        │ • Calculate credit score    │
        │ • Assess risk level         │
        │ • Recommend loan amount     │
        │ • Set interest rate         │
        │ • Generate final decision   │
        │                              │
        └───────────────┬──────────────┘
                        │ Evidence: credit_score, risk_level, recommendation
                        │
        ┌───────────────▼──────────────┐
        │                              │
        │  FINAL DECISION              │
        │                              │
        │ Status: APPROVED /           │
        │         REJECTED /            │
        │         MANUAL_REVIEW        │
        │                              │
        │ + Loan Amount               │
        │ + Interest Rate             │
        │ + Tenure                    │
        │ + Complete Evidence Trail   │
        │                              │
        └──────────────────────────────┘
```

## 🔄 Agent Ports and Endpoints

| Order | Agent | Port | Endpoint | Input | Output |
|-------|-------|------|----------|-------|--------|
| 1 | **Intake** | 8001 | `/converse` | Applicant info | Conversation ID, slots |
| 2 | **KYC** | 8002 | `/parse-document` | Document + intake data | Verified info, score |
| 3 | **Face** | 8003 | `/verify-face` | Selfie image | Liveness, match score |
| 4 | **Payslip** | 8004 | `/payslip/verify` | Payslip file | Salary, deductions, income |
| 5 | **Bank** | 8005 | `/parse-bank-statement` | Bank statement + payslip | Balance, transactions, risk |
| 6 | **Credit** | 8006 | `/score-application` | All prior evidence | Score, risk, decision |

## 📊 Data Flow Between Agents

### Stage 1: Intake Output → Stage 2: KYC Input
```json
{
  "conversation_id": "conv-APP-001",
  "applicant_name": "John Doe",
  "applicant_dob": "1990-05-15",
  "slots_filled": ["name", "dob", "phone", "employment"]
}
```

### Stage 2: KYC Output → Stage 3: Face Input
```json
{
  "kyc_verified": true,
  "verification_score": 0.99,
  "extracted_name": "John Doe",
  "extracted_dob": "1990-05-15",
  "name_match": true
}
```

### Stage 3: Face Output → Stage 4: Payslip Input
```json
{
  "face_verified": true,
  "liveness_score": 0.98,
  "match_confidence": 0.97,
  "comparison": "MATCH"
}
```

### Stage 4: Payslip Output → Stage 5: Bank Input
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

### Stage 5: Bank Output → Stage 6: Credit Input
```json
{
  "average_balance": 150000,
  "transaction_volume": 2400000,
  "spending_ratio": 0.45,
  "risk_indicators": ["low_savings", "high_spending"]
}
```

### Stage 6: Credit Output (Final)
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

## ⚠️ Failure Handling

### Critical Stages (Stop on Failure)
- **Intake**: If applicant info cannot be collected → STOP
- **KYC**: If identity cannot be verified → REJECT
- **Face**: If face cannot be verified → REJECT

### Non-Critical Stages (Continue on Failure)
- **Payslip**: If parsing fails → Use default/estimate
- **Bank**: If statement not available → Use payslip income only
- **Credit**: If any agent fails → Use available data

## 🔐 Security & Validation

At each stage:
1. **Input Validation**: Verify all required fields present
2. **Data Sanitization**: Clean and validate data types
3. **Error Handling**: Graceful failure with detailed logging
4. **Audit Trail**: Log all decisions and evidence
5. **Timeout Protection**: 60-second timeout per agent

## 📈 Processing Metrics

- **Total Processing Time**: ~2-3 minutes for typical application
- **Per-Stage Time**:
  - Intake: 10-15 seconds
  - KYC: 10-15 seconds
  - Face: 5-10 seconds
  - Payslip: 15-20 seconds
  - Bank: 20-30 seconds
  - Credit: 10-15 seconds

## 🎯 Success Criteria

Application APPROVED when:
- ✅ KYC verification score > 90%
- ✅ Face verification successful
- ✅ Liveness score > 95%
- ✅ Income verified (payslip & bank agreement)
- ✅ Credit score > 700
- ✅ Risk level = "Low"

Application REJECTED when:
- ❌ KYC verification fails
- ❌ Face verification fails
- ❌ Income cannot be verified
- ❌ Credit score < 600
- ❌ Risk level = "High"

Application MANUAL_REVIEW when:
- ⚠️ Risk level = "Medium"
- ⚠️ Income discrepancy between sources
- ⚠️ Partial data missing

## 🔄 Retry Logic

- **Max Retries**: 2 attempts per agent
- **Retry Condition**: Timeout or network error
- **Backoff**: 2-second delay between retries
- **Permanent Failure**: After 2 retries, mark as failed

## 📝 Logging & Audit

Every stage logs:
- ✓ Stage start time
- ✓ Agent endpoint called
- ✓ Request payload (sanitized)
- ✓ Response time
- ✓ Response status
- ✓ Evidence collected
- ✓ Any errors or warnings

## 🚀 Starting the Orchestrator

```bash
# 1. Start all agent services
docker-compose up -d

# 2. Verify all agents are healthy
python orchestrator_agent.py health

# 3. Process an application
python orchestrator_agent.py process APP-001 config.json

# 4. Get results
python orchestrator_agent.py status APP-001
```

## 📊 Example Complete Flow

```
INPUT:
- Application ID: APP-20240115-001
- Applicant: John Doe (john@example.com)
- Income: 800,000 p.a.
- Loan Request: 500,000

PROCESSING:
Stage 1: Intake → "Conversation started, slots filled: 80%"
Stage 2: KYC → "Identity verified, score: 99%"
Stage 3: Face → "Face matched, liveness: 98%"
Stage 4: Payslip → "Income confirmed: 800,000 p.a."
Stage 5: Bank → "Average balance: 150,000, risk: LOW"
Stage 6: Credit → "Score: 750, Recommended: 600,000"

OUTPUT:
Status: APPROVED ✅
Loan Amount: ₹600,000
Interest Rate: 8.5%
Tenure: 60 months
Processing Time: 2.5 minutes
```

---

This sequential flow ensures complete verification before final approval!
