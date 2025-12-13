# ✅ Installation Complete!

You've successfully installed all dependencies.

---

## 🎯 NEXT: Start the Services

You need **8 new terminal windows**. Open them and run these commands:

### Terminal 1: Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### Terminal 2: Intake Agent
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/intake_agent"
python main.py
```

### Terminal 3: KYC Agent
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/kyc_agent"
python main.py
```

### Terminal 4: Face Agent
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/face-agent"
python main.py
```

### Terminal 5: Payslip Agent
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/payslip-agent"
python main.py
```

### Terminal 6: Bank Agent
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/bank-agent"
python main.py
```

### Terminal 7: Credit Agent
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent/agents/credit-agent"
python main.py
```

### Terminal 8: API Server
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
python run_orchestrator_server.py
```

---

## ✅ When All Running

Each should show something like:
```
INFO:     Uvicorn running on http://0.0.0.0:PORT
```

Then verify in new terminal:
```bash
curl http://localhost:8000/health
```

---

## 📝 Submit Data

Open browser → **http://localhost:8000/docs**

Or use curl:
```bash
curl -X POST "http://localhost:8000/process-application" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_info": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+91-9123456789",
      "annual_income": 1500000,
      "current_employer": "Tech Company",
      "designation": "Manager",
      "years_at_current_employer": 3,
      "loan_amount_requested": 1000000,
      "loan_tenure_months": 60
    }
  }'
```

---

**Ready? Start with Terminal 1 (Redis)!**
