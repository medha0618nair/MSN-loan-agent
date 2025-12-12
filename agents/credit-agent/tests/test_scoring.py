"""
Unit tests for Credit Scoring Agent.
"""
import pytest
from datetime import datetime
import json

from models import (
    CreditScoringRequest, IntakeEvidence, KYCEvidence, FaceEvidence,
    PayslipEvidence, BankEvidence, FraudEvidence, EvidenceBundle,
    LoanRequest, AppMetadata
)
from utils import (
    FeatureEngineer, ScoringRules, ProbabilityCalculator,
    create_explanation_tokens
)
from model import CreditScoringModel


@pytest.fixture
def sample_good_evidence():
    """Complete, clean evidence for approval."""
    return EvidenceBundle(
        intake=IntakeEvidence(
            applicant_name="John Doe",
            email="john@example.com",
            pan="DIJPN7537R",
            loan_amount=150000
        ),
        kyc=KYCEvidence(
            pan_number="DIJPN7537R",
            name_extracted="JOHN DOE",
            kyc_confidence=0.95
        ),
        face=FaceEvidence(
            face_verified=True,
            match_confidence=0.92
        ),
        payslip=PayslipEvidence(
            net_pay_payslip=45000,
            monthly_income=45000,
            income_confidence=0.85
        ),
        bank=BankEvidence(
            median_salary=44000,
            months_salary_detected=6,
            payroll_consistency=0.85,
            salary_share_of_credits=0.80,
            confidence=0.90,
            bank_salary_detected=True
        ),
        fraud=FraudEvidence(
            fraud_score=0.05,
            reasons=[]
        )
    )


@pytest.fixture
def sample_loan_request():
    """Standard loan request."""
    return LoanRequest(
        loan_amount=150000,
        tenure_months=24,
        monthly_emi_estimate=6750
    )


@pytest.fixture
def sample_metadata():
    """Standard metadata."""
    return AppMetadata(
        submission_ts=datetime.utcnow().isoformat(),
        source="web"
    )


class TestFeatureEngineering:
    """Test feature extraction and engineering."""
    
    def test_monthly_income_bank_preferred(self, sample_good_evidence):
        """Bank income should be preferred when confidence high."""
        income, source = FeatureEngineer.get_monthly_income(sample_good_evidence)
        assert income == 44000
        assert source == "bank_statement"
    
    def test_monthly_income_fallback_to_payslip(self):
        """Fall back to payslip when bank confidence low."""
        evidence = EvidenceBundle(
            bank=BankEvidence(
                median_salary=44000,
                confidence=0.4  # Below 0.6 threshold
            ),
            payslip=PayslipEvidence(
                net_pay_payslip=45000,
                income_confidence=0.8
            )
        )
        income, source = FeatureEngineer.get_monthly_income(evidence)
        assert income == 45000
        assert source == "payslip"
    
    def test_monthly_income_missing(self):
        """Return None when no income available."""
        evidence = EvidenceBundle()
        income, source = FeatureEngineer.get_monthly_income(evidence)
        assert income is None
        assert source == "missing"
    
    def test_income_confidence_combined(self, sample_good_evidence):
        """Income confidence should be weighted average."""
        conf = FeatureEngineer.get_income_confidence(sample_good_evidence)
        assert 0.8 <= conf <= 1.0
    
    def test_identity_confidence(self, sample_good_evidence):
        """Identity confidence combines KYC and face."""
        conf = FeatureEngineer.get_identity_confidence(sample_good_evidence)
        assert 0.9 <= conf <= 1.0
    
    def test_dti_calculation(self):
        """DTI = EMI / monthly_income."""
        dti = FeatureEngineer.calculate_dti(
            monthly_emi=6750,
            monthly_income=45000
        )
        assert abs(dti - 0.15) < 0.01
    
    def test_dti_missing_income(self):
        """DTI should be None if income missing."""
        dti = FeatureEngineer.calculate_dti(6750, None)
        assert dti is None
    
    def test_loan_to_income(self):
        """LTI = loan_amount / (monthly_income * tenure)."""
        lti = FeatureEngineer.calculate_loan_to_income(
            loan_amount=150000,
            monthly_income=45000,
            tenure_months=24
        )
        expected = 150000 / (45000 * 24)
        assert abs(lti - expected) < 0.001


class TestScoringRules:
    """Test decision rules and validations."""
    
    def test_sufficient_evidence_complete(self, sample_good_evidence):
        """Complete evidence should pass validation."""
        is_sufficient, error = ScoringRules.check_sufficient_evidence(sample_good_evidence)
        assert is_sufficient is True
        assert error is None
    
    def test_insufficient_identity(self):
        """Missing identity should fail."""
        evidence = EvidenceBundle(
            bank=BankEvidence(median_salary=45000, confidence=0.9)
        )
        is_sufficient, error = ScoringRules.check_sufficient_evidence(evidence)
        assert is_sufficient is False
        assert error == "insufficient_identity_evidence"
    
    def test_insufficient_income(self):
        """Missing income should fail."""
        evidence = EvidenceBundle(
            kyc=KYCEvidence(kyc_confidence=0.8)
        )
        is_sufficient, error = ScoringRules.check_sufficient_evidence(evidence)
        assert is_sufficient is False
        assert error == "insufficient_income_evidence"
    
    def test_fraud_ok(self, sample_good_evidence):
        """Low fraud score should pass."""
        is_ok, action = ScoringRules.check_fraud_flags(sample_good_evidence)
        assert is_ok is True
        assert action is None
    
    def test_fraud_high_review(self):
        """Fraud score 0.6-0.8 should trigger REVIEW."""
        evidence = EvidenceBundle(
            fraud=FraudEvidence(fraud_score=0.65)
        )
        is_ok, action = ScoringRules.check_fraud_flags(evidence)
        assert is_ok is False
        assert action == "REVIEW"
    
    def test_fraud_very_high_reject(self):
        """Fraud score > 0.8 should trigger REJECT."""
        evidence = EvidenceBundle(
            fraud=FraudEvidence(fraud_score=0.85)
        )
        is_ok, action = ScoringRules.check_fraud_flags(evidence)
        assert is_ok is False
        assert action == "REJECT"
    
    def test_max_eligible_loan(self):
        """Max eligible should be based on income."""
        max_loan = ScoringRules.calculate_max_eligible_loan(
            monthly_income=45000,
            tenure_months=24,
            income_confidence=0.9,
            payroll_consistency=0.85
        )
        # Should be roughly 30 months of income
        assert 800000 < max_loan < 1400000
    
    def test_recommend_tenure_high_dti(self):
        """High DTI should reduce tenure."""
        tenure = ScoringRules.recommend_tenure(
            requested_tenure=36,
            dti=0.45,
            income_confidence=0.7
        )
        assert tenure < 36
    
    def test_pd_to_tier_low(self):
        """PD <= 0.30 should be LOW risk."""
        tier, action = ProbabilityCalculator.map_pd_to_tier_and_action(0.25)
        assert tier == "LOW"
        assert action == "APPROVE"
    
    def test_pd_to_tier_medium(self):
        """0.30 < PD <= 0.60 should be MEDIUM risk."""
        tier, action = ProbabilityCalculator.map_pd_to_tier_and_action(0.45)
        assert tier == "MEDIUM"
        assert action == "REVIEW"
    
    def test_pd_to_tier_high(self):
        """PD > 0.60 should be HIGH risk."""
        tier, action = ProbabilityCalculator.map_pd_to_tier_and_action(0.75)
        assert tier == "HIGH"
        assert action == "REJECT"


class TestProbabilityCalculation:
    """Test default probability calculation."""
    
    def test_logistic_function(self):
        """Logistic should output 0-1."""
        assert 0 < ProbabilityCalculator.logistic(0) < 1
        assert ProbabilityCalculator.logistic(-10) < 0.1
        assert ProbabilityCalculator.logistic(10) > 0.9
    
    def test_default_probability_good(self):
        """Good profile should have low PD."""
        pd = ProbabilityCalculator.calculate_default_probability(
            dti=0.15,
            income_confidence=0.9,
            payroll_consistency=0.85,
            fraud_score=0.05,
            identity_confidence=0.92,
            months_salary_detected=6
        )
        assert pd < 0.35
    
    def test_default_probability_risky(self):
        """Risky profile should have high PD."""
        pd = ProbabilityCalculator.calculate_default_probability(
            dti=0.55,
            income_confidence=0.4,
            payroll_consistency=0.3,
            fraud_score=0.4,
            identity_confidence=0.5,
            months_salary_detected=1
        )
        assert pd > 0.5


class TestExplanationTokens:
    """Test explanation generation."""
    
    def test_explanation_tokens(self, sample_good_evidence):
        """Should generate relevant tokens."""
        tokens = create_explanation_tokens(
            evidence=sample_good_evidence,
            monthly_income=44000,
            income_source="bank_statement",
            dti=0.15,
            fraud_score=0.05
        )
        assert "median_income_used" in tokens
        assert "face_verified" in tokens
        assert "low_fraud_score" in tokens
        assert len(tokens) > 0


class TestScoringModel:
    """Test model interface."""
    
    def test_model_loads(self):
        """Model should initialize (fallback or trained)."""
        model = CreditScoringModel()
        assert model is not None
        assert model.model_version is not None
    
    def test_model_predict(self):
        """Model predict should return valid PD and importances."""
        model = CreditScoringModel()
        features = {
            "dti": 0.15,
            "income_confidence": 0.9,
            "payroll_consistency": 0.85,
            "fraud_score": 0.05,
            "identity_confidence": 0.92,
            "months_salary_detected": 6,
            "tenure_months": 24,
            "loan_to_income": 1.0,
            "income_level_normalized": 0.9
        }
        pd_score, importances = model.predict(features)
        
        assert 0 <= pd_score <= 1
        assert isinstance(importances, dict)
        assert len(importances) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
