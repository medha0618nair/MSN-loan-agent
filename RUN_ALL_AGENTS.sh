#!/bin/bash

# ========================================
# RUN ALL 6 AGENTS + ORCHESTRATOR
# ========================================
# Starts all agents in parallel background processes
# Kill them all with: pkill -f "python.*main.py"

set -e

REPO_ROOT="/Users/apple/Desktop/codered final/MSN-loan-agent"

echo "================================================"
echo "🚀 STARTING ALL AGENTS & ORCHESTRATOR"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to start an agent
start_agent() {
    local agent_name=$1
    local agent_path=$2
    local port=$3
    local main_file=${4:-"main.py"}
    
    echo -e "${BLUE}Starting $agent_name on port $port...${NC}"
    
    cd "$agent_path"
    
    # Activate venv if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Start in background
    python3 "$main_file" > "logs_${agent_name}.log" 2>&1 &
    local PID=$!
    
    echo -e "${GREEN}✓ $agent_name started (PID: $PID)${NC}"
    echo "$PID" > "${agent_name}.pid"
    
    sleep 2  # Give server time to start
}

# Create logs directory
mkdir -p "$REPO_ROOT/logs"

# ========================================
# START ALL 6 AGENTS
# ========================================

echo ""
echo "Starting all agents..."
echo ""

# 1. Intake Agent (port 8001) - NEW STRICT FLOW
start_agent "INTAKE_AGENT" \
    "$REPO_ROOT/agents/intake_agent" \
    "8001" \
    "main_strict_flow.py"

# 2. KYC Agent (port 8002)
start_agent "KYC_AGENT" \
    "$REPO_ROOT/agents/kyc_agent" \
    "8002" \
    "main.py"

# 3. Face Agent (port 8003)
start_agent "FACE_AGENT" \
    "$REPO_ROOT/agents/face-agent" \
    "8003" \
    "main.py"

# 4. Payslip Agent (port 8004)
start_agent "PAYSLIP_AGENT" \
    "$REPO_ROOT/agents/payslip-agent" \
    "8004" \
    "main.py"

# 5. Bank Agent (port 8005)
start_agent "BANK_AGENT" \
    "$REPO_ROOT/agents/bank-agent" \
    "8005" \
    "main.py"

# 6. Credit Agent (port 8006)
start_agent "CREDIT_AGENT" \
    "$REPO_ROOT/agents/credit-agent" \
    "8006" \
    "main.py"

echo ""
echo "================================================"
echo "✅ ALL AGENTS STARTED"
echo "================================================"
echo ""
echo "Agent Status:"
echo "  🟢 INTAKE AGENT  - http://localhost:8001"
echo "  🟢 KYC AGENT     - http://localhost:8002"
echo "  🟢 FACE AGENT    - http://localhost:8003"
echo "  🟢 PAYSLIP AGENT - http://localhost:8004"
echo "  🟢 BANK AGENT    - http://localhost:8005"
echo "  🟢 CREDIT AGENT  - http://localhost:8006"
echo ""

# ========================================
# START ORCHESTRATOR
# ========================================

sleep 3

echo -e "${BLUE}Starting ORCHESTRATOR on port 8000...${NC}"
cd "$REPO_ROOT"

if [ -d "venv_main" ]; then
    source venv_main/bin/activate
fi

python3 run_orchestrator_server.py > logs_orchestrator.log 2>&1 &
ORCH_PID=$!

echo -e "${GREEN}✓ ORCHESTRATOR started (PID: $ORCH_PID)${NC}"
echo "$ORCH_PID" > "orchestrator.pid"

echo ""
echo "================================================"
echo "✅ ORCHESTRATOR STARTED"
echo "================================================"
echo ""
echo "🟢 ORCHESTRATOR API - http://localhost:8000"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "================================================"
echo "📋 HOW TO SUBMIT A LOAN APPLICATION"
echo "================================================"
echo ""
echo "curl -X POST http://localhost:8000/process-application \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"applicant_info\": {"
echo "      \"name\": \"John Doe\","
echo "      \"email\": \"john@example.com\","
echo "      \"phone\": \"+91-9876543210\","
echo "      \"annual_income\": 4500000,"
echo "      \"current_employer\": \"Tech Corp\","
echo "      \"designation\": \"Manager\","
echo "      \"years_at_current_employer\": 5,"
echo "      \"loan_amount_requested\": 300000,"
echo "      \"loan_tenure_months\": 12"
echo "    }"
echo "  }'"
echo ""
echo "================================================"
echo "⚠️  TO STOP ALL AGENTS:"
echo "================================================"
echo ""
echo "pkill -f 'python.*main.py'"
echo ""
echo "Or individually:"
echo "  kill \$(cat INTAKE_AGENT.pid ORCHESTRATOR.pid ...)"
echo ""
echo "================================================"
echo "📊 WATCH LOGS:"
echo "================================================"
echo ""
echo "tail -f logs_*.log"
echo ""
