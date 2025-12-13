# 🎼 ORCHESTRATOR WORKFLOW - DEEP DIVE

## What is the Orchestrator?

The **Orchestrator Agent (Port 9000)** is the **master conductor** that:
- Receives the complete loan application
- Coordinates all 5 verification agents
- Executes them in **parallel** for speed
- Merges all results into a single evidence package
- Passes to credit agent for final decision

---

## 🎯 Orchestrator Workflow Steps

### STEP 1: Application Received
```
Orchestrator receives:
├─ application_id: "APP-20251213001122"
├─ applicant_info
│  ├─ name: "Nithin Nair"
│  ├─ age: 30
│  ├─ monthly_income: 500000
│  └─ annual_income: 6000000
├─ loan_request
│  ├─ amount: 3000000
│  ├─ duration: 60 months
│  └─ purpose: "personal"
└─ documents
   ├─ kyc_file: "pancard.png"
   ├─ id_photo: "id.jpg"
   ├─ selfie: "nithin.jpg"
   ├─ payslip: "payslip.pdf"
   └─ bank_statement: "bank.csv"
```

---

### STEP 2: Launch Parallel Agents

```
ORCHESTRATOR LAUNCHES (All at once):
│
├─→ [T=0ms] KYC Agent (8002)
│  └─ Task: Parse PAN document
│  └─ Input: pancard.png
│  └─ Expected Return: Pan number, name, verification status
│
├─→ [T=0ms] Face Agent (8003)
│  └─ Task: Verify face match & liveness
│  └─ Input: id.jpg + nithin.jpg
│  └─ Expected Return: Similarity score, liveness score
│
├─→ [T=0ms] Payslip Agent (8004)
│  └─ Task: Extract income info
│  └─ Input: payslip.pdf
│  └─ Expected Return: Monthly salary, company, designation
│
└─→ [T=0ms] Bank Agent (8005)
   └─ Task: Analyze account
   └─ Input: bank.csv
   └─ Expected Return: Balance, salary detection, health score

⏳ PARALLEL EXECUTION (All happen simultaneously)
   │
   ├─ KYC finishes at T=500ms ✅
   ├─ Face finishes at T=600ms ✅
   ├─ Payslip finishes at T=800ms ✅
   └─ Bank finishes at T=1000ms ✅
```

---

### STEP 3: Collect Results

```
Orchestrator waits for all agents to complete:

Promise.all([
  kycPromise,
  facePromise,
  payslipPromise,
  bankPromise
]) → All results collected
```

---

### STEP 4: Merge Evidence Package

```javascript
MERGED EVIDENCE PACKAGE:
{
  "application_id": "APP-20251213001122",
  "kyc_evidence": {
    "verified": true,
    "pan_number": "AAUPA0055K",
    "name": "Nithin Nair",
    "confidence": 0.98
  },
  "face_evidence": {
    "match_score": 0.9845,
    "liveness_score": 0.9512,
    "is_live": true,
    "is_match": true
  },
  "income_evidence": {
    "monthly_salary": 500000,
    "annual_salary": 6000000,
    "company": "Microsoft India",
    "verified": true,
    "confidence": 0.96
  },
  "bank_evidence": {
    "current_balance": 80602,
    "average_monthly_salary": 475000,
    "delinquency": false,
    "account_health": "good"
  },
  "applicant_info": {
    "name": "Nithin Nair",
    "age": 30,
    "monthly_income": 500000,
    "annual_income": 6000000
  },
  "loan_request": {
    "amount": 3000000,
    "duration_months": 60,
    "purpose": "personal"
  }
}
```

---

### STEP 5: Call Credit Agent

```
Orchestrator sends merged package to Credit Agent (8006):

POST /score
{
  "application_id": "APP-20251213001122",
  "applicant_info": { ... },
  "verification_results": {
    "kyc_status": "verified",
    "face_match": 0.9845,
    "liveness_score": 0.9512,
    "salary_verified": true,
    "credit_score": 679,
    "bank_balance": 80602,
    "delinquency": false
  }
}

↓ Credit Agent processes ↓

Returns:
{
  "decision": "APPROVED",
  "credit_score": 679,
  "approval_amount": 3000000,
  "interest_rate": 7.5,
  "monthly_emi": 3856.24,
  "total_repayment": 3084988
}
```

---

### STEP 6: Return Final Result to Frontend

```
Orchestrator returns to frontend:

{
  "application_id": "APP-20251213001122",
  "workflow_status": "completed",
  "final_decision": {
    "status": "APPROVED",
    "amount": 3000000,
    "rate": 7.5,
    "emi": 3856.24,
    "duration": 60
  },
  "all_verifications": {
    "kyc": "✅ PASSED",
    "face": "✅ PASSED",
    "income": "✅ PASSED",
    "bank": "✅ PASSED"
  },
  "total_processing_time_ms": 1500
}
```

---

## ⏱️ TIMING COMPARISON

### Sequential Execution (Without Orchestrator):
```
KYC (500ms) → Face (600ms) → Payslip (800ms) → Bank (1000ms) → Credit (300ms)
= 3200ms TOTAL ❌ SLOW
```

### Parallel Execution (With Orchestrator):
```
MAX(KYC, Face, Payslip, Bank) + Credit
= MAX(500, 600, 800, 1000) + 300
= 1000 + 300
= 1300ms TOTAL ✅ FAST (2.5x faster!)
```

---

## 🔌 API Endpoint Reference

### Orchestrator Health Check
```
GET /health
Response: 200 OK
```

### Process Complete Application
```
POST /orchestrate/process

Request:
{
  "application_id": "APP-20251213001122",
  "applicant_data": { ... },
  "documents": { ... }
}

Response:
{
  "workflow_status": "completed",
  "stages_completed": [...],
  "merged_results": {...},
  "final_decision": {...},
  "processing_time_ms": 1500
}
```

---

**This is the heart of the system! 🎼**
