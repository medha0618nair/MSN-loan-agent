# 📚 MSN LOAN AGENT - COMPLETE API DOCUMENTATION

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      REACT FRONTEND                         │
│                    (localhost:3002)                          │
└────────────┬────────────────────────────────────────────────┘
             │
             │ HTTP REST Calls
             ▼
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR AGENT (Port 9000)                  │
│    Coordinates workflow & merges agent results              │
└─┬──────────┬──────────┬──────────┬──────────┬───────────────┘
  │          │          │          │          │
  ▼          ▼          ▼          ▼          ▼
┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
│ITA  │  │KYC  │  │Face │  │Pay  │  │Bank │  │Cred │
│8001 │  │8002 │  │8003 │  │8004 │  │8005 │  │8006 │
└─────┘  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘
```

---

## 📡 AGENT ENDPOINTS & PORT MAPPING

| Agent | Port | Purpose | Protocol |
|-------|------|---------|----------|
| **Intake Agent** | 8001 | Conversational data collection | FastAPI |
| **KYC Agent** | 8002 | Identity/PAN verification | FastAPI |
| **Face Agent** | 8003 | Biometric/liveness verification | FastAPI |
| **Payslip Agent** | 8004 | Income verification | FastAPI |
| **Bank Agent** | 8005 | Account/statement analysis | FastAPI |
| **Credit Agent** | 8006 | Final credit decision | FastAPI |
| **Orchestrator Agent** | 9000 | Workflow coordinator | FastAPI |

---

## 🔄 COMPLETE WORKFLOW FLOW

```
START
  │
  ├─→ [1] INTAKE AGENT (Port 8001)
  │   └─ Conversational data collection
  │   └─ User provides: Name, Income, Loan Amount, Duration
  │
  ├─→ [2] PARALLEL VERIFICATION (Agents 8002-8005)
  │   │
  │   ├─→ KYC Agent (8002) - Verify PAN/Identity
  │   │
  │   ├─→ Face Agent (8003) - Verify face match & liveness
  │   │
  │   ├─→ Payslip Agent (8004) - Extract salary info
  │   │
  │   └─→ Bank Agent (8005) - Analyze bank statement
  │
  ├─→ [3] ORCHESTRATOR (Port 9000)
  │   └─ Merges all agent results
  │   └─ Creates evidence package
  │
  ├─→ [4] CREDIT AGENT (Port 8006)
  │   └─ Makes final approval/rejection decision
  │
  └─→ DONE ✅
```

---

---

## 🎯 DETAILED AGENT ENDPOINTS

---

### 1️⃣ INTAKE AGENT (Port 8001)

**Purpose:** Conversational data collection through multi-turn dialogue

#### GET `/health`
**Description:** Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "service": "intake-agent",
  "version": "intake-v1",
  "timestamp": "2025-12-13T10:30:45.123456"
}
```

---

#### POST `/intake/start`
**Description:** Initialize a new loan application

**Request:**
```json
{}
```

**Response:**
```json
{
  "application_id": "APP-20251213001122",
  "current_stage": "initial_greeting",
  "bot_message": "Welcome to loan verification! What type of loan do you need? (personal/home/auto/education)",
  "collected_data": {}
}
```

---

#### POST `/intake/message`
**Description:** Send message to intake agent (conversational flow)

**Request:**
```json
{
  "application_id": "APP-20251213001122",
  "user_message": "I need a personal loan",
  "session_id": "sess-123"
}
```

**Response:**
```json
{
  "application_id": "APP-20251213001122",
  "bot_message": "What is your monthly income?",
  "current_stage": "income_collection",
  "collected_data": {
    "loan_type": "personal",
    "name": null,
    "income": null,
    "loan_amount": null,
    "duration": null
  },
  "completed": false
}
```

---

#### Intake Conversation Flow Example:

```
Stage 1: Loan Type
  Bot: "What type of loan do you need?"
  User: "personal"

Stage 2: Name
  Bot: "What is your name?"
  User: "Nithin Nair"

Stage 3: Monthly Income
  Bot: "What is your monthly income?"
  User: "₹5,00,000"

Stage 4: Loan Amount
  Bot: "What loan amount do you need?"
  User: "₹30,00,000"

Stage 5: Duration
  Bot: "What loan duration? (months)"
  User: "60"

Stage 6: Complete
  Bot: "✅ Information collected! Proceeding to verification..."
  completed: true
```

---

### 2️⃣ KYC AGENT (Port 8002)

**Purpose:** Identity verification via PAN/Aadhaar documents

#### GET `/health`
**Response:**
```json
{
  "status": "ok",
  "service": "kyc-agent"
}
```

---

#### POST `/kyc/parse`
**Description:** Upload and verify identity document (PAN/Aadhaar/Passport)

**Request (FormData):**
```
POST /kyc/parse

Headers:
  Content-Type: multipart/form-data

Body:
  kyc_file: <binary image file>
  application_id: "APP-20251213001122"
  doc_type: "pan"  // Options: pan, aadhaar, passport
  doc_id: "kyc-doc-001"
```

**Response:**
```json
{
  "application_id": "APP-20251213001122",
  "doc_type": "pan",
  "extracted_info": {
    "pan_number": "AAUPA0055K",
    "name": "Nithin Nair",
    "dob": "1995-05-15",
    "status": "authentic"
  },
  "verification_result": {
    "is_valid": true,
    "checksum_valid": true,
    "format_valid": true,
    "confidence": 0.98
  },
  "message": "✅ PAN document verified successfully"
}
```

---

### 3️⃣ FACE AGENT (Port 8003)

**Purpose:** Biometric face verification and liveness detection

#### GET `/health`
**Response:**
```json
{
  "status": "healthy",
  "version": "face-v1",
  "timestamp": "2025-12-13T10:30:45"
}
```

---

#### POST `/face/verify`
**Description:** Verify face match between ID photo and live selfie

**Request (FormData):**
```
POST /face/verify

Headers:
  Content-Type: multipart/form-data

Body:
  id_crop: <binary image - face from ID>
  selfie: <binary image - live selfie>
  application_id: "APP-20251213001122"
  subject_id: "subject-001"
```

**Response:**
```json
{
  "application_id": "APP-20251213001122",
  "similarity": 0.9845,
  "similarity_metric": "cosine",
  "liveness_score": 0.9512,
  "is_live": true,
  "is_match": true,
  "face_detected_id": true,
  "face_detected_selfie": true,
  "spoof_detected": false,
  "confidence_level": "high",
  "message": "✅ Face match verified! Liveness confirmed.",
  "timestamp": "2025-12-13T10:31:45"
}
```

---

### 4️⃣ PAYSLIP AGENT (Port 8004)

**Purpose:** Income verification through payslip analysis

#### GET `/health`
**Response:**
```json
{
  "status": "healthy",
  "service": "payslip-income-verification-agent",
  "version": "payslip-v1"
}
```

---

#### POST `/payslip/verify`
**Description:** Upload payslip for income extraction

**Request (FormData):**
```
POST /payslip/verify

Headers:
  Content-Type: multipart/form-data

Body:
  payslip_file: <binary file - PDF/PNG/JPG>
  application_id: "APP-20251213001122"
```

**Response:**
```json
{
  "application_id": "APP-20251213001122",
  "extracted_data": {
    "employee_name": "Nithin Nair",
    "monthly_salary": 500000,
    "gross_annual": 6000000,
    "company": "Microsoft India",
    "designation": "Senior Software Engineer",
    "employee_id": "EMP-12345",
    "pay_period": "2025-11",
    "deductions": 45000,
    "net_salary": 455000
  },
  "verification": {
    "is_valid_payslip": true,
    "salary_consistency": "high",
    "employment_verified": true,
    "confidence": 0.96
  },
  "message": "✅ Income verified! Monthly salary: ₹5,00,000"
}
```

---

#### POST `/payslip/test`
**Description:** Demo endpoint with sample payslip data

**Request:**
```
POST /payslip/test
```

**Response:** Same as `/payslip/verify` with sample data

---

### 5️⃣ BANK AGENT (Port 8005)

**Purpose:** Account analysis and salary detection

#### GET `/health`
**Response:**
```json
{
  "status": "ok",
  "service": "bank-agent"
}
```

---

#### POST `/bank/parse`
**Description:** Upload bank statement CSV for analysis

**Request (FormData):**
```
POST /bank/parse

Headers:
  Content-Type: multipart/form-data

Body:
  bank_file: <binary CSV file>
  application_id: "APP-20251213001122"
  account_id: "ACC1001"
```

**Response:**
```json
{
  "application_id": "APP-20251213001122",
  "account_analysis": {
    "account_id": "ACC1001",
    "current_balance": 80602,
    "statement_period": "2025-06-01 to 2025-11-30",
    "total_inflows": 2850000,
    "total_outflows": 2769398,
    "net_flow": 80602
  },
  "salary_detection": {
    "recurring_salary_detected": true,
    "average_monthly_salary": 475000,
    "salary_frequency": "monthly",
    "salary_deposits": [
      "2025-06-03: ₹42,074.61",
      "2025-10-04: ₹41,628.84",
      "2025-11-04: ₹45,652"
    ],
    "salary_consistency": 0.92
  },
  "financial_health": {
    "delinquency_detected": false,
    "overdraft_instances": 0,
    "average_balance": 45000,
    "expense_ratio": 0.97
  },
  "message": "✅ Bank analysis complete. Salary verified: ₹45,000+ monthly"
}
```

---

### 6️⃣ CREDIT AGENT (Port 8006)

**Purpose:** Final loan decision based on all verification results

#### GET `/health`
**Response:**
```json
{
  "status": "ok",
  "version": "score-v1"
}
```

---

#### GET `/model/info`
**Description:** Get credit scoring model information

**Response:**
```json
{
  "model_version": "1.0.0",
  "training_date": "2025-12-01",
  "feature_list": [
    "income", "dti_ratio", "credit_score", 
    "employment_stability", "kyc_status", "age"
  ],
  "model_type": "gradient_boosting",
  "status": "production"
}
```

---

#### POST `/score`
**Description:** Calculate credit score and make loan decision

**Request:**
```json
{
  "application_id": "APP-20251213001122",
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
  },
  "verification_results": {
    "kyc_status": "verified",
    "kyc_confidence": 0.98,
    "face_match": 0.9845,
    "liveness_score": 0.9512,
    "salary_verified": true,
    "average_salary": 475000,
    "bank_balance": 80602,
    "delinquency": false,
    "credit_score": 679
  }
}
```

**Response:**
```json
{
  "application_id": "APP-20251213001122",
  "decision": "APPROVED",
  "credit_score": 679,
  "risk_score": 2.1,
  "risk_category": "Very Low Risk",
  "approval_amount": 3000000,
  "recommended_amount": 3000000,
  "interest_rate": 7.5,
  "terms": {
    "principal": 3000000,
    "duration_months": 60,
    "monthly_emi": 3856.24,
    "total_interest": 849888,
    "total_repayment": 3084988
  },
  "feature_importance": {
    "income": 0.28,
    "dti_ratio": 0.22,
    "credit_score": 0.18,
    "employment_stability": 0.15,
    "kyc_verification": 0.12,
    "age": 0.05
  },
  "reasoning": "Application approved based on credit profile",
  "timestamp": "2025-12-13T10:35:45"
}
```

---

---

## 🎛️ ORCHESTRATOR AGENT (Port 9000)

**Purpose:** Coordinates workflow, manages state, merges results

#### GET `/health`
**Response:**
```json
{
  "status": "ok",
  "service": "orchestrator-agent"
}
```

---

#### POST `/orchestrate/process`
**Description:** Start complete loan processing workflow

**Request:**
```json
{
  "application_id": "APP-20251213001122",
  "applicant_data": {
    "name": "Nithin Nair",
    "monthly_income": 500000,
    "loan_amount": 3000000,
    "duration": 60
  },
  "documents": {
    "kyc_file": "file_path_or_url",
    "id_photo": "file_path_or_url",
    "selfie": "file_path_or_url",
    "payslip": "file_path_or_url",
    "bank_statement": "file_path_or_url"
  }
}
```

**Response:**
```json
{
  "application_id": "APP-20251213001122",
  "workflow_status": "completed",
  "stages_completed": [
    "intake",
    "kyc_verification",
    "face_verification",
    "income_verification",
    "bank_analysis",
    "credit_decision"
  ],
  "merged_results": {
    "kyc": {
      "verified": true,
      "pan": "AAUPA0055K",
      "confidence": 0.98
    },
    "face": {
      "match_score": 0.9845,
      "liveness": true
    },
    "income": {
      "verified": true,
      "monthly": 475000
    },
    "bank": {
      "account_health": "good",
      "balance": 80602
    }
  },
  "final_decision": {
    "status": "APPROVED",
    "amount": 3000000,
    "rate": 7.5,
    "emi": 3856.24
  },
  "processing_time_ms": 2450
}
```

---

---

## 📊 DATA FLOW DIAGRAM

```
┌─ FRONTEND ─────────────────────────────────────┐
│                                                │
│  1. User starts application                    │
│  2. Answers intake questions                   │
│  3. Uploads documents                          │
│  4. Receives decision                          │
│                                                │
└────────────────┬────────────────────────────────┘
                 │
                 │ REST API Calls
                 ▼
┌─ ORCHESTRATOR (9000) ──────────────────────────┐
│                                                │
│  1. Receives application                       │
│  2. Launches parallel agents                   │
│  3. Waits for all results                      │
│  4. Merges evidence package                    │
│  5. Calls credit decision                      │
│                                                │
└────────┬────────────┬────────────┬─────────────┘
         │            │            │
    Parallel      Parallel     Parallel
    Execution     Execution    Execution
         │            │            │
         ▼            ▼            ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │   KYC   │  │   FACE  │  │PAYSLIP  │
    │ (8002)  │  │ (8003)  │  │ (8004)  │
    └─────────┘  └─────────┘  └─────────┘
         │            │            │
         │ All return to orchestrator
         │            │            │
         └────────┬───┴────────┬────┘
                  │            │
                  ▼            ▼
            ┌──────────┐  ┌──────────┐
            │  BANK    │  │  CREDIT  │
            │ (8005)   │  │ (8006)   │
            └──────────┘  └──────────┘
                  │            │
                  └────┬───────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  FINAL DECISION      │
            │  APPROVED/REJECTED   │
            │  Loan Terms          │
            └──────────────────────┘
```

---

## 🔐 AUTHENTICATION & SECURITY

- **CORS Enabled:** `localhost:3001`, `localhost:3000`, `*`
- **No API Key Required:** All endpoints public (for demo)
- **Content-Type:** `application/json` or `multipart/form-data`
- **Response Format:** All responses are JSON

---

## ⚡ EXAMPLE END-TO-END FLOW

### Step 1: Initialize Application
```bash
curl -X POST http://localhost:8001/intake/start
# Returns: application_id = APP-20251213001122
```

### Step 2: Collect User Info (Multi-turn)
```bash
# Message 1
curl -X POST http://localhost:8001/intake/message \
  -H "Content-Type: application/json" \
  -d '{"application_id": "APP-20251213001122", "user_message": "personal"}'

# Message 2
curl -X POST http://localhost:8001/intake/message \
  -H "Content-Type: application/json" \
  -d '{"application_id": "APP-20251213001122", "user_message": "Nithin"}'

# ... Continue for income, amount, duration ...
```

### Step 3: Upload & Verify Documents (Parallel)
```bash
# KYC
curl -X POST http://localhost:8002/kyc/parse \
  -F "kyc_file=@pancard.png" \
  -F "application_id=APP-20251213001122"

# Face
curl -X POST http://localhost:8003/face/verify \
  -F "id_crop=@pancard.png" \
  -F "selfie=@nithin.jpg" \
  -F "application_id=APP-20251213001122"

# Payslip
curl -X POST http://localhost:8004/payslip/verify \
  -F "payslip_file=@payslip.pdf" \
  -F "application_id=APP-20251213001122"

# Bank
curl -X POST http://localhost:8005/bank/parse \
  -F "bank_file=@bank_statement.csv" \
  -F "application_id=APP-20251213001122"
```

### Step 4: Get Final Decision
```bash
curl -X POST http://localhost:8006/score \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-20251213001122",
    "applicant_info": {...},
    "verification_results": {...}
  }'
# Returns: APPROVED with ₹30,00,000 at 7.5% for 60 months
```

---

## 📈 FRONTEND INTEGRATION CHECKLIST

✅ **To build the frontend, ensure you:**

1. **Call `/intake/start`** to initialize application
2. **Implement chat loop** for `/intake/message` multi-turn dialogue
3. **Implement file upload** components for documents
4. **Call all 5 verification agents** (KYC, Face, Payslip, Bank)
5. **Show real-time progress** (agent status panel)
6. **Display final decision** from credit agent
7. **Handle errors** and retry logic
8. **Show loading states** during processing

---

## 🎯 RESPONSE STATUS CODES

| Code | Meaning | Example |
|------|---------|---------|
| 200 | ✅ Success | Document verified |
| 201 | ✅ Created | Application created |
| 400 | ❌ Bad Request | Invalid file format |
| 404 | ❌ Not Found | Application not found |
| 422 | ❌ Validation Error | Missing required field |
| 500 | ❌ Server Error | Processing failed |

---

**Generated:** 2025-12-13
**Version:** 1.0.0
**Status:** Production Ready ✅
