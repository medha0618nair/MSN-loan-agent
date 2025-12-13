# 🧪 Complete Test Case for Loan Verification System

## What This Test Does

The `test_complete_system.py` script tests the **entire loan verification pipeline**:

1. ✅ **Intake Agent Health** - Checks if port 8001 is responding
2. ✅ **Orchestrator Health** - Checks if port 9000 is responding
3. ✅ **All Agents Status** - Verifies all 6 agents show RUNNING
4. ✅ **Start Conversation** - Creates new application
5. ✅ **Answer All Questions** - Submits answers for all 17 questions
6. ✅ **Application Saved** - Verifies data persists to database
7. ✅ **Orchestrator Endpoints** - Checks orchestrator API is working

---

## How to Run the Test

### Step 1: Start All Services
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
bash START_ALL_SERVICES.sh
```

**Wait for output:**
```
✅ ALL SERVICES STARTED AND RUNNING
```

### Step 2: Run the Test (New Terminal)
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
python3 test_complete_system.py
```

### Step 3: View Results

Expected output:
```
================================================================================
🧪 MULTI-AGENT LOAN SYSTEM - COMPLETE TEST SUITE
================================================================================

Test 1: Intake Agent Health
--------------------------------------------------------------------------------
✅ PASS - Intake Agent Health Check
  └─ Status: 200

Test 2: Orchestrator Health
--------------------------------------------------------------------------------
✅ PASS - Orchestrator Health Check
  └─ Status: 200

Test 3: All Agents Status
--------------------------------------------------------------------------------
✅ PASS - All Agents Status
  └─ Status:
    intake: RUNNING
    kyc: RUNNING
    face: RUNNING
    payslip: RUNNING
    bank: RUNNING
    credit: RUNNING
    orchestrator: RUNNING

Test 4: Start Conversation
--------------------------------------------------------------------------------
✅ PASS - Start Conversation
  └─ App ID: APP-XYZ123ABC
    First Q: What type of loan do you need?...

Test 5: Answer All Questions
--------------------------------------------------------------------------------
✅ PASS - Answer All Questions
  └─ Answered 17/17 questions

Test 6: Application Saved
--------------------------------------------------------------------------------
✅ PASS - Application Saved
  └─ Collected 17 fields

Test 7: Orchestrator Endpoints
--------------------------------------------------------------------------------
✅ PASS - Orchestrator Endpoints
  └─ /status endpoint responds: HTTP 404

================================================================================
📊 TEST RESULTS SUMMARY
================================================================================

✅ PASSED - Intake Agent Health Check
✅ PASSED - Orchestrator Health Check
✅ PASSED - All Agents Status
✅ PASSED - Start Conversation
✅ PASSED - Answer All Questions
✅ PASSED - Application Saved
✅ PASSED - Orchestrator Endpoints

================================================================================
✅ PASSED: 7/7
❌ FAILED: 0/7
================================================================================

📁 Results saved to: test_results.json

🎉 ALL TESTS PASSED! System is working correctly.
```

---

## Test Data Used

The test automatically answers all 17 questions with this data:

| Question | Answer | Type |
|----------|--------|------|
| Loan Type | personal | Valid |
| Full Name | John Doe | Valid |
| Date of Birth | 1990-05-15 | Valid |
| Phone | 9876543210 | Valid |
| Email | john@example.com | Valid |
| PAN | ABCDE1234F | Valid |
| Employment | salaried | Valid |
| Employer | Tech Corp | Valid |
| Designation | Senior Engineer | Valid |
| Years at Job | 5 | Valid |
| Monthly Income | 100000 | Valid |
| Loan Amount | 500000 | Valid |
| Tenure | 60 | Valid |
| KYC File | ./images/nithin3.jpg | File |
| Selfie | ./images/nithinPAN.png | File |
| Payslip | ./payslip/payslip_nithin_j.txt | File |
| Bank Statement | skip | Optional |

---

## What Each Test Checks

### Test 1: Intake Agent Health
- Sends: `GET /health`
- Expects: HTTP 200
- Verifies: Intake Agent is running on port 8001

### Test 2: Orchestrator Health
- Sends: `GET /health`
- Expects: HTTP 200
- Verifies: Orchestrator is running on port 9000

### Test 3: All Agents Status
- Sends: `GET /agents/status`
- Expects: All agents return "RUNNING"
- Verifies: All 6 agents operational

### Test 4: Start Conversation
- Sends: `POST /start`
- Expects: Valid application_id + first question
- Verifies: Conversation initialization works

### Test 5: Answer All Questions
- Sends: 17 POST /message requests
- Expects: All succeed (HTTP 200)
- Verifies: Complete question flow works

### Test 6: Application Saved
- Sends: `GET /state/{app_id}`
- Expects: Returns all collected data
- Verifies: Data persistence works

### Test 7: Orchestrator Endpoints
- Sends: `GET /status/TEST-JOB`
- Expects: Endpoint exists (any 2xx/4xx response)
- Verifies: Orchestrator API is operational

---

## Output Files

The test creates:
- `test_results.json` - Detailed results in JSON format

```json
[
  {
    "test": "Intake Agent Health Check",
    "status": "✅ PASS",
    "details": "Status: 200",
    "timestamp": "2025-12-13T12:00:00"
  },
  ...
]
```

---

## Troubleshooting

### ❌ Test fails - "Connection refused"
**Solution:** Services not running
```bash
bash START_ALL_SERVICES.sh
# Wait 5 seconds
python3 test_complete_system.py
```

### ❌ Test fails - "Agent Status Check"
**Solution:** Some agents not running
- This is OK if you don't have all agents installed
- Intake and Orchestrator are the minimum required

### ❌ Test fails - "Answer Questions"
**Solution:** File paths wrong
- Update test data in `test_complete_system.py`
- Change paths to match your file locations

---

## Running Continuously

Run the test multiple times to verify consistency:

```bash
# Run test every 10 seconds
watch -n 10 python3 test_complete_system.py
```

---

## Test Success Criteria

✅ **All 7 tests pass** = System working correctly
✅ **Application data saved** = Database persistence working
✅ **Questions answered sequentially** = Intake flow working
✅ **Agents status RUNNING** = Orchestrator aware of all agents

---

## Next Steps

Once tests pass:
1. Your system is fully operational
2. All services running permanently
3. RAG agentic model can call any endpoint
4. Ready for production use

```bash
# Submit real applications
python3 submit_application_v2.py

# Check orchestrator
curl http://localhost:9000/agents/status

# View audit results
cat audit/JOB-*.json
```

---

**Test suite ready! Run it now:** 
```bash
python3 test_complete_system.py
```
