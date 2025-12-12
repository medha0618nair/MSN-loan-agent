"""
Credit scoring model: training, prediction, and fallback logic.
Provides both LightGBM model and rule-based fallback.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
from pathlib import Path
import joblib

try:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    HAS_LGB = True
except ImportError:
    HAS_LGB = False

from utils import ProbabilityCalculator

logger = logging.getLogger(__name__)

MODEL_DIR = Path("./models")
MODEL_PATH = MODEL_DIR / "credit_model.pkl"
SCALER_PATH = MODEL_DIR / "feature_scaler.pkl"
MODEL_METADATA_PATH = MODEL_DIR / "model_metadata.json"


class CreditScoringModel:
    """Wrapper for credit scoring model with fallback."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_version = "score-v1"
        self.training_date = None
        self.feature_names = [
            "dti",
            "income_confidence",
            "payroll_consistency",
            "fraud_score",
            "identity_confidence",
            "months_salary_detected",
            "tenure_months",
            "loan_to_income",
            "income_level_normalized"
        ]
        self.is_fallback = True
        
        # Try to load model
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model from disk."""
        if not HAS_LGB:
            logger.warning("LightGBM not available, using fallback scorer")
            return
        
        if not MODEL_PATH.exists():
            logger.info("No model file found, will use fallback rule-based scoring")
            return
        
        try:
            self.model = joblib.load(MODEL_PATH)
            if SCALER_PATH.exists():
                self.scaler = joblib.load(SCALER_PATH)
            
            if MODEL_METADATA_PATH.exists():
                with open(MODEL_METADATA_PATH) as f:
                    metadata = json.load(f)
                    self.model_version = metadata.get("model_version", "score-v1")
                    self.training_date = metadata.get("training_date")
            
            self.is_fallback = False
            logger.info(f"Loaded model {self.model_version}")
        except Exception as e:
            logger.warning(f"Failed to load model: {e}, using fallback")
            self.is_fallback = True
    
    def _prepare_features(self, feature_dict: Dict[str, Optional[float]]) -> np.ndarray:
        """
        Convert feature dict to numpy array in correct order.
        Impute missing values with sensible defaults.
        """
        features = []
        
        for fname in self.feature_names:
            value = feature_dict.get(fname)
            
            # Imputation defaults
            if value is None:
                if fname == "dti":
                    value = 0.3  # Default moderate DTI
                elif fname == "income_confidence":
                    value = 0.5
                elif fname == "payroll_consistency":
                    value = 0.6
                elif fname == "fraud_score":
                    value = 0.2
                elif fname == "identity_confidence":
                    value = 0.5
                elif fname == "months_salary_detected":
                    value = 3
                elif fname == "tenure_months":
                    value = 24
                elif fname == "loan_to_income":
                    value = 1.0
                elif fname == "income_level_normalized":
                    value = 0.5
            
            features.append(float(value))
        
        return np.array(features).reshape(1, -1)
    
    def predict(self, feature_dict: Dict[str, Optional[float]]) -> Tuple[float, Dict[str, float]]:
        """
        Predict probability of default and return feature importances.
        
        Args:
            feature_dict: Dictionary of features (can have missing values)
        
        Returns:
            (pd_score, feature_importances_dict)
        """
        X = self._prepare_features(feature_dict)
        
        # Use model if available
        if not self.is_fallback and self.model is not None:
            try:
                if self.scaler:
                    X_scaled = self.scaler.transform(X)
                else:
                    X_scaled = X
                
                # Get probability for default class
                if hasattr(self.model, 'predict_proba'):
                    proba = self.model.predict_proba(X_scaled)[0]
                    pd_score = float(proba[1]) if len(proba) > 1 else float(proba[0])
                else:
                    pd_score = float(self.model.predict(X_scaled)[0])
                
                # Get feature importances
                if hasattr(self.model, 'feature_importances_'):
                    importances = self.model.feature_importances_
                    importances_dict = {
                        name: float(imp) 
                        for name, imp in zip(self.feature_names, importances)
                    }
                    # Normalize to sum to 1.0
                    total = sum(importances_dict.values())
                    if total > 0:
                        importances_dict = {k: v/total for k, v in importances_dict.items()}
                else:
                    importances_dict = self._default_importances()
                
                return pd_score, importances_dict
            
            except Exception as e:
                logger.warning(f"Model prediction failed: {e}, falling back to rules")
                return self._fallback_predict(feature_dict)
        
        return self._fallback_predict(feature_dict)
    
    def _fallback_predict(self, feature_dict: Dict[str, Optional[float]]) -> Tuple[float, Dict[str, float]]:
        """
        Rule-based fallback prediction.
        """
        dti = feature_dict.get("dti")
        income_confidence = feature_dict.get("income_confidence", 0.5)
        payroll_consistency = feature_dict.get("payroll_consistency")
        fraud_score = feature_dict.get("fraud_score", 0.0)
        identity_confidence = feature_dict.get("identity_confidence", 0.5)
        months_salary = feature_dict.get("months_salary_detected")
        
        pd_score = ProbabilityCalculator.calculate_default_probability(
            dti=dti,
            income_confidence=income_confidence,
            payroll_consistency=payroll_consistency,
            fraud_score=fraud_score,
            identity_confidence=identity_confidence,
            months_salary_detected=months_salary
        )
        
        importances = self._default_importances()
        return pd_score, importances
    
    def _default_importances(self) -> Dict[str, float]:
        """Default feature importance distribution."""
        return {
            "income": 0.35,
            "payroll_consistency": 0.25,
            "fraud_score": 0.15,
            "face_confidence": 0.10,
            "kyc_confidence": 0.10,
            "dti": 0.03,
            "tenure": 0.02,
            "other": 0.00
        }
    
    def get_model_info(self) -> Dict:
        """Return model metadata."""
        return {
            "model_version": self.model_version,
            "training_date": self.training_date,
            "feature_list": self.feature_names,
            "model_type": "GradientBoosting" if not self.is_fallback else "RuleBased",
            "status": "trained" if not self.is_fallback else "fallback"
        }


def train_sample_model():
    """
    Train a sample Gradient Boosting model on synthetic data.
    Call this once to create a model file.
    """
    if not HAS_LGB:
        logger.error("scikit-learn not installed, cannot train model")
        return
    
    from sklearn.ensemble import GradientBoostingClassifier
    
    logger.info("Training sample credit scoring model...")
    
    # Create synthetic training data
    n_samples = 1000
    rng = np.random.RandomState(42)
    
    X_train = pd.DataFrame({
        "dti": rng.uniform(0.1, 0.6, n_samples),
        "income_confidence": rng.uniform(0.3, 1.0, n_samples),
        "payroll_consistency": rng.uniform(0.4, 1.0, n_samples),
        "fraud_score": rng.uniform(0.0, 0.5, n_samples),
        "identity_confidence": rng.uniform(0.3, 1.0, n_samples),
        "months_salary_detected": rng.uniform(1, 12, n_samples),
        "tenure_months": rng.choice([12, 24, 36, 48, 60], n_samples),
        "loan_to_income": rng.uniform(0.5, 3.0, n_samples),
        "income_level_normalized": rng.uniform(0.3, 1.0, n_samples)
    })
    
    # Create synthetic labels (default probability)
    # Higher DTI, lower confidence, lower consistency -> higher default
    y_train = (
        X_train["dti"] * 0.3 +
        (1 - X_train["income_confidence"]) * 0.2 +
        (1 - X_train["payroll_consistency"]) * 0.2 +
        X_train["fraud_score"] * 0.15 +
        (1 - X_train["identity_confidence"]) * 0.15
    )
    y_train = (y_train > 0.35).astype(int)  # Binary classification
    
    # Train model using GradientBoostingClassifier instead of LightGBM
    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Save model
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    logger.info(f"Model saved to {MODEL_PATH}")
    
    # Save metadata
    metadata = {
        "model_version": "score-v1",
        "training_date": datetime.utcnow().isoformat(),
        "n_features": X_train.shape[1],
        "n_samples": n_samples
    }
    with open(MODEL_METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    
    logger.info("Model training complete")
