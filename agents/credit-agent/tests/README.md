# Credit Scoring Agent Tests

This directory contains comprehensive unit tests for the credit scoring service.

## Running Tests

```bash
# Run all tests
pytest test_scoring.py -v

# Run specific test
pytest test_scoring.py::TestFeatureEngineering::test_monthly_income_bank_preferred -v

# Run with coverage
pytest test_scoring.py --cov=.. --cov-report=html

# Run with detailed output
pytest test_scoring.py -v -s
```

## Test Coverage

- **TestFeatureEngineering** (8 tests)
  - Monthly income selection (bank vs payslip preference)
  - Missing income handling
  - Confidence score calculation
  - DTI and LTI computation

- **TestScoringRules** (12 tests)
  - Sufficient evidence validation
  - Fraud flag detection (low, medium, high)
  - Max eligible loan calculation
  - Tenure recommendation logic
  - PD-to-decision mapping

- **TestProbabilityCalculation** (3 tests)
  - Logistic function behavior
  - Default probability for good/risky profiles

- **TestExplanationTokens** (1 test)
  - Explanation token generation

- **TestScoringModel** (2 tests)
  - Model loading and initialization
  - Prediction output validation

## Expected Test Results

All tests should pass (~27 assertions):
```
test_scoring.py::TestFeatureEngineering::test_monthly_income_bank_preferred PASSED
test_scoring.py::TestFeatureEngineering::test_monthly_income_fallback_to_payslip PASSED
test_scoring.py::TestFeatureEngineering::test_monthly_income_missing PASSED
...
======================== 27 passed in 1.25s ========================
```
