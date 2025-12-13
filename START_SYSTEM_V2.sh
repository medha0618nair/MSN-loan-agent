#!/bin/bash
# Start all agents and orchestrator v2
# Intake (8001) → Orchestrator (9000) → Parallel Agents → Credit Agent

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

echo "==============================================="
echo "🚀 STARTING MULTI-AGENT SYSTEM v2"
echo "==============================================="
echo ""
echo "📋 Architecture:"
echo "  - Intake Agent (8001)"
echo "  - Orchestrator (9000)"
echo "  - KYC Agent (8002)"
echo "  - Face Agent (8003)"
echo "  - Payslip Agent (8004)"
echo "  - Bank Agent (8005)"
echo "  - Credit Agent (8006)"
echo ""

# Function to kill all processes on exit
cleanup() {
    echo ""
    echo "⚠️  Shutting down..."
    kill $(jobs -p) 2>/dev/null || true
}
trap cleanup EXIT

# Start Intake Agent
echo "1️⃣  Starting Intake Agent on port 8001..."
cd "$PROJECT_DIR/agents/intake_agent"
python3 main_v2.py > "$LOG_DIR/intake.log" 2>&1 &
INTAKE_PID=$!
sleep 2

# Start Orchestrator
echo "2️⃣  Starting Orchestrator on port 9000..."
cd "$PROJECT_DIR/orchestrator_agent"
python3 main_v2.py > "$LOG_DIR/orchestrator.log" 2>&1 &
ORCHESTRATOR_PID=$!
sleep 2

# Start other agents (use existing ones if available)
echo "3️⃣  Starting other agents..."
cd "$PROJECT_DIR/agents"

# KYC Agent
if [ -f "kyc_agent/main.py" ]; then
    echo "   - KYC Agent (8002)..."
    cd kyc_agent && python3 main.py > "$LOG_DIR/kyc.log" 2>&1 &
    cd ..
fi

# Face Agent
if [ -f "face_agent/main.py" ]; then
    echo "   - Face Agent (8003)..."
    cd face_agent && python3 main.py > "$LOG_DIR/face.log" 2>&1 &
    cd ..
fi

# Payslip Agent
if [ -f "payslip_agent/main.py" ]; then
    echo "   - Payslip Agent (8004)..."
    cd payslip_agent && python3 main.py > "$LOG_DIR/payslip.log" 2>&1 &
    cd ..
fi

# Bank Agent
if [ -f "bank_agent/main.py" ]; then
    echo "   - Bank Agent (8005)..."
    cd bank_agent && python3 main.py > "$LOG_DIR/bank.log" 2>&1 &
    cd ..
fi

# Credit Agent
if [ -f "credit_agent/main.py" ]; then
    echo "   - Credit Agent (8006)..."
    cd credit_agent && python3 main.py > "$LOG_DIR/credit.log" 2>&1 &
    cd ..
fi

echo ""
echo "✅ All agents started!"
echo ""
echo "📊 Monitor logs:"
echo "   tail -f $LOG_DIR/intake.log"
echo "   tail -f $LOG_DIR/orchestrator.log"
echo ""
echo "🧪 Test endpoints:"
echo "   curl http://localhost:8001/health    # Intake"
echo "   curl http://localhost:9000/health    # Orchestrator"
echo "   curl http://localhost:9000/agents/status"
echo ""
echo "🎯 Submit application:"
echo "   python3 submit_application_v2.py"
echo ""
echo "⏳ Press Ctrl+C to stop all services..."
echo ""

wait
