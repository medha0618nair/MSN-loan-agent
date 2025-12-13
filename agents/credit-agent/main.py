"""
Credit Scoring Agent - FastAPI Service.
Accepts merged evidence from orchestrator and returns credit decisions.
"""
import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import (
    CreditScoringRequest, CreditScoringResponse, ErrorResponse,
    ModelInfoResponse, FeatureImportances
)
from utils import (
    FeatureEngineer, ScoringRules, create_explanation_tokens,
    ProbabilityCalculator
)
from model import CreditScoringModel, train_sample_model

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Credit Scoring Agent",
    description="Produce credit decisions from merged agent evidence",
    version="score-v1"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://10.110.1.81:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
scoring_model: Optional[CreditScoringModel] = None
AUDIT_DIR = Path("./audit")


def initialize():
    """Initialize model and audit directory."""
    global scoring_model
    
    AUDIT_DIR.mkdir(exist_ok=True)
    
    # Try to load existing model; if none, train sample
    scoring_model = CreditScoringModel()
    
    if scoring_model.is_fallback:
        logger.info("No trained model found, attempting to train sample model...")
        try:
            train_sample_model()
            # Reload after training
            scoring_model = CreditScoringModel()
        except Exception as e:
            logger.warning(f"Could not train sample model: {e}")
    
    logger.info("Credit Scoring Agent initialized")


def log_with_app_id(app_id: str, message: str, level: str = "info"):
    """Helper to log with application_id prefix."""
    log_msg = f"[{app_id}] {message}"
    if level == "info":
        logger.info(log_msg)
    elif level == "error":
        logger.error(log_msg)
    elif level == "warning":
        logger.warning(log_msg)


def write_audit_log(app_id: str, request_data: dict, response_data: dict):
    """Write request/response to audit file (PII-safe)."""
    try:
        audit_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "application_id": app_id,
            "request_summary": {
                "loan_amount": request_data.get("loan_request", {}).get("loan_amount"),
                "tenure_months": request_data.get("loan_request", {}).get("tenure_months"),
            },
            "response": response_data
        }
        
        audit_file = AUDIT_DIR / f"audit_{app_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(audit_file, "w") as f:
            json.dump(audit_record, f, indent=2)
        
        log_with_app_id(app_id, f"Audit logged to {audit_file.name}")
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    initialize()


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "version": "score-v1"}


@app.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Return model metadata."""
    if not scoring_model:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    info = scoring_model.get_model_info()
    return ModelInfoResponse(
        model_version=info["model_version"],
        training_date=info["training_date"],
        feature_list=info["feature_list"],
        model_type=info["model_type"],
        status=info["status"]
    )


@app.post("/score", response_model=CreditScoringResponse)
async def score_application(request: CreditScoringRequest):
    """
    Score a credit application based on merged agent evidence.
    
    Returns probability of default, risk tier, and recommended action.
    """
    app_id = request.application_id
    log_with_app_id(app_id, "Score request received")
    
    try:
        # Validate required evidence
        evidence = request.evidence
        loan = request.loan_request
        
        # Check for sufficient evidence
        is_sufficient, error_msg = ScoringRules.check_sufficient_evidence(evidence)
        if not is_sufficient:
            log_with_app_id(app_id, f"Insufficient evidence: {error_msg}", "warning")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Extract features
        monthly_income, income_source = FeatureEngineer.get_monthly_income(evidence)
        if monthly_income is None:
            raise HTTPException(status_code=400, detail="insufficient_income_evidence")
        
        log_with_app_id(app_id, f"Monthly income: ₹{monthly_income} ({income_source})")
        
        # Calculate derived features
        dti = FeatureEngineer.calculate_dti(loan.monthly_emi_estimate, monthly_income)
        income_confidence = FeatureEngineer.get_income_confidence(evidence)
        identity_confidence = FeatureEngineer.get_identity_confidence(evidence)
        loan_to_income = FeatureEngineer.calculate_loan_to_income(
            loan.loan_amount, monthly_income, loan.tenure_months
        )
        
        payroll_consistency = evidence.bank.payroll_consistency if evidence.bank else 0.0
        fraud_score = evidence.fraud.fraud_score if evidence.fraud else 0.0
        months_salary = evidence.bank.months_salary_detected if evidence.bank else None
        
        log_with_app_id(app_id, f"DTI: {dti:.2f}, Income Confidence: {income_confidence:.2f}")
        
        # Check fraud flags first
        is_fraud_ok, fraud_action = ScoringRules.check_fraud_flags(evidence)
        
        # Prepare features for model
        feature_dict = {
            "dti": dti,
            "income_confidence": income_confidence,
            "payroll_consistency": payroll_consistency,
            "fraud_score": fraud_score,
            "identity_confidence": identity_confidence,
            "months_salary_detected": float(months_salary) if months_salary else None,
            "tenure_months": float(loan.tenure_months),
            "loan_to_income": loan_to_income,
            "income_level_normalized": min(monthly_income / 50000.0, 1.0)  # Normalize to ~50K
        }
        
        # Get PD score and importances from model
        pd_score, importances_raw = scoring_model.predict(feature_dict)
        
        log_with_app_id(app_id, f"PD Score: {pd_score:.4f}")
        
        # Map to decision
        risk_tier, action = ProbabilityCalculator.map_pd_to_tier_and_action(pd_score)
        
        # Override action if fraud
        if not is_fraud_ok:
            action = fraud_action
            log_with_app_id(app_id, f"Fraud override: {action}", "warning")
        
        # Calculate max eligible loan
        max_eligible = ScoringRules.calculate_max_eligible_loan(
            monthly_income=monthly_income,
            tenure_months=loan.tenure_months,
            income_confidence=income_confidence,
            payroll_consistency=payroll_consistency
        )
        
        # Recommend tenure
        recommended_tenure = ScoringRules.recommend_tenure(
            loan.tenure_months,
            dti,
            income_confidence
        )
        
        # Calculate recommended EMI
        recommended_emi = (loan.loan_amount / recommended_tenure) if recommended_tenure > 0 else loan.monthly_emi_estimate
        
        # Generate explanation
        explanation = create_explanation_tokens(
            evidence=evidence,
            monthly_income=monthly_income,
            income_source=income_source,
            dti=dti,
            fraud_score=fraud_score
        )
        
        # Calculate confidence (model confidence * evidence quality)
        evidence_confidence = min(
            (income_confidence + identity_confidence) / 2.0 * 0.6 + 0.4,
            1.0
        )
        
        # Build response
        feature_imp = FeatureImportances(
            income=importances_raw.get("income", 0.35),
            payroll_consistency=importances_raw.get("payroll_consistency", 0.25),
            fraud_score=importances_raw.get("fraud_score", 0.15),
            face_confidence=importances_raw.get("face_confidence", 0.10),
            kyc_confidence=importances_raw.get("kyc_confidence", 0.10),
            dti=importances_raw.get("dti", 0.03),
            tenure=importances_raw.get("tenure", 0.02),
            other=importances_raw.get("other", 0.00)
        )
        
        response = CreditScoringResponse(
            application_id=app_id,
            pd_score=round(pd_score, 4),
            risk_tier=risk_tier,
            recommended_action=action,
            max_eligible_loan=max_eligible,
            recommended_tenure_months=recommended_tenure,
            monthly_emi_recommendation=round(recommended_emi, 2),
            explanation=explanation,
            feature_importances=feature_imp,
            confidence=round(evidence_confidence, 2),
            agent_version="score-v1",
            ts=datetime.now(timezone.utc).isoformat()
        )
        
        # Audit log
        write_audit_log(app_id, request.model_dump(), response.model_dump())
        
        log_with_app_id(app_id, f"Decision: {action} (PD: {pd_score:.2%}, Risk: {risk_tier})")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        log_with_app_id(app_id, f"Error: {e}", "error")
        raise HTTPException(status_code=500, detail="internal_error")


@app.post("/validate-schema")
async def validate_schema(request: dict):
    """Debug endpoint to validate request schema."""
    try:
        req = CreditScoringRequest(**request)
        return {"status": "valid", "application_id": req.application_id}
    except Exception as e:
        return {"status": "invalid", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
