"""
Bank Statement Extraction Agent - FastAPI Service.
Parses CSV bank statements and detects recurring salary credits.
"""
import os
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import BankParseRequest, BankParseResponse, HealthResponse
from utils import (
    normalize_amount, parse_date, detect_recurring_salary,
    compute_income_metrics, compute_payroll_consistency, compute_confidence
)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Bank Statement Agent",
    description="Parse CSV bank statements and detect salary credits",
    version="bank-v1"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DATA_PATH = os.getenv("DATA_PATH", "./data")
logger.info(f"Bank Agent initialized, data path: {DATA_PATH}")


def log_with_app_id(app_id: str, message: str, level: str = "info"):
    """Helper to log with application_id prefix."""
    log_msg = f"[{app_id}] {message}"
    if level == "info":
        logger.info(log_msg)
    elif level == "error":
        logger.error(log_msg)
    elif level == "warning":
        logger.warning(log_msg)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@app.post("/bank/parse", response_model=BankParseResponse)
async def parse_bank_statement(request: BankParseRequest):
    """
    Parse bank statement CSV and detect recurring salary credits.
    
    Expected CSV columns (case-insensitive):
    - date
    - amount
    - description
    """
    app_id = request.application_id
    log_with_app_id(app_id, f"Parse request: {request.evidence_id}")
    
    try:
        # Validate file exists
        if not os.path.exists(request.file_uri):
            log_with_app_id(app_id, f"File not found: {request.file_uri}", level="error")
            raise HTTPException(status_code=404, detail="file_not_found")
        
        # Check file type
        file_ext = Path(request.file_uri).suffix.lower()
        if file_ext != ".csv":
            log_with_app_id(app_id, f"Unsupported file type: {file_ext}", level="error")
            raise HTTPException(status_code=400, detail="unsupported_file_type")
        
        # Load CSV
        log_with_app_id(app_id, f"Loading CSV: {request.file_uri}")
        try:
            df = pd.read_csv(request.file_uri)
        except Exception as e:
            log_with_app_id(app_id, f"CSV parse error: {e}", level="error")
            raise HTTPException(status_code=400, detail="invalid_csv_format")
        
        # Normalize column names
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Validate required columns
        required_cols = {"date", "amount", "description"}
        available_cols = set(df.columns)
        
        if not required_cols.issubset(available_cols):
            missing = required_cols - available_cols
            log_with_app_id(app_id, f"Missing columns: {missing}", level="error")
            raise HTTPException(status_code=400, detail="invalid_csv_format")
        
        # Parse transactions
        transactions = []
        for _, row in df.iterrows():
            date_obj, date_ok = parse_date(row["date"])
            if not date_ok:
                continue
            
            amount = normalize_amount(row["amount"])
            description = str(row.get("description", "")).lower()
            
            transactions.append({
                "date": date_obj,
                "amount": amount,
                "description": description,
            })
        
        if not transactions:
            log_with_app_id(app_id, "No valid transactions parsed", level="warning")
            raise HTTPException(status_code=400, detail="invalid_csv_format")
        
        # Detect salary
        salary_txns, salary_metrics = detect_recurring_salary(transactions)
        
        if not salary_metrics.get("bank_salary_detected"):
            log_with_app_id(app_id, "No recurring salary detected", level="warning")
            raise HTTPException(status_code=400, detail="no_salary_detected")
        
        # Compute metrics
        income_metrics = compute_income_metrics(transactions, salary_txns)
        consistency = compute_payroll_consistency(salary_txns)
        
        # Keyword strength (based on description matches)
        keyword_count = sum(1 for t in salary_txns if t["description"])
        keyword_strength = min(keyword_count / len(salary_txns), 1.0) if salary_txns else 0.0
        
        confidence = compute_confidence(salary_txns, salary_metrics, keyword_strength)
        
        # Build response
        response = BankParseResponse(
            application_id=app_id,
            evidence_id=request.evidence_id,
            bank_salary_detected=salary_metrics.get("bank_salary_detected", False),
            salary_amounts=salary_metrics.get("salary_amounts", []),
            salary_dates=salary_metrics.get("salary_dates", []),
            months_salary_detected=salary_metrics.get("months_salary_detected", 0),
            avg_salary=income_metrics.get("avg_salary", 0.0),
            median_salary=income_metrics.get("median_salary", 0.0),
            monthly_income_estimate=income_metrics.get("monthly_income_estimate", 0.0),
            payroll_consistency=consistency,
            inflow_std=income_metrics.get("inflow_std", 0.0),
            salary_share_of_credits=income_metrics.get("salary_share_of_credits", 0.0),
            confidence=confidence,
            ts=datetime.utcnow().isoformat(),
        )
        
        log_with_app_id(app_id, f"Parse complete: salary={salary_metrics.get('months_salary_detected')} months, confidence={confidence}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        log_with_app_id(app_id, f"Parse error: {str(e)}", level="error")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
