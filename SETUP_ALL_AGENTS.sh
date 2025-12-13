#!/bin/bash

# ========================================
# SETUP ALL AGENTS - Multi-Python Environments
# ========================================
# This script sets up all 6 agents with Python 3.11
# Run this ONCE before running agents

set -e

REPO_ROOT="/Users/apple/Desktop/codered final/MSN-loan-agent"
PYTHON_311=$(which python3.11 || which python3 || which python)

echo "================================================"
echo "🚀 SETTING UP ALL 6 LOAN AGENTS"
echo "================================================"
echo ""
echo "Python Version: $PYTHON_311"
echo "Repository Root: $REPO_ROOT"
echo ""

# Check if Python 3.11+ is available
PYTHON_VERSION=$($PYTHON_311 --version 2>&1 | awk '{print $2}')
echo "✓ Using Python $PYTHON_VERSION"
echo ""

# ========================================
# 1. INTAKE AGENT
# ========================================
echo "📋 Setting up INTAKE AGENT (port 8001)..."
cd "$REPO_ROOT/agents/intake_agent"

if [ ! -d "venv" ]; then
    $PYTHON_311 -m venv venv
    echo "✓ Created virtual environment"
fi

source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Installed dependencies"
deactivate

# ========================================
# 2. KYC AGENT
# ========================================
echo "📋 Setting up KYC AGENT (port 8002)..."
cd "$REPO_ROOT/agents/kyc_agent"

if [ ! -d "venv" ]; then
    $PYTHON_311 -m venv venv
    echo "✓ Created virtual environment"
fi

source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Installed dependencies"
deactivate

# ========================================
# 3. FACE AGENT
# ========================================
echo "📋 Setting up FACE AGENT (port 8003)..."
cd "$REPO_ROOT/agents/face-agent"

if [ ! -d "venv" ]; then
    $PYTHON_311 -m venv venv
    echo "✓ Created virtual environment"
fi

source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Installed dependencies"
deactivate

# ========================================
# 4. PAYSLIP AGENT
# ========================================
echo "📋 Setting up PAYSLIP AGENT (port 8004)..."
cd "$REPO_ROOT/agents/payslip-agent"

if [ ! -d "venv" ]; then
    $PYTHON_311 -m venv venv
    echo "✓ Created virtual environment"
fi

source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Installed dependencies"
deactivate

# ========================================
# 5. BANK AGENT
# ========================================
echo "📋 Setting up BANK AGENT (port 8005)..."
cd "$REPO_ROOT/agents/bank-agent"

if [ ! -d "venv" ]; then
    $PYTHON_311 -m venv venv
    echo "✓ Created virtual environment"
fi

source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Installed dependencies"
deactivate

# ========================================
# 6. CREDIT AGENT
# ========================================
echo "📋 Setting up CREDIT AGENT (port 8006)..."
cd "$REPO_ROOT/agents/credit-agent"

if [ ! -d "venv" ]; then
    $PYTHON_311 -m venv venv
    echo "✓ Created virtual environment"
fi

source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Installed dependencies"
deactivate

# ========================================
# 7. MASTER ORCHESTRATOR
# ========================================
echo "📋 Setting up MASTER ORCHESTRATOR (port 8000)..."
cd "$REPO_ROOT"

if [ ! -d "venv_main" ]; then
    $PYTHON_311 -m venv venv_main
    echo "✓ Created virtual environment"
fi

source venv_main/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Installed dependencies"
deactivate

echo ""
echo "================================================"
echo "✅ ALL AGENTS SETUP COMPLETE"
echo "================================================"
echo ""
echo "Next step: Run all agents with:"
echo "  bash $REPO_ROOT/RUN_ALL_AGENTS.sh"
echo ""
