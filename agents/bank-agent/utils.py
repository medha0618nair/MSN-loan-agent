"""
Utility functions for bank statement parsing and salary detection.
"""
import logging
from typing import List, Dict, Tuple, Any
from datetime import datetime
import re
import statistics

logger = logging.getLogger(__name__)

# Salary detection keywords
SALARY_KEYWORDS = [
    "salary", "sal", "payroll", "salary/", "salary -", "payroll credit",
    "monthly salary", "emp", "neft", "imps", "salary txn"
]


def normalize_amount(amount_str: str) -> float:
    """Convert amount string to float, handling commas and whitespace."""
    if isinstance(amount_str, (int, float)):
        return float(amount_str)
    
    try:
        # Remove commas and whitespace
        clean = str(amount_str).replace(',', '').strip()
        return float(clean)
    except ValueError:
        logger.warning(f"Failed to normalize amount: {amount_str}")
        return 0.0


def parse_date(date_str: str) -> Tuple[datetime, bool]:
    """Parse date string to datetime object. Return (date, success)."""
    formats = [
        "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y",
        "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y",
        "%d-%b-%Y", "%d/%b/%Y"
    ]
    
    date_str = str(date_str).strip()
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt), True
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date: {date_str}")
    return None, False


def is_salary_credit(description: str, amount: float) -> bool:
    """Check if transaction is likely a salary credit."""
    if amount <= 0:
        return False
    
    desc_lower = str(description).lower()
    
    # Check keywords
    keyword_match = any(kw in desc_lower for kw in SALARY_KEYWORDS)
    
    # Typical salary ranges (INR)
    reasonable_salary = 10000 <= amount <= 500000
    
    return keyword_match and reasonable_salary


def detect_recurring_salary(
    transactions: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Detect recurring monthly salary credits.
    
    Returns:
        (salary_transactions, metrics)
    """
    salary_txns = []
    
    for txn in transactions:
        if is_salary_credit(txn.get("description", ""), txn.get("amount", 0)):
            salary_txns.append(txn)
    
    if not salary_txns:
        return [], {
            "bank_salary_detected": False,
            "salary_amounts": [],
            "salary_dates": [],
            "months_salary_detected": 0,
        }
    
    # Sort by date
    salary_txns.sort(key=lambda x: x.get("date"))
    
    # Extract amounts and dates
    amounts = [t["amount"] for t in salary_txns]
    dates = [t["date"].strftime("%Y-%m-%d") if isinstance(t["date"], datetime) else t["date"] 
             for t in salary_txns]
    
    # Check if recurring (within tolerance)
    tolerance = 0.08  # 8% variance
    avg_amt = statistics.mean(amounts) if amounts else 0
    max_variance = avg_amt * tolerance
    amount_range = max(amounts) - min(amounts) if amounts else 0
    
    is_recurring = len(amounts) >= 2 and amount_range <= max_variance
    
    metrics = {
        "bank_salary_detected": is_recurring,
        "salary_amounts": amounts,
        "salary_dates": dates,
        "months_salary_detected": len(amounts),
        "is_recurring": is_recurring,
    }
    
    return salary_txns, metrics


def compute_income_metrics(
    transactions: List[Dict[str, Any]],
    salary_txns: List[Dict[str, Any]]
) -> Dict[str, float]:
    """Compute income-related metrics."""
    salary_amounts = [t["amount"] for t in salary_txns]
    
    if not salary_amounts:
        return {
            "avg_salary": 0.0,
            "median_salary": 0.0,
            "monthly_income_estimate": 0.0,
            "inflow_std": 0.0,
            "salary_share_of_credits": 0.0,
        }
    
    # Salary statistics
    avg_salary = statistics.mean(salary_amounts)
    median_salary = statistics.median(salary_amounts)
    
    # Inflow std (all positive transactions)
    inflows = [t["amount"] for t in transactions if t["amount"] > 0]
    inflow_std = statistics.stdev(inflows) if len(inflows) > 1 else 0.0
    
    # Salary share
    total_credits = sum(inflows)
    salary_sum = sum(salary_amounts)
    salary_share = salary_sum / total_credits if total_credits > 0 else 0.0
    
    return {
        "avg_salary": round(avg_salary, 2),
        "median_salary": round(median_salary, 2),
        "monthly_income_estimate": round(median_salary, 2),
        "inflow_std": round(inflow_std, 2),
        "salary_share_of_credits": round(salary_share, 4),
    }


def compute_payroll_consistency(salary_txns: List[Dict[str, Any]]) -> float:
    """
    Compute payroll consistency score (0-1).
    
    Combines:
    - Recurrence: regular occurrence (2+ months)
    - Timing: day-of-month consistency
    - Amount: amount variance
    """
    if len(salary_txns) < 2:
        return 0.0
    
    amounts = [t["amount"] for t in salary_txns]
    dates = [t["date"] if isinstance(t["date"], datetime) else 
             datetime.strptime(t["date"], "%Y-%m-%d") for t in salary_txns]
    
    # Recurrence score: number of occurrences normalized (2+ = 1.0)
    recurrence_score = min(len(salary_txns) / 3.0, 1.0)
    
    # Timing score: day-of-month consistency
    days = [d.day for d in dates]
    day_std = statistics.stdev(days) if len(days) > 1 else 0
    timing_score = max(1.0 - (day_std / 15.0), 0.0)  # 15 days = 0 score
    
    # Amount score: variance in amounts
    amount_mean = statistics.mean(amounts)
    amount_cv = (statistics.stdev(amounts) / amount_mean) if len(amounts) > 1 and amount_mean > 0 else 0
    amount_score = max(1.0 - (amount_cv * 2), 0.0)  # CV > 0.5 = low score
    
    # Weighted combination
    consistency = (
        0.5 * recurrence_score +
        0.25 * timing_score +
        0.25 * amount_score
    )
    
    return round(min(max(consistency, 0.0), 1.0), 4)


def compute_confidence(
    salary_txns: List[Dict[str, Any]],
    metrics: Dict[str, Any],
    keyword_strength: float
) -> float:
    """
    Compute overall confidence score (0-1).
    
    Factors:
    - Presence of keywords
    - Recurrence ratio
    - Amount variance
    """
    if not salary_txns or not metrics.get("is_recurring"):
        return 0.0
    
    # Keyword strength (provided by caller)
    keyword_score = keyword_strength  # 0-1
    
    # Recurrence: 2 months = 0.5, 3+ = 1.0
    recurrence_score = min(len(salary_txns) / 3.0, 1.0)
    
    # Low variance is good
    amounts = [t["amount"] for t in salary_txns]
    if len(amounts) > 1:
        amount_mean = statistics.mean(amounts)
        cv = statistics.stdev(amounts) / amount_mean if amount_mean > 0 else 0
        variance_score = max(1.0 - (cv * 1.5), 0.0)
    else:
        variance_score = 0.7
    
    # Weighted confidence
    confidence = (
        0.4 * keyword_score +
        0.4 * recurrence_score +
        0.2 * variance_score
    )
    
    return round(min(max(confidence, 0.0), 1.0), 4)
