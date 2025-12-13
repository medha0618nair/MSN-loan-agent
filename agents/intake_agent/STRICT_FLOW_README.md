# Intake Agent - Strict Conversational Flow

## Overview

The updated Intake Agent implements a **strict sequential conversation flow** where users answer exactly 13 required questions in a predefined order.

**Key Features:**
- ✅ Strict sequential ordering (no skipping questions)
- ✅ Validation at each step
- ✅ Persistent state (resume on restart)
- ✅ Conditional questions (e.g., employer only for salaried)
- ✅ Clear error messages with retry logic

---

## Conversation Flow (13 Questions)

### Phase 1: Personal Information (5 questions)

1. **loan_type** (Required)
   - Question: "What type of loan would you like to apply for? (personal/home/auto/education)"
   - Validates: One of [personal, home, auto, education]
   - Example: `personal`

2. **full_name** (Required)
   - Question: "Great — what is your full name?"
   - Validates: At least 2 characters, letters and spaces only
   - Example: `John Doe`

3. **date_of_birth** (Required)
   - Question: "What is your date of birth? (YYYY-MM-DD)"
   - Validates: Valid date format, age 18-100
   - Example: `1990-05-15`

4. **phone** (Required)
   - Question: "What is your phone number?"
   - Validates: 10-digit format or with country code
   - Example: `9876543210`

5. **email** (Required)
   - Question: "What is your email address?"
   - Validates: Valid email format
   - Example: `john@example.com`

### Phase 2: Identity & Employment (8 questions)

6. **pan** (Required)
   - Question: "What is your PAN?"
   - Validates: Format AAAAA9999A
   - Example: `ABCDE1234F`

7. **employment_type** (Required)
   - Question: "What is your employment type? (salaried/self-employed/student)"
   - Validates: One of [salaried, self-employed, student]
   - Example: `salaried`

8. **employer_name** (Conditional - Only if employment_type == "salaried")
   - Question: "Who is your current employer?"
   - Validates: At least 2 characters
   - Example: `TechCorp Inc`

9. **designation** (Conditional - Only if employment_type == "salaried")
   - Question: "What is your job designation?"
   - Validates: At least 2 characters
   - Example: `Senior Developer`

10. **years_at_job** (Required)
    - Question: "How many years have you been in your current job?"
    - Validates: Number 0-70
    - Example: `5`

### Phase 3: Financial Information (2 questions)

11. **monthly_income** (Required)
    - Question: "What is your monthly income?"
    - Validates: Positive number up to 10,000,000
    - Example: `75000`

12. **loan_amount** (Required)
    - Question: "What loan amount are you requesting?"
    - Validates: Positive number up to 50,000,000
    - Example: `500000`

### Phase 4: Loan Terms (1 question)

13. **tenure_months** (Required)
    - Question: "For how many months do you want the loan?"
    - Validates: 1-600 months
    - Example: `60`

### Phase 5: Document Uploads (4 Optional)

14. **kyc_document** (Optional)
    - Question: "Please upload your KYC document (Aadhaar/PAN). Type 'skip' to skip."
    - Validates: File path or "skip"

15. **selfie** (Optional)
    - Question: "Please upload a selfie for face verification. Type 'skip' to skip."
    - Validates: File path or "skip"

16. **payslip** (Optional)
    - Question: "Please upload your recent payslip. Type 'skip' to skip."
    - Validates: File path or "skip"

17. **bank_statement** (Optional)
    - Question: "Please upload your bank statement (last 3 months). Type 'skip' to skip."
    - Validates: File path or "skip"

---

## API Endpoints

### 1. POST /start
**Start a new conversation or resume existing one**

```bash
curl -X POST http://localhost:8001/start \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-12345",
    "conversation_id": "conv-xyz"  # optional
  }'
```

Response:
```json
{
  "application_id": "APP-12345",
  "conversation_id": "conv-xyz",
  "bot_message": "What type of loan would you like to apply for? (personal/home/auto/education)",
  "next_question_id": "loan_type",
  "current_question": {
    "id": "loan_type",
    "question": "What type of loan...",
    "field_name": "loan_type",
    "required": true,
    "validator": "validate_loan_type"
  }
}
```

### 2. POST /message
**Send user answer and get next question**

```bash
curl -X POST http://localhost:8001/message \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-12345",
    "user_message": "personal"
  }'
```

Response (if valid):
```json
{
  "application_id": "APP-12345",
  "bot_message": "Great — what is your full name?",
  "next_question_id": "full_name",
  "current_question": { ... },
  "collected_slots": {
    "loan_type": "personal"
  },
  "completed": false,
  "message": "Answer recorded. Next question..."
}
```

Response (if invalid):
```json
{
  "application_id": "APP-12345",
  "bot_message": "❌ Invalid loan type. Please choose from: personal, home, auto, education\n\nWhat type of loan...",
  "next_question_id": "loan_type",
  "current_question": { ... },
  "collected_slots": {},
  "completed": false,
  "message": "Validation failed, please retry"
}
```

### 3. GET /state/{application_id}
**Get current conversation state**

```bash
curl http://localhost:8001/state/APP-12345
```

### 4. POST /reset/{application_id}
**Reset conversation to start over**

```bash
curl -X POST http://localhost:8001/reset/APP-12345
```

### 5. GET /health
**Health check**

```bash
curl http://localhost:8001/health
```

---

## Running the Agent

### Start the Agent

```bash
cd /Users/apple/Desktop/codered\ final/MSN-loan-agent/agents/intake_agent
python3 main_strict_flow.py
```

The agent will start on `http://0.0.0.0:8001`

### Test with Client

```bash
python3 test_strict_flow.py
```

---

## Key Implementation Details

### Files Created/Modified

1. **chat_flow.py** (NEW)
   - Defines the exact conversation flow
   - Implements validators for each question
   - ConversationFlowManager class handles flow logic

2. **storage.py** (NEW)
   - Persists conversation state to JSON files
   - Resumes conversations on restart
   - Stores message history

3. **main_strict_flow.py** (NEW)
   - FastAPI endpoints for conversation
   - Enforces strict sequential ordering
   - Returns error on validation failures

### Validation Flow

```
User Input
    ↓
Load Current Question
    ↓
Validate Answer
    ↓
Invalid? → Re-ask same question (keep question_id)
    ↓
Valid? → Save answer
    ↓
Get Next Question (considering conditions)
    ↓
Send Next Question
    ↓
Is this the last? → Mark complete
    ↓
Return Response
```

### Conditional Questions

Questions can be conditional based on previous answers:

```python
"employment_type": "salaried" → Ask employer_name and designation
"employment_type": "student" → Skip employer_name and designation
```

### State Persistence

After every answer, state is saved:

```json
{
  "application_id": "APP-12345",
  "conversation_id": "conv-xyz",
  "current_question_id": "full_name",
  "collected_slots": {
    "loan_type": "personal"
  },
  "completed": false,
  "messages": [
    {"role": "bot", "content": "...", "timestamp": "..."},
    {"role": "user", "content": "personal", "timestamp": "..."}
  ]
}
```

If user restarts, they resume from `current_question_id`.

---

## Validators

Each question has a dedicated validator:

| Question | Validator | Rules |
|----------|-----------|-------|
| loan_type | validate_loan_type | Must be in [personal, home, auto, education] |
| full_name | validate_full_name | 2+ chars, letters/spaces only |
| dob | validate_date_of_birth | Format YYYY-MM-DD, age 18-100 |
| phone | validate_phone | 10 digits or with country code |
| email | validate_email | Valid email format |
| pan | validate_pan | Format AAAAA9999A |
| employment_type | validate_employment_type | One of [salaried, self-employed, student] |
| employer_name | validate_employer_name | 2+ characters |
| designation | validate_designation | 2+ characters |
| years_at_job | validate_years_at_job | Number 0-70 |
| monthly_income | validate_monthly_income | Positive, max 10,000,000 |
| loan_amount | validate_loan_amount | Positive, max 50,000,000 |
| tenure_months | validate_tenure_months | 1-600 months |
| documents | validate_document_upload | File path or "skip" |

---

## Example Conversation

```
Bot: What type of loan would you like to apply for? (personal/home/auto/education)
User: personal

Bot: Great — what is your full name?
User: John Doe

Bot: What is your date of birth? (YYYY-MM-DD)
User: 1990-05-15

Bot: What is your phone number?
User: 9876543210

Bot: What is your email address?
User: john@example.com

Bot: What is your PAN?
User: ABCDE1234F

Bot: What is your employment type? (salaried/self-employed/student)
User: salaried

Bot: Who is your current employer?
User: TechCorp Inc

Bot: What is your job designation?
User: Senior Developer

Bot: How many years have you been in your current job?
User: 5

Bot: What is your monthly income?
User: 75000

Bot: What loan amount are you requesting?
User: 500000

Bot: For how many months do you want the loan?
User: 60

Bot: Please upload your KYC document...
User: skip

Bot: Please upload a selfie...
User: skip

Bot: Please upload your recent payslip...
User: skip

Bot: Please upload your bank statement...
User: skip

Bot: ✅ Your application is complete and ready for verification!
```

---

## Troubleshooting

### Agent not responding
- Check if agent is running on port 8001
- Check logs for errors

### Invalid answer keeps getting rejected
- Make sure you're following the exact format specified
- For dates: Use YYYY-MM-DD format
- For PAN: Use format AAAAA9999A (5 letters, 4 digits, 1 letter)

### Want to reset conversation
```bash
curl -X POST http://localhost:8001/reset/APP-12345
```

Then start again with `/start`

---

## Integration with Orchestrator

The Intake Agent can be called by the master orchestrator:

```python
intake_result = await orchestrator.call_intake_agent({
    "application_id": "APP-001",
    "conversation_id": "conv-123"
})
```

Returns complete conversation state with all collected slots.
