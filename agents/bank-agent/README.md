# Bank Statement Extraction Agent

A FastAPI microservice that parses CSV bank statements and detects recurring salary credits for credit scoring workflows.

## Overview

This agent:
- Accepts CSV files with transaction data (date, amount, description)
- Detects recurring monthly salary credits using keyword matching and statistical analysis
- Computes income metrics: avg salary, median, payroll consistency, confidence
- Returns structured JSON for downstream credit scoring agents

## API Specification

### Health Check
```bash
curl http://localhost:8003/health
```

**Response:**
```json
{
  "status": "ok",
  "agent": "bank-agent",
  "version": "bank-v1"
}
```

### Parse Bank Statement

**Endpoint:** `POST /bank/parse`

**Request:**
```json
{
  "application_id": "APP-001",
  "evidence_id": "ev-bank-001",
  "file_uri": "./data/APP-001/bank_statement.csv"
}
```

**Expected CSV Format:**
```csv
date,amount,description
2025-09-05,45000,SALARY CREDIT
2025-09-10,-2500,UPI PAYMENT
2025-10-05,45100,SALARY CREDIT
2025-10-12,-3000,BILL PAYMENT
2025-11-05,45000,SALARY CREDIT
```

**Success Response (200):**
```json
{
  "application_id": "APP-001",
  "evidence_id": "ev-bank-001",
  "bank_salary_detected": true,
  "salary_amounts": [45000, 45100, 45000],
  "salary_dates": ["2025-09-05", "2025-10-05", "2025-11-05"],
  "months_salary_detected": 3,
  "avg_salary": 45033.33,
  "median_salary": 45000.0,
  "monthly_income_estimate": 45000.0,
  "payroll_consistency": 0.92,
  "inflow_std": 0.0,
  "salary_share_of_credits": 0.95,
  "confidence": 0.88,
  "agent_version": "bank-v1",
  "ts": "2025-12-12T10:35:00.123456"
}
```

**Error Responses:**
- `404 file_not_found`: File not accessible at specified path
- `400 unsupported_file_type`: File is not a .csv
- `400 invalid_csv_format`: CSV missing required columns or malformed
- `400 no_salary_detected`: No recurring salary credits found

## Setup & Run

### Installation

```bash
cd agents/bank-agent
pip install -r requirements.txt
```

### Upload Your Bank Statement

Place your bank statement CSV file in the `data/` directory:

```
data/
├── APP-001/
│   └── bank_statement.csv
├── APP-002/
│   └── statement.csv
```

### CSV Format Required

Your CSV must have these columns (case-insensitive):
- `date` - Transaction date (YYYY-MM-DD or similar)
- `amount` - Transaction amount (positive = credit, negative = debit)
- `description` - Transaction description (for keyword matching)

**Example:**
```csv
date,amount,description
2025-09-05,45000,SALARY CREDIT
2025-09-10,-2500,UPI PAYMENT
2025-10-05,45100,SALARY CREDIT
2025-10-12,-3000,BILL PAYMENT
2025-11-05,45000,SALARY CREDIT
2025-11-15,-2000,SHOPPING
```

### Start Service

```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8003
```

Service will run on `http://localhost:8003`

### Run Tests

```bash
pytest tests/ -v
```

## Docker

### Build Image

```bash
docker build -t bank-agent:latest .
```

### Run Container

```bash
docker run -d -p 8003:8003 \
  -v $(pwd)/data:/app/data \
  --name bank-agent \
  bank-agent:latest
```

## Example Workflow

### 1. Generate Test Data
```bash
python sample_data/generate_sample_bank.py ./data/APP-001/bank.csv
```

### 2. Parse Statement
```bash
curl -X POST http://localhost:8003/bank/parse \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-001",
    "evidence_id": "ev-bank-001",
    "file_uri": "./data/APP-001/bank.csv"
  }' | python -m json.tool
```

### 3. Response with Salary Metrics
```json
{
  "bank_salary_detected": true,
  "salary_amounts": [45000, 45000, 45000],
  "months_salary_detected": 3,
  "avg_salary": 45000.0,
  "median_salary": 45000.0,
  "monthly_income_estimate": 45000.0,
  "payroll_consistency": 0.94,
  "confidence": 0.89
}
```

## Metrics Explained

| Field | Description |
|-------|-------------|
| `bank_salary_detected` | Whether recurring salary was found (bool) |
| `salary_amounts` | List of detected salary transaction amounts |
| `salary_dates` | ISO dates of salary credits |
| `months_salary_detected` | Number of months with salary credit |
| `avg_salary` | Average salary across months |
| `median_salary` | Median salary (typically used as estimate) |
| `monthly_income_estimate` | Median salary (primary income estimate) |
| `payroll_consistency` | Score 0-1: regularity of salary (recurrence + timing + amount) |
| `inflow_std` | Standard deviation of all positive transactions |
| `salary_share_of_credits` | Salary as % of total credit inflows |
| `confidence` | Overall confidence 0-1: keyword strength + recurrence + variance |

## Salary Detection Logic

1. **Keyword Match:** Checks transaction description for: salary, payroll, sal, credit
2. **Amount Range:** 10,000 - 500,000 INR
3. **Recurrence:** Same amount (±8% tolerance) appears in 2+ months
4. **Consistency Scoring:**
   - Recurrence: 2 months = 0.5, 3+ = 1.0
   - Timing: Day-of-month variance (5th vs 28th = low score)
   - Amount: Coefficient of variation (low CV = high score)

## Architecture

```
bank-agent/
├── main.py              # FastAPI app + /bank/parse endpoint
├── models.py            # Pydantic request/response schemas
├── utils.py             # Salary detection + scoring logic
├── requirements.txt     # Dependencies
├── Dockerfile           # Container image
├── tests/
│   └── test_bank_parser.py  # Unit & integration tests
├── sample_data/
│   └── generate_sample_bank.py  # CSV generator for testing
└── data/                # Runtime data directory
```

## Environment Variables

- `DATA_PATH`: Path to data directory (default: `./data`)

## Error Handling

All errors return JSON with standardized format:
```json
{
  "error": "error_code",
  "detail": "Human readable message",
  "timestamp": "2025-12-12T10:35:00.123456"
}
```

## Logging

All requests logged with `application_id` prefix:
```
[APP-001] Parse request: ev-bank-001
[APP-001] Loading CSV: ./data/APP-001/bank.csv
[APP-001] Parse complete: salary=3 months, confidence=0.88
```

## Version

- Agent Version: `bank-v1`
- FastAPI: 0.104.1
- Python: 3.11+
