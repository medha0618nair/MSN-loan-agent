# 🎨 FRONTEND INTEGRATION GUIDE

## Quick Reference for Frontend Developers

### Base URLs (All Running Locally)
```javascript
const API_BASE = {
  INTAKE: 'http://localhost:8001',
  KYC: 'http://localhost:8002',
  FACE: 'http://localhost:8003',
  PAYSLIP: 'http://localhost:8004',
  BANK: 'http://localhost:8005',
  CREDIT: 'http://localhost:8006',
  ORCHESTRATOR: 'http://localhost:9000'
};
```

---

## Step-by-Step Integration

### 1️⃣ Initialize Application
```javascript
async function startLoanApplication() {
  const response = await fetch('http://localhost:8001/intake/start', {
    method: 'POST'
  });
  const data = await response.json();
  
  return {
    applicationId: data.application_id,
    message: data.bot_message,
    stage: data.current_stage
  };
  // Returns: "Welcome to loan verification! What type of loan..."
}
```

### 2️⃣ Conversational Intake (Multi-turn)
```javascript
async function sendMessage(applicationId, userMessage) {
  const response = await fetch('http://localhost:8001/intake/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      application_id: applicationId,
      user_message: userMessage
    })
  });
  
  const data = await response.json();
  
  return {
    botMessage: data.bot_message,
    stage: data.current_stage,
    collectedData: data.collected_data,
    isComplete: data.completed
  };
}

// Usage Flow:
// 1. "personal" → Next question
// 2. "Nithin Nair" → Next question  
// 3. "500000" → Next question
// 4. "3000000" → Next question
// 5. "60" → Completed ✅
```

### 3️⃣ KYC Document Verification
```javascript
async function verifyKYC(applicationId, kycFile) {
  const formData = new FormData();
  formData.append('kyc_file', kycFile);
  formData.append('application_id', applicationId);
  formData.append('doc_type', 'pan'); // or 'aadhaar', 'passport'
  formData.append('doc_id', `kyc-${Date.now()}`);
  
  const response = await fetch('http://localhost:8002/kyc/parse', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  
  return {
    panNumber: data.extracted_info.pan_number,
    name: data.extracted_info.name,
    isValid: data.verification_result.is_valid,
    confidence: data.verification_result.confidence,
    message: data.message
  };
}
```

### 4️⃣ Face Verification (Biometric)
```javascript
async function verifyFace(applicationId, idPhoto, selfie) {
  const formData = new FormData();
  formData.append('id_crop', idPhoto);
  formData.append('selfie', selfie);
  formData.append('application_id', applicationId);
  formData.append('subject_id', `subject-${applicationId}`);
  
  const response = await fetch('http://localhost:8003/face/verify', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  
  return {
    similarity: data.similarity, // 0-1 (0.98 = 98% match)
    liveness: data.liveness_score,
    isLive: data.is_live,
    isMatch: data.is_match,
    confidence: data.confidence_level,
    message: data.message
  };
}
```

### 5️⃣ Payslip Income Verification
```javascript
async function verifyPayslip(applicationId, payslipFile) {
  const formData = new FormData();
  formData.append('payslip_file', payslipFile);
  formData.append('application_id', applicationId);
  
  const response = await fetch('http://localhost:8004/payslip/verify', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  
  return {
    employeeName: data.extracted_data.employee_name,
    monthlySalary: data.extracted_data.monthly_salary,
    company: data.extracted_data.company,
    designation: data.extracted_data.designation,
    isValid: data.verification.is_valid_payslip,
    confidence: data.verification.confidence,
    message: data.message
  };
}
```

### 6️⃣ Bank Statement Analysis
```javascript
async function analyzeBankStatement(applicationId, bankFile, accountId) {
  const formData = new FormData();
  formData.append('bank_file', bankFile);
  formData.append('application_id', applicationId);
  formData.append('account_id', accountId);
  
  const response = await fetch('http://localhost:8005/bank/parse', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  
  return {
    balance: data.account_analysis.current_balance,
    monthlySalary: data.salary_detection.average_monthly_salary,
    salaryFrequency: data.salary_detection.salary_frequency,
    noDelinquency: !data.financial_health.delinquency_detected,
    accountHealth: 'good', // Based on analysis
    message: data.message
  };
}
```

### 7️⃣ Credit Decision (Final)
```javascript
async function getCreditscore(applicationId, verificationResults) {
  const payload = {
    application_id: applicationId,
    applicant_info: {
      name: verificationResults.kyc.name,
      age: 30,
      monthly_income: verificationResults.income.monthly,
      annual_income: verificationResults.income.monthly * 12
    },
    loan_request: {
      amount: 3000000,
      duration_months: 60,
      purpose: 'personal'
    },
    verification_results: {
      kyc_status: 'verified',
      kyc_confidence: verificationResults.kyc.confidence,
      face_match: verificationResults.face.similarity,
      liveness_score: verificationResults.face.liveness,
      salary_verified: verificationResults.payslip.isValid,
      average_salary: verificationResults.payslip.monthlySalary,
      bank_balance: verificationResults.bank.balance,
      delinquency: !verificationResults.bank.noDelinquency,
      credit_score: 679
    }
  };
  
  const response = await fetch('http://localhost:8006/score', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const data = await response.json();
  
  return {
    decision: data.decision, // APPROVED or REJECTED
    creditScore: data.credit_score,
    approvalAmount: data.approval_amount,
    interestRate: data.interest_rate,
    monthlyEMI: data.terms.monthly_emi,
    totalRepayment: data.terms.total_repayment,
    reasoning: data.reasoning
  };
}
```

---

## 🔄 Complete Example: React Component

```jsx
import React, { useState } from 'react';

const LoanApplication = () => {
  const [appId, setAppId] = useState(null);
  const [stage, setStage] = useState('intro');
  const [results, setResults] = useState({});

  // Initialize
  const handleStart = async () => {
    const response = await fetch('http://localhost:8001/intake/start', {
      method: 'POST'
    });
    const data = await response.json();
    setAppId(data.application_id);
    setStage('intake');
  };

  // Intake conversation
  const handleMessage = async (message) => {
    const response = await fetch('http://localhost:8001/intake/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        application_id: appId,
        user_message: message
      })
    });
    const data = await response.json();
    
    if (data.completed) {
      setStage('verification');
      startVerification();
    }
  };

  // Parallel verification
  const startVerification = async () => {
    // All run in parallel
    const [kyc, face, payslip, bank] = await Promise.all([
      fetch('http://localhost:8002/kyc/parse', { /* ... */ }),
      fetch('http://localhost:8003/face/verify', { /* ... */ }),
      fetch('http://localhost:8004/payslip/verify', { /* ... */ }),
      fetch('http://localhost:8005/bank/parse', { /* ... */ })
    ]);
    
    const kycData = await kyc.json();
    const faceData = await face.json();
    const payslipData = await payslip.json();
    const bankData = await bank.json();

    // Get credit decision
    const creditResponse = await fetch('http://localhost:8006/score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        application_id: appId,
        verification_results: {
          kyc_status: kycData.verification_result.is_valid ? 'verified' : 'failed',
          face_match: faceData.similarity,
          salary_verified: payslipData.verification.is_valid_payslip,
          // ... more fields
        }
      })
    });

    const creditData = await creditResponse.json();
    setResults({
      kyc: kycData,
      face: faceData,
      payslip: payslipData,
      bank: bankData,
      credit: creditData
    });
    setStage('complete');
  };

  return (
    <div>
      {stage === 'intro' && (
        <button onClick={handleStart}>Start Application</button>
      )}
      {stage === 'intake' && (
        <ChatInput onSend={handleMessage} />
      )}
      {stage === 'verification' && (
        <VerificationStatus results={results} />
      )}
      {stage === 'complete' && (
        <FinalDecision results={results.credit} />
      )}
    </div>
  );
};

export default LoanApplication;
```

---

## 🐛 Error Handling

```javascript
async function safeApiCall(url, options = {}) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Error at ${url}:`, error);
    return {
      error: error.message,
      fallback: true // Use mock data
    };
  }
}

// Usage
const data = await safeApiCall('http://localhost:8002/kyc/parse', {
  method: 'POST',
  body: formData
});

if (data.fallback) {
  // Use mock response
  console.log('Using fallback mock data');
}
```

---

## 📱 UI/UX Recommendations

### 1. **Multi-step Form**
```
Step 1: Loan Details (Intake)
  └─ Q1: Loan Type
  └─ Q2: Name
  └─ Q3: Income
  └─ Q4: Amount
  └─ Q5: Duration

Step 2: Document Upload
  └─ KYC Document (PAN/Aadhaar)
  └─ ID Photo (for face verification)
  └─ Selfie (for liveness)
  └─ Payslip
  └─ Bank Statement

Step 3: Verification Progress
  └─ KYC Agent: 🔄 Processing → ✅ Verified
  └─ Face Agent: 🔄 Processing → ✅ Verified
  └─ Payslip Agent: 🔄 Processing → ✅ Verified
  └─ Bank Agent: 🔄 Processing → ✅ Verified

Step 4: Final Decision
  └─ Status: ✅ APPROVED
  └─ Amount: ₹30,00,000
  └─ Rate: 7.5% p.a.
  └─ Monthly EMI: ₹3,856.24
```

### 2. **Loading States**
- Show spinner during agent processing
- Display agent names with real-time status
- Show estimated completion time

### 3. **Error Recovery**
- Retry button for failed uploads
- Alternative document options
- Contact support link

---

## 🎯 Testing with cURL

```bash
# 1. Start application
curl -X POST http://localhost:8001/intake/start

# 2. Send message
curl -X POST http://localhost:8001/intake/message \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-123",
    "user_message": "personal"
  }'

# 3. Upload KYC
curl -X POST http://localhost:8002/kyc/parse \
  -F "kyc_file=@pancard.png" \
  -F "application_id=APP-123" \
  -F "doc_type=pan"

# 4. Verify Face
curl -X POST http://localhost:8003/face/verify \
  -F "id_crop=@id.jpg" \
  -F "selfie=@selfie.jpg" \
  -F "application_id=APP-123" \
  -F "subject_id=subject-123"

# 5. Get Credit Score
curl -X POST http://localhost:8006/score \
  -H "Content-Type: application/json" \
  -d '{"application_id": "APP-123", ...}'
```

---

## 📊 Response Time Expectations

| Agent | Processing Time |
|-------|-----------------|
| Intake | Instant (user input) |
| KYC | 500-800ms |
| Face | 600-1000ms |
| Payslip | 800-1200ms |
| Bank | 1000-1500ms |
| Credit | 200-400ms |
| **Total (Parallel)** | **~1500ms** |

---

**Happy Coding! 🚀**
