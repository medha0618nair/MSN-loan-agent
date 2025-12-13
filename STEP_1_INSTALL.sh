#!/bin/bash
# COPY & PASTE - Run these commands in order

# ============================================
# STEP 1: Install Dependencies (Run Once)
# ============================================

cd "/Users/apple/Desktop/codered final/MSN-loan-agent"

pip install -r orchestrator_requirements.txt
pip install fastapi uvicorn
pip install -r agents/intake_agent/requirements.txt
pip install -r agents/kyc_agent/requirements.txt
pip install -r agents/face-agent/requirements.txt
pip install -r agents/payslip-agent/requirements.txt
pip install -r agents/bank-agent/requirements.txt
pip install -r agents/credit-agent/requirements.txt

echo "✅ All dependencies installed"
