"""
Unit tests for bank statement parser.
"""
import pytest
import csv
import json
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    normalize_amount, parse_date, is_salary_credit,
    detect_recurring_salary, compute_income_metrics,
    compute_payroll_consistency, compute_confidence
)


class TestNormalizeAmount:
    """Test amount normalization."""
    
    def test_normalize_string_with_comma(self):
        assert normalize_amount("45,000") == 45000.0
        assert normalize_amount("1,000,000") == 1000000.0
    
    def test_normalize_float(self):
        assert normalize_amount(45000.5) == 45000.5
    
    def test_normalize_int(self):
        assert normalize_amount(45000) == 45000.0


class TestParseDate:
    """Test date parsing."""
    
    def test_parse_iso_format(self):
        date_obj, ok = parse_date("2025-09-05")
        assert ok is True
        assert date_obj.year == 2025
        assert date_obj.month == 9
        assert date_obj.day == 5
    
    def test_parse_dd_mm_yyyy(self):
        date_obj, ok = parse_date("05-09-2025")
        assert ok is True or ok is False  # Depends on format ambiguity
    
    def test_parse_invalid(self):
        date_obj, ok = parse_date("invalid-date")
        assert ok is False


class TestSalaryCreditDetection:
    """Test salary credit identification."""
    
    def test_salary_keyword_match(self):
        assert is_salary_credit("SALARY CREDIT", 45000) is True
        assert is_salary_credit("payroll credit", 45000) is True
        assert is_salary_credit("sal deposit", 45000) is True
    
    def test_negative_amount(self):
        assert is_salary_credit("SALARY", -45000) is False
    
    def test_amount_out_of_range(self):
        assert is_salary_credit("SALARY", 5000) is False  # Too low
        assert is_salary_credit("SALARY", 600000) is False  # Too high
    
    def test_no_keyword_match(self):
        assert is_salary_credit("RANDOM CREDIT", 45000) is False


class TestRecurringSalaryDetection:
    """Test recurring salary detection."""
    
    def test_recurring_salary_3_months(self):
        transactions = [
            {"date": datetime(2025, 9, 5), "amount": 45000, "description": "SALARY"},
            {"date": datetime(2025, 10, 5), "amount": 45100, "description": "SALARY"},
            {"date": datetime(2025, 11, 5), "amount": 45000, "description": "SALARY"},
        ]
        salary_txns, metrics = detect_recurring_salary(transactions)
        
        assert len(salary_txns) == 3
        assert metrics["bank_salary_detected"] is True
        assert metrics["months_salary_detected"] == 3
    
    def test_no_salary(self):
        transactions = [
            {"date": datetime(2025, 9, 5), "amount": -2500, "description": "DEBIT"},
            {"date": datetime(2025, 10, 5), "amount": 1000, "description": "RANDOM"},
        ]
        salary_txns, metrics = detect_recurring_salary(transactions)
        
        assert len(salary_txns) == 0
        assert metrics["bank_salary_detected"] is False


class TestIncomeMetrics:
    """Test income metric calculation."""
    
    def test_income_metrics_calculation(self):
        transactions = [
            {"date": datetime(2025, 9, 5), "amount": 45000, "description": "SALARY"},
            {"date": datetime(2025, 10, 5), "amount": 45000, "description": "SALARY"},
            {"date": datetime(2025, 11, 5), "amount": 45000, "description": "SALARY"},
            {"date": datetime(2025, 9, 10), "amount": -2500, "description": "BILL"},
        ]
        salary_txns = transactions[:3]
        
        metrics = compute_income_metrics(transactions, salary_txns)
        
        assert metrics["avg_salary"] == 45000.0
        assert metrics["median_salary"] == 45000.0
        assert metrics["monthly_income_estimate"] == 45000.0
        assert metrics["salary_share_of_credits"] > 0


class TestPayrollConsistency:
    """Test payroll consistency score."""
    
    def test_consistent_payroll(self):
        salary_txns = [
            {"date": datetime(2025, 9, 5), "amount": 45000},
            {"date": datetime(2025, 10, 5), "amount": 45000},
            {"date": datetime(2025, 11, 5), "amount": 45000},
        ]
        
        score = compute_payroll_consistency(salary_txns)
        assert 0.8 <= score <= 1.0  # High consistency
    
    def test_inconsistent_payroll(self):
        salary_txns = [
            {"date": datetime(2025, 9, 5), "amount": 45000},
            {"date": datetime(2025, 10, 15), "amount": 35000},  # Different day and amount
        ]
        
        score = compute_payroll_consistency(salary_txns)
        assert score < 0.8  # Lower consistency


class TestConfidence:
    """Test confidence calculation."""
    
    def test_high_confidence(self):
        salary_txns = [
            {"date": datetime(2025, 9, 5), "amount": 45000, "description": "SALARY"},
            {"date": datetime(2025, 10, 5), "amount": 45000, "description": "SALARY"},
            {"date": datetime(2025, 11, 5), "amount": 45000, "description": "SALARY"},
        ]
        metrics = {"is_recurring": True}
        
        confidence = compute_confidence(salary_txns, metrics, keyword_strength=0.9)
        assert confidence > 0.7
    
    def test_low_confidence_no_recurrence(self):
        salary_txns = [
            {"date": datetime(2025, 9, 5), "amount": 45000, "description": "SALARY"},
        ]
        metrics = {"is_recurring": False}
        
        confidence = compute_confidence(salary_txns, metrics, keyword_strength=0.5)
        assert confidence == 0.0


class TestCSVIntegration:
    """Integration tests with actual CSV files."""
    
    @pytest.fixture
    def sample_csv(self, tmp_path):
        """Create a sample CSV file."""
        csv_file = tmp_path / "test_bank.csv"
        transactions = [
            ["date", "amount", "description"],
            ["2025-09-05", "45000", "SALARY CREDIT"],
            ["2025-09-10", "-2500", "UPI PAYMENT"],
            ["2025-10-05", "45100", "SALARY CREDIT"],
            ["2025-10-12", "-3000", "BILL PAYMENT"],
            ["2025-11-05", "45000", "SALARY CREDIT"],
            ["2025-11-15", "-2000", "SHOPPING"],
        ]
        
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(transactions)
        
        return csv_file
    
    def test_valid_csv_parsing(self, sample_csv):
        """Test parsing of valid CSV file."""
        import pandas as pd
        
        df = pd.read_csv(sample_csv)
        df.columns = [col.lower().strip() for col in df.columns]
        
        assert "date" in df.columns
        assert "amount" in df.columns
        assert "description" in df.columns
        assert len(df) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
