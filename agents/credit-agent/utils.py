"""
Feature engineering and scoring utilities for credit decisioning.
"""
import math
from typing import Dict, Optional, List, Tuple
import numpy as np
from models import EvidenceBundle, LoanRequest


class FeatureEngineer:
    """Extract and engineer features from evidence bundle."""
    
    @staticmethod
    def get_monthly_income(evidence: EvidenceBundle) -> Tuple[Optional[int], str]:
        """
        Determine monthly income with precedence: bank > payslip > null.
        Returns (income, source).
        """
        # Prefer bank statement if confidence >= 0.6
        if evidence.bank and evidence.bank.median_salary:
            if evidence.bank.confidence >= 0.6:
                return evidence.bank.median_salary, "bank_statement"
        
        # Fall back to payslip
        if evidence.payslip and evidence.payslip.net_pay_payslip:
            return evidence.payslip.net_pay_payslip, "payslip"
        
        if evidence.payslip and evidence.payslip.monthly_income:
            return evidence.payslip.monthly_income, "payslip"
        
        # Final fallback to bank avg
        if evidence.bank and evidence.bank.avg_salary:
            return evidence.bank.avg_salary, "bank_avg"
        
        return None, "missing"
    
    @staticmethod
    def get_income_confidence(evidence: EvidenceBundle) -> float:
        """
        Weighted average of confidence scores from income sources.
        """
        confidences = []
        weights = []
        
        if evidence.bank:
            confidences.append(evidence.bank.confidence)
            weights.append(0.6)  # Bank highest weight
        
        if evidence.payslip:
            confidences.append(evidence.payslip.income_confidence)
            weights.append(0.35)  # Payslip second
        
        if evidence.face:
            confidences.append(evidence.face.match_confidence * 0.2)
            weights.append(0.05)  # Face low weight for income
        
        if not confidences:
            return 0.0
        
        return sum(c * w for c, w in zip(confidences, weights)) / sum(weights)
    
    @staticmethod
    def get_identity_confidence(evidence: EvidenceBundle) -> float:
        """
        Combined identity confidence: KYC and face verification.
        """
        confidences = []
        
        if evidence.kyc:
            confidences.append(evidence.kyc.kyc_confidence)
        
        if evidence.face:
            confidences.append(evidence.face.match_confidence)
        
        if not confidences:
            return 0.0
        
        return np.mean(confidences)
    
    @staticmethod
    def calculate_dti(monthly_emi: float, monthly_income: Optional[int]) -> Optional[float]:
        """
        Debt-to-Income ratio: EMI / monthly_income.
        """
        if monthly_income is None or monthly_income <= 0:
            return None
        
        return monthly_emi / monthly_income
    
    @staticmethod
    def calculate_loan_to_income(loan_amount: int, monthly_income: Optional[int], tenure_months: int) -> Optional[float]:
        """
        Loan-to-income ratio: loan_amount / (monthly_income * tenure_months).
        """
        if monthly_income is None or monthly_income <= 0:
            return None
        
        total_income_period = monthly_income * tenure_months
        return loan_amount / total_income_period if total_income_period > 0 else None


class ScoringRules:
    """Decision rules and risk assessment."""
    
    @staticmethod
    def check_sufficient_evidence(evidence: EvidenceBundle) -> Tuple[bool, Optional[str]]:
        """
        Validate that we have minimum evidence to score.
        Returns (is_sufficient, error_reason).
        """
        # Must have identity verification
        kyc_ok = evidence.kyc and evidence.kyc.kyc_confidence >= 0.5
        face_ok = evidence.face and evidence.face.match_confidence >= 0.5
        
        identity_ok = kyc_ok or face_ok
        if not identity_ok:
            return False, "insufficient_identity_evidence"
        
        # Must have income evidence
        income, source = FeatureEngineer.get_monthly_income(evidence)
        if income is None:
            return False, "insufficient_income_evidence"
        
        return True, None
    
    @staticmethod
    def check_fraud_flags(evidence: EvidenceBundle) -> Tuple[bool, Optional[str]]:
        """
        Check for fraud red flags.
        Returns (is_fraud_ok, action_override).
        """
        if not evidence.fraud:
            return True, None
        
        fraud_score = evidence.fraud.fraud_score
        
        if fraud_score > 0.8:
            return False, "REJECT"
        
        if fraud_score > 0.6:
            return False, "REVIEW"
        
        return True, None
    
    @staticmethod
    def calculate_max_eligible_loan(
        monthly_income: int,
        tenure_months: int,
        income_confidence: float,
        payroll_consistency: Optional[float] = None
    ) -> int:
        """
        Calculate maximum eligible loan based on income and stability.
        Formula: monthly_income * tenure_months * risk_factor
        """
        base_ltv = 30  # Max 30 months of income
        
        # Adjust for income confidence
        confidence_factor = 1.0 if income_confidence >= 0.8 else 0.9 if income_confidence >= 0.6 else 0.7
        
        # Adjust for payroll consistency
        stability_factor = 1.0
        if payroll_consistency is not None:
            if payroll_consistency < 0.5:
                stability_factor = 0.7
            elif payroll_consistency < 0.7:
                stability_factor = 0.85
        
        max_loan = int(monthly_income * base_ltv * confidence_factor * stability_factor)
        return max_loan
    
    @staticmethod
    def recommend_tenure(
        requested_tenure: int,
        dti: Optional[float],
        income_confidence: float
    ) -> int:
        """
        Recommend tenure based on DTI and income confidence.
        """
        if dti is None:
            return requested_tenure
        
        if dti > 0.4:
            # High EMI burden, reduce tenure
            return max(12, requested_tenure - 12)
        elif dti > 0.5:
            # Very high burden
            return max(12, requested_tenure - 24)
        
        # If low burden and high confidence, can extend
        if dti < 0.25 and income_confidence >= 0.8:
            return min(84, requested_tenure + 12)
        
        return requested_tenure


class ProbabilityCalculator:
    """Default rule-based PD calculation when model unavailable."""
    
    @staticmethod
    def logistic(x: float) -> float:
        """Logistic function: 1 / (1 + e^-x)."""
        try:
            return 1.0 / (1.0 + np.exp(-x))
        except:
            return 0.5
    
    @staticmethod
    def calculate_default_probability(
        dti: Optional[float],
        income_confidence: float,
        payroll_consistency: Optional[float],
        fraud_score: float,
        identity_confidence: float,
        months_salary_detected: Optional[int]
    ) -> float:
        """
        Rule-based PD score using logistic formula.
        Higher = more default risk.
        """
        score = 0.0
        
        # DTI component: each 0.1 increase adds 0.2 to score
        if dti is not None:
            score += min(dti * 2.0, 1.0)
        else:
            score += 0.3  # Missing DTI is risky
        
        # Income confidence: lower confidence increases risk
        score += (1.0 - income_confidence) * 0.3
        
        # Payroll consistency: low consistency = higher risk
        if payroll_consistency is not None:
            score += (1.0 - payroll_consistency) * 0.2
        else:
            score += 0.15
        
        # Fraud: direct addition
        score += fraud_score * 0.15
        
        # Identity: low confidence = high risk
        score += (1.0 - identity_confidence) * 0.15
        
        # Salary history: low months = higher risk
        if months_salary_detected is not None:
            salary_history_factor = min(months_salary_detected / 6.0, 1.0)
            score += (1.0 - salary_history_factor) * 0.05
        else:
            score += 0.05
        
        # Apply logistic transformation and normalize to [0, 1]
        pd_score = ProbabilityCalculator.logistic(score - 2.0)
        
        return round(pd_score, 4)
    
    @staticmethod
    def map_pd_to_tier_and_action(pd_score: float) -> Tuple[str, str]:
        """
        Map PD score to risk tier and recommended action.
        """
        if pd_score <= 0.30:
            return "LOW", "APPROVE"
        elif pd_score <= 0.60:
            return "MEDIUM", "REVIEW"
        else:
            return "HIGH", "REJECT"


def create_explanation_tokens(
    evidence: EvidenceBundle,
    monthly_income: int,
    income_source: str,
    dti: Optional[float],
    fraud_score: float
) -> List[str]:
    """
    Generate human-readable explanation tokens.
    """
    tokens = []
    
    # Income source
    if income_source == "bank_statement":
        tokens.append("median_income_used")
    elif income_source == "payslip":
        tokens.append("payslip_income_used")
    
    # Fraud
    if fraud_score < 0.3:
        tokens.append("low_fraud_score")
    elif fraud_score > 0.6:
        tokens.append("high_fraud_risk")
    
    # Identity
    if evidence.face and evidence.face.face_verified:
        tokens.append("face_verified")
    
    if evidence.kyc and evidence.kyc.kyc_confidence >= 0.8:
        tokens.append("kyc_verified")
    
    # Income stability
    if evidence.bank and evidence.bank.payroll_consistency >= 0.8:
        tokens.append("stable_payroll")
    elif evidence.bank and evidence.bank.payroll_consistency < 0.5:
        tokens.append("inconsistent_payroll")
    
    # DTI
    if dti is not None:
        if dti < 0.25:
            tokens.append("low_dti")
        elif dti > 0.4:
            tokens.append("high_dti")
    
    # Salary history
    if evidence.bank and evidence.bank.months_salary_detected:
        if evidence.bank.months_salary_detected >= 6:
            tokens.append("long_salary_history")
        elif evidence.bank.months_salary_detected < 2:
            tokens.append("short_salary_history")
    
    return tokens if tokens else ["standard_assessment"]
