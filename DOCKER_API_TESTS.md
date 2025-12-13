# Docker System - API Test Examples

## Overview

This document provides curl commands and examples for testing the complete Docker-deployed multi-agent loan system.

## Prerequisites

All services must be running and healthy:

```bash
docker-compose ps
# Expected: All 7 services showing "Up (healthy)"

# Quick test
curl http://localhost:8001/health  # Should return 200 OK
```

## 1. Health Check Endpoints

### Test All Services

```bash
#!/bin/bash
# test_health.sh

echo "Testing service health..."

services=(
  "Intake:8001"
  "KYC:8002"
  "Face:8003"
  "Payslip:8004"
  "Bank:8005"
  "Credit:8006"
  "Orchestrator:9000"
)

for service in "${services[@]}"; do
  name="${service%:*}"
  port="${service#*:}"
  
  if curl -s http://localhost:$port/health > /dev/null 2>&1; then
    echo "✓ $name (port $port) - OK"
  else
    echo "✗ $name (port $port) - FAILED"
  fi
done
```

Run:
```bash
bash test_health.sh
```

## 2. Intake Agent Tests

### 2.1 Start New Conversation

```bash
curl -X POST http://localhost:8001/start \
  -H "Content-Type: application/json" \
  -d '{}' \
  | jq '.'
```

**Response:**
```json
{
  "conversation_id": "conv_abc123",
  "status": "pending",
  "message": "Please provide personal information"
}
```

### 2.2 Get Conversation History

```bash
CONVERSATION_ID="conv_abc123"

curl -X GET "http://localhost:8001/conversation/$CONVERSATION_ID" \
  -H "Content-Type: application/json" \
  | jq '.'
```

### 2.3 Submit Personal Information

```bash
curl -X POST http://localhost:8001/personal_info \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123",
    "name": "Nithin J",
    "email": "nithin@example.com",
    "phone": "9876543210",
    "dob": "1993-05-15",
    "address": "123 Main St"
  }' \
  | jq '.'
```

### 2.4 Check Stored Data

```bash
# From inside container
docker-compose exec intake \
  cat /app/data/conversations/conv_abc123/conversation.json | jq '.'
```

## 3. KYC Agent Tests

### 3.1 Parse PAN Document

```bash
curl -X POST http://localhost:8002/kyc/parse \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-001",
    "evidence_id": "KYC-001",
    "file_uri": "/app/uploads/nithinofPAN.jpeg"
  }' \
  | jq '.'
```

**Expected Response:**
```json
{
  "application_id": "APP-001",
  "evidence_id": "KYC-001",
  "status": "verified",
  "extracted_data": {
    "pan_number": "DIJPN7537R",
    "name": "NITHIN J",
    "father_name": "...",
    "dob": "25/01/2006"
  },
  "confidence": 0.95,
  "verified": true
}
```

### 3.2 Validate Extracted Data

```bash
curl -X POST http://localhost:8002/kyc/validate \
  -H "Content-Type: application/json" \
  -d '{
    "pan_number": "DIJPN7537R",
    "name": "NITHIN J",
    "dob": "25/01/2006"
  }' \
  | jq '.'
```

## 4. Face Agent Tests

### 4.1 Verify Face

```bash
curl -X POST http://localhost:8003/face/verify \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-001",
    "evidence_id": "FACE-001",
    "selfie_uri": "/app/uploads/selfie.jpg",
    "document_face_uri": "/app/uploads/pan_photo.jpg"
  }' \
  | jq '.'
```

**Expected Response:**
```json
{
  "application_id": "APP-001",
  "evidence_id": "FACE-001",
  "match_confidence": 0.92,
  "verified": true,
  "status": "verified"
}
```

## 5. Payslip Agent Tests

### 5.1 Extract Income from Payslip

```bash
curl -X POST http://localhost:8004/extract \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-001",
    "evidence_id": "PAYSLIP-001",
    "file_uri": "/app/uploads/payslip_dec2024.pdf"
  }' \
  | jq '.'
```

**Expected Response:**
```json
{
  "application_id": "APP-001",
  "evidence_id": "PAYSLIP-001",
  "status": "success",
  "extracted_data": {
    "salary": 50000,
    "year": 2024,
    "month": "December",
    "hra": 10000,
    "dearness_allowance": 5000,
    "bonus": 0
  }
}
```

## 6. Bank Agent Tests

### 6.1 Parse Bank Statement

```bash
curl -X POST http://localhost:8005/bank/parse \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-001",
    "evidence_id": "BANK-001",
    "file_uri": "/app/bank-statement/bank_transactions_ACC1001.csv"
  }' \
  | jq '.'
```

**Expected Response:**
```json
{
  "application_id": "APP-001",
  "evidence_id": "BANK-001",
  "status": "success",
  "analysis": {
    "account_type": "savings",
    "total_transactions": 24,
    "analysis_period_months": 2,
    "average_salary": 41851.72,
    "salary_frequency": "monthly",
    "salary_detected": true,
    "salary_consistency": "stable"
  }
}
```

### 6.2 Test from Inside Docker Network

```bash
# Uses internal service name
docker-compose exec bank \
  curl -X POST http://bank:8000/bank/parse \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-001",
    "evidence_id": "BANK-001",
    "file_uri": "/app/bank-statement/bank_transactions_ACC1001.csv"
  }' | jq '.'
```

## 7. Credit Agent Tests

### 7.1 Calculate Credit Score

```bash
curl -X POST http://localhost:8006/score \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-001",
    "applicant_name": "Nithin J",
    "annual_salary": 500000,
    "cibil_score": 750,
    "existing_emi": 10000,
    "average_bank_balance": 100000,
    "employment_type": "salaried"
  }' \
  | jq '.'
```

**Expected Response:**
```json
{
  "application_id": "APP-001",
  "credit_score": 745,
  "probability_of_default": 0.0030,
  "risk_level": "LOW",
  "recommended_action": "APPROVE",
  "confidence": 0.95,
  "details": {
    "salary_stability": 0.9,
    "debt_to_income_ratio": 0.02,
    "historical_payment": 0.95,
    "bureau_score_weight": 0.85
  }
}
```

## 8. Orchestrator Agent Tests

### 8.1 Start Complete Application

```bash
curl -X POST http://localhost:9000/start \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_name": "Nithin J",
    "email": "nithin@example.com",
    "phone": "9876543210"
  }' \
  | jq '.'
```

**Response:**
```json
{
  "orchestration_id": "orch_xyz789",
  "status": "started",
  "steps": [
    "intake",
    "kyc",
    "face_verification",
    "payslip_analysis",
    "bank_analysis",
    "credit_scoring"
  ]
}
```

### 8.2 Check Orchestration Status

```bash
ORCHESTRATION_ID="orch_xyz789"

curl -X GET "http://localhost:9000/status/$ORCHESTRATION_ID" \
  -H "Content-Type: application/json" \
  | jq '.'
```

**Response:**
```json
{
  "orchestration_id": "orch_xyz789",
  "status": "in_progress",
  "current_step": "bank_analysis",
  "completed_steps": ["intake", "kyc", "face_verification"],
  "progress_percentage": 60,
  "estimated_remaining_seconds": 30,
  "results": {
    "kyc": {
      "status": "verified",
      "pan": "DIJPN7537R"
    },
    "face": {
      "status": "verified",
      "confidence": 0.92
    }
  }
}
```

### 8.3 Get Final Decision

```bash
curl -X GET "http://localhost:9000/decision/$ORCHESTRATION_ID" \
  -H "Content-Type: application/json" \
  | jq '.'
```

**Response:**
```json
{
  "orchestration_id": "orch_xyz789",
  "status": "completed",
  "final_decision": "APPROVED",
  "summary": {
    "kyc_status": "verified",
    "face_verification": "passed",
    "salary_detected": 41851.72,
    "credit_risk": "LOW",
    "credit_score": 745
  },
  "approved_amount": 500000,
  "tenure_months": 60,
  "interest_rate": 9.5,
  "emi": 10526
}
```

## 9. Integration Tests

### 9.1 Complete End-to-End Flow

```bash
#!/bin/bash
# complete_e2e_test.sh

echo "=== Starting Complete End-to-End Test ==="

# 1. Start intake
echo "1. Starting intake conversation..."
RESPONSE=$(curl -s -X POST http://localhost:8001/start \
  -H "Content-Type: application/json" \
  -d '{}')

CONVERSATION_ID=$(echo $RESPONSE | jq -r '.conversation_id')
echo "✓ Conversation started: $CONVERSATION_ID"

# 2. Submit personal info
echo "2. Submitting personal information..."
curl -s -X POST http://localhost:8001/personal_info \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONVERSATION_ID\",
    \"name\": \"Nithin J\",
    \"email\": \"nithin@example.com\",
    \"phone\": \"9876543210\",
    \"dob\": \"1993-05-15\"
  }" > /dev/null
echo "✓ Personal info submitted"

# 3. Extract KYC
echo "3. Processing KYC document..."
KYC_RESPONSE=$(curl -s -X POST http://localhost:8002/kyc/parse \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-001",
    "evidence_id": "KYC-001",
    "file_uri": "/app/uploads/nithinofPAN.jpeg"
  }')

PAN=$(echo $KYC_RESPONSE | jq -r '.extracted_data.pan_number')
echo "✓ PAN extracted: $PAN"

# 4. Parse bank statement
echo "4. Analyzing bank statement..."
BANK_RESPONSE=$(curl -s -X POST http://localhost:8005/bank/parse \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-001",
    "evidence_id": "BANK-001",
    "file_uri": "/app/bank-statement/bank_transactions_ACC1001.csv"
  }')

SALARY=$(echo $BANK_RESPONSE | jq -r '.analysis.average_salary')
echo "✓ Average salary detected: ₹$SALARY"

# 5. Calculate credit score
echo "5. Calculating credit score..."
CREDIT_RESPONSE=$(curl -s -X POST http://localhost:8006/score \
  -H "Content-Type: application/json" \
  -d "{
    \"application_id\": \"APP-001\",
    \"applicant_name\": \"Nithin J\",
    \"annual_salary\": $(echo \"$SALARY * 12\" | bc | cut -d. -f1),
    \"cibil_score\": 750,
    \"existing_emi\": 10000,
    \"average_bank_balance\": 100000,
    \"employment_type\": \"salaried\"
  }")

CREDIT_SCORE=$(echo $CREDIT_RESPONSE | jq -r '.credit_score')
DECISION=$(echo $CREDIT_RESPONSE | jq -r '.recommended_action')
echo "✓ Credit score: $CREDIT_SCORE - Decision: $DECISION"

echo ""
echo "=== End-to-End Test Complete ==="
echo "Summary:"
echo "  Conversation: $CONVERSATION_ID"
echo "  PAN: $PAN"
echo "  Salary: ₹$SALARY"
echo "  Credit Score: $CREDIT_SCORE"
echo "  Decision: $DECISION"
```

Run:
```bash
bash complete_e2e_test.sh
```

### 9.2 Parallel Service Testing

```bash
#!/bin/bash
# parallel_test.sh

echo "Testing service parallelization..."

# Test all health endpoints in parallel
(curl -s http://localhost:8001/health && echo "✓ Intake") &
(curl -s http://localhost:8002/health && echo "✓ KYC") &
(curl -s http://localhost:8003/health && echo "✓ Face") &
(curl -s http://localhost:8004/health && echo "✓ Payslip") &
(curl -s http://localhost:8005/health && echo "✓ Bank") &
(curl -s http://localhost:8006/health && echo "✓ Credit") &
(curl -s http://localhost:9000/health && echo "✓ Orchestrator") &

wait

echo "All services responded!"
```

## 10. Performance Testing

### 10.1 Load Test Single Endpoint

```bash
#!/bin/bash
# load_test.sh - Simple load test

PORT=${1:-8001}
REQUESTS=${2:-100}
CONCURRENCY=${3:-10}

echo "Load testing localhost:$PORT with $REQUESTS requests, $CONCURRENCY concurrent..."

ab -n $REQUESTS -c $CONCURRENCY http://localhost:$PORT/health
```

Usage:
```bash
bash load_test.sh 8001 100 10  # Test intake with 100 requests, 10 concurrent
```

### 10.2 Response Time Benchmark

```bash
#!/bin/bash
# benchmark.sh

echo "Benchmarking service response times..."

for port in 8001 8002 8003 8004 8005 8006 9000; do
  echo "Port $port:"
  time curl -s http://localhost:$port/health > /dev/null
done
```

## 11. Docker Network Tests

### 11.1 Test Inter-Service Communication

```bash
# From orchestrator to other services
docker-compose exec orchestrator bash << 'EOF'

echo "Testing inter-service communication..."

services=("intake:8000" "kyc:8000" "bank:8000" "credit:8000")

for service in "${services[@]}"; do
  if curl -s http://$service/health > /dev/null; then
    echo "✓ http://$service/health"
  else
    echo "✗ http://$service/health"
  fi
done

EOF
```

### 11.2 Check Network Isolation

```bash
# Verify services can only communicate via network
docker network inspect loan-agent-network | jq '.Containers'
```

## 12. Data Verification Tests

### 12.1 Verify Stored Conversations

```bash
#!/bin/bash
# verify_data.sh

echo "Checking stored conversation data..."

docker-compose exec intake bash << 'EOF'

DATA_DIR="/app/data/conversations"

if [ ! -d "$DATA_DIR" ]; then
  echo "✗ Data directory not found"
  exit 1
fi

CONV_COUNT=$(find $DATA_DIR -name "conversation.json" | wc -l)
echo "✓ Found $CONV_COUNT stored conversations"

# Show latest conversation
LATEST=$(find $DATA_DIR -name "conversation.json" -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2-)
echo "Latest conversation:"
cat "$LATEST" | jq '.'

EOF
```

### 12.2 Verify Audit Logs

```bash
# Check audit logs
docker-compose exec kyc ls -la /app/audit/ | head -20
docker-compose exec credit ls -la /app/audit/ | head -20
```

## Troubleshooting Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Success ✓ |
| 201 | Created | Resource created ✓ |
| 400 | Bad Request | Check JSON format |
| 401 | Unauthorized | Check authentication |
| 404 | Not Found | Check endpoint URL |
| 500 | Server Error | Check service logs |
| 503 | Unavailable | Service not ready |

## Quick Reference

```bash
# Check all endpoints are responding
for port in 8001 8002 8003 8004 8005 8006 9000; do
  curl -I http://localhost:$port/health 2>/dev/null | head -1
done

# View real-time logs while testing
docker-compose logs -f

# Run a simple test
curl -s http://localhost:8001/health | jq '.'

# Full end-to-end automated test
bash complete_e2e_test.sh
```

## Environment Variables Available

Inside containers:
```bash
docker-compose exec intake env | grep -E "INTAKE|KYC|BANK|CREDIT"
```

Expected:
```
INTAKE_URL=http://intake:8000
KYC_URL=http://kyc:8000
FACE_URL=http://face:8000
PAYSLIP_URL=http://payslip:8000
BANK_URL=http://bank:8000
CREDIT_URL=http://credit:8000
```

---

**Note:** Replace `localhost` with the Docker service name when testing from inside containers (e.g., `http://intake:8000` instead of `http://localhost:8001`)

**Test Success Indicators:**
- ✓ All health endpoints return 200 OK
- ✓ Services can reach each other via Docker network
- ✓ Data is persisted to volumes
- ✓ Orchestrator successfully chains all services
- ✓ Final decision is returned with all required fields
