# Credit Scoring Agent

Production-ready microservice for credit decisioning. Accepts merged evidence from Intake, KYC/OCR, Face, Payslip, Bank, and Fraud agents to produce a credit score, risk tier, and recommended action.

## Features

- **Probability of Default (PD) Scoring**: ML-based with rule-based fallback
- **Risk Tiering**: LOW / MEDIUM / HIGH
- **Decision Support**: APPROVE / REVIEW / REJECT recommendations
- **Feature Engineering**: DTI, LTI, combined confidence scores
- **Audit Logging**: Request/response pairs for compliance
- **Model Metadata**: Version, training date, and feature importance
- **Input Validation**: Strict Pydantic schemas for all requests

## Architecture

```
main.py              # FastAPI app (port 8004)
models.py            # Pydantic schemas
utils.py             # Feature engineering + scoring rules
model.py             # ML model wrapper + fallback logic
tests/test_scoring.py # Comprehensive unit tests
sample_data/         # Example payloads for testing
audit/               # Request/response audit logs
models/              # Trained model artifacts (auto-generated)
```

## Installation

### Prerequisites
- Python 3.9+
- pip

### Setup

```bash
cd agents/credit-agent

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/test_scoring.py -v

# Start service
python main.py
```

The service will initialize a sample trained model on first startup if none exists.

## API Endpoints

### POST /score
Score a credit application.

**Request:**
```json
{
  "application_id": "APP-001",
  "evidence": {
    "intake": {
      "applicant_name": "John Doe",
      "email": "john@example.com",
      "phone": "9876543210",
      "loan_amount": 150000,
      "loan_purpose": "Personal",
      "pan": "DIJPN7537R"
    },
    "kyc": {
      "pan_number": "DIJPN7537R",
      "aadhaar_number": "123456789012",
      "name_extracted": "JOHN DOE",
      "kyc_confidence": 0.95,
      "doc_type": "pan"
    },
    "face": {
      "face_verified": true,
      "match_confidence": 0.92,
      "liveness_score": 0.98
    },
    "payslip": {
      "net_pay_payslip": 45000,
      "gross_pay_payslip": 65000,
      "monthly_income": 45000,
      "income_confidence": 0.85,
      "employment_status": "employed"
    },
    "bank": {
      "median_salary": 44000,
      "avg_salary": 44500,
      "months_salary_detected": 6,
      "payroll_consistency": 0.85,
      "salary_share_of_credits": 0.80,
      "inflow_std": 1200.5,
      "confidence": 0.90,
      "bank_salary_detected": true
    },
    "fraud": {
      "fraud_score": 0.05,
      "reasons": [],
      "suspicious_keywords": []
    }
  },
  "loan_request": {
    "loan_amount": 150000,
    "tenure_months": 24,
    "monthly_emi_estimate": 6750
  },
  "app_metadata": {
    "submission_ts": "2025-12-12T10:00:00Z",
    "source": "web"
  }
}
```

**Response (200 OK):**
```json
{
  "application_id": "APP-001",
  "pd_score": 0.2345,
  "risk_tier": "LOW",
  "recommended_action": "APPROVE",
  "max_eligible_loan": 1080000,
  "recommended_tenure_months": 24,
  "monthly_emi_recommendation": 6750.0,
  "explanation": [
    "median_income_used",
    "low_fraud_score",
    "face_verified",
    "kyc_verified",
    "stable_payroll",
    "long_salary_history"
  ],
  "feature_importances": {
    "income": 0.35,
    "payroll_consistency": 0.25,
    "fraud_score": 0.15,
    "face_confidence": 0.10,
    "kyc_confidence": 0.10,
    "dti": 0.03,
    "tenure": 0.02,
    "other": 0.0
  },
  "confidence": 0.88,
  "agent_version": "score-v1",
  "ts": "2025-12-12T10:01:00Z"
}
```

### GET /model/info
Retrieve model metadata.

**Response (200 OK):**
```json
{
  "model_version": "score-v1",
  "training_date": "2025-12-12T09:30:00Z",
  "feature_list": [
    "dti",
    "income_confidence",
    "payroll_consistency",
    "fraud_score",
    "identity_confidence",
    "months_salary_detected",
    "tenure_months",
    "loan_to_income",
    "income_level_normalized"
  ],
  "model_type": "LightGBM",
  "status": "trained"
}
```

### GET /health
Health check.

**Response (200 OK):**
```json
{
  "status": "ok",
  "version": "score-v1"
}
```

## Error Responses

All errors return JSON:

### 400 Bad Request
```json
{
  "detail": "insufficient_income_evidence"
}
```

Common error details:
- `insufficient_identity_evidence` - KYC/Face confidence < 0.5
- `insufficient_income_evidence` - No payslip or bank salary data
- `missing_fields` - Required fields missing

### 500 Internal Server Error
```json
{
  "detail": "internal_error"
}
```

## Feature Engineering

The agent computes the following features from evidence:

### Income Features
- **monthly_income_estimate**: Median salary (bank, confidence >= 0.6) > net pay (payslip) > avg salary (bank)
- **income_confidence**: Weighted average of bank.confidence, payslip.income_confidence, face.match_confidence
- **dti**: monthly_emi_estimate / monthly_income_estimate
- **loan_to_income**: loan_amount / (monthly_income * tenure_months)

### Stability Features
- **payroll_consistency**: From bank statement recurrence analysis
- **months_salary_detected**: Number of months with recurring salary
- **inflow_std**: Standard deviation of salary amounts

### Identity Features
- **kyc_confidence**: From KYC/OCR extraction
- **face_match_confidence**: From face verification
- **identity_confidence**: Combined KYC + face average

### Risk Features
- **fraud_score**: From fraud detection agent
- **tenure_months**: Loan tenure
- **income_level_normalized**: Normalized to 0-1 relative to 50K baseline

## Decision Logic

### Probability of Default (PD)
- **Formula**: Rule-based logistic or ML model prediction
- **Range**: 0.0 to 1.0 (higher = more default risk)

### Risk Tier Mapping
| PD Score | Risk Tier | Action |
|----------|-----------|--------|
| ≤ 0.30   | LOW       | APPROVE |
| 0.31-0.60| MEDIUM    | REVIEW  |
| > 0.60   | HIGH      | REJECT  |

### Fraud Override
- If fraud_score > 0.8: Action = REJECT (regardless of PD)
- If fraud_score > 0.6: Action = REVIEW (regardless of PD)

### Max Eligible Loan
```
Base LTV = 30 months of income
Max Loan = Base LTV × confidence_factor × stability_factor
```

### Recommended Tenure
- If DTI > 0.4: Reduce tenure by 12 months (min 12)
- If DTI > 0.5: Reduce tenure by 24 months (min 12)
- If DTI < 0.25 and income_confidence >= 0.8: Extend tenure by 12 months (max 84)

## cURL Examples

### Score Good Application
```bash
curl -X POST http://localhost:8004/score \
  -H "Content-Type: application/json" \
  -d @sample_data/sample_good.json
```

### Score Fraud Application
```bash
curl -X POST http://localhost:8004/score \
  -H "Content-Type: application/json" \
  -d @sample_data/sample_fraud.json
```

### Get Model Info
```bash
curl http://localhost:8004/model/info
```

### Health Check
```bash
curl http://localhost:8004/health
```

## Audit Logging

All requests are logged to `audit/audit_<app_id>_<timestamp>.json` with:
- Timestamp of request
- Application ID
- Loan amount and tenure
- Full response (without PII)

Example audit log:
```json
{
  "timestamp": "2025-12-12T10:01:00Z",
  "application_id": "APP-001",
  "request_summary": {
    "loan_amount": 150000,
    "tenure_months": 24
  },
  "response": {
    "pd_score": 0.2345,
    "risk_tier": "LOW",
    "recommended_action": "APPROVE",
    ...
  }
}
```

## Running Tests

```bash
# Run all tests
pytest tests/test_scoring.py -v

# Run specific test class
pytest tests/test_scoring.py::TestScoringRules -v

# Run with coverage
pytest tests/test_scoring.py --cov=. --cov-report=html
```

Test coverage:
- Feature engineering (income selection, confidence calculation, DTI)
- Scoring rules (sufficient evidence, fraud flags, decision mapping)
- Probability calculation (logistic function, default probability)
- Model interface (prediction, feature importances)
- Explanation generation

## Docker

### Build
```bash
docker build -t credit-agent:latest .
```

### Run
```bash
docker run -p 8004:8004 \
  -v $(pwd)/audit:/app/audit \
  -v $(pwd)/models:/app/models \
  credit-agent:latest
```

## Performance

**Response Time Target**: P95 < 300ms for prediction (model in memory)

**Typical Latency**:
- Feature engineering: ~10ms
- Model prediction: ~20ms
- Total: ~40ms average

**Memory**: ~200MB for model + inference

## Security & Privacy

### PII Handling
- Application ID and loan details are logged
- PII (names, PAN, Aadhaar) is NOT stored in audit logs
- Only pointers to evidence documents are logged
- All logs are timestamped for audit trail

### Authentication (Placeholder)
Currently accepts all requests. For production, integrate OAuth2/JWT:

```python
# In main.py, add after CORS middleware:
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/score")
async def score_application(request: CreditScoringRequest, token: HTTPAuthorizationCredentials = Depends(security)):
    # Validate token
    pass
```

## Troubleshooting

### Model not loading
```
WARNING: No trained model found, will use fallback rule-based scoring
```
This is normal. The service auto-trains a sample model on first startup.

### Port already in use
```bash
lsof -i :8004  # Find process
kill -9 <PID>   # Kill process
```

Or change port in `main.py`:
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)  # Use 8005 instead
```

### Insufficient evidence errors
Ensure evidence bundle includes:
1. KYC confidence >= 0.5 OR Face confidence >= 0.5
2. Either bank salary (median_salary + confidence >= 0.6) OR payslip (net_pay_payslip)

## Next Steps

1. **Integrate with Orchestrator**: Call `/score` endpoint with merged evidence
2. **Configure Authentication**: Add OAuth2/JWT in production
3. **Monitor Metrics**: Log PD distribution, approval rates, fraud catch rates
4. **Retrain Model**: Collect actual loan defaults and retrain monthly
5. **A/B Testing**: Compare ML model vs rule-based decisions

## License

Internal - Unisys UIP
