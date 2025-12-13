#!/bin/bash
# COMPLETE SYSTEM STARTUP - All services running permanently
# This script starts all agents and the orchestrator

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/.pids"

mkdir -p "$LOG_DIR"
mkdir -p "$PROJECT_DIR/data/conversations"
mkdir -p "$PROJECT_DIR/audit"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║    🚀 STARTING COMPLETE MULTI-AGENT LOAN SYSTEM               ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Function to start a service
start_service() {
    local name=$1
    local port=$2
    local script=$3
    
    echo "Starting $name on port $port..."
    cd "$PROJECT_DIR/$script"
    nohup python3 main_v2.py > "$LOG_DIR/${name}.log" 2>&1 &
    local pid=$!
    echo $pid >> "$PID_FILE"
    echo "  ✅ $name started (PID: $pid)"
    sleep 1
}

# Clean up old PIDs
> "$PID_FILE"

echo "📡 Starting Core Services:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start Intake Agent
start_service "Intake Agent" 8001 "agents/intake_agent"

# Start Orchestrator
start_service "Orchestrator" 9000 "orchestrator_agent"

echo ""
echo "📊 Starting Other Agents (if available):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start other agents if they exist
if [ -f "$PROJECT_DIR/agents/kyc_agent/main.py" ]; then
    start_service "KYC Agent" 8002 "agents/kyc_agent"
fi

if [ -f "$PROJECT_DIR/agents/face_agent/main.py" ]; then
    start_service "Face Agent" 8003 "agents/face_agent"
fi

if [ -f "$PROJECT_DIR/agents/payslip_agent/main.py" ]; then
    start_service "Payslip Agent" 8004 "agents/payslip_agent"
fi

if [ -f "$PROJECT_DIR/agents/bank_agent/main.py" ]; then
    start_service "Bank Agent" 8005 "agents/bank_agent"
fi

if [ -f "$PROJECT_DIR/agents/credit_agent/main.py" ]; then
    start_service "Credit Agent" 8006 "agents/credit_agent"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║  ✅ ALL SERVICES STARTED AND RUNNING                          ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "📋 SERVICES RUNNING:"
echo "  • Intake Agent        http://localhost:8001"
echo "  • Orchestrator        http://localhost:9000"
echo "  • KYC Agent           http://localhost:8002"
echo "  • Face Agent          http://localhost:8003"
echo "  • Payslip Agent       http://localhost:8004"
echo "  • Bank Agent          http://localhost:8005"
echo "  • Credit Agent        http://localhost:8006"
echo ""

echo "🧪 TEST HEALTH:"
echo "  curl http://localhost:9000/agents/status"
echo ""

echo "📝 SUBMIT APPLICATION:"
echo "  python3 submit_application_v2.py"
echo ""

echo "📊 VIEW LOGS:"
echo "  tail -f logs/intake.log"
echo "  tail -f logs/orchestrator.log"
echo ""

echo "⏹️  STOP ALL SERVICES:"
echo "  bash STOP_SYSTEM.sh"
echo ""

echo "⏳ Services will run indefinitely. Press Ctrl+C to stop..."
echo ""

# Wait for all processes
wait
