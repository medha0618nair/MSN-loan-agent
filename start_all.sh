#!/bin/bash

# Automated Startup Script - Start all agents and orchestrator server
# Run this once to start everything

set -e

BASE_DIR="/Users/apple/Desktop/codered final/MSN-loan-agent"
cd "$BASE_DIR"

echo "================================"
echo "🚀 STARTING LOAN ORCHESTRATOR"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi

echo -e "${YELLOW}✓ Python3 found$(python3 --version)${NC}"
echo ""

# Check Redis
echo -e "${YELLOW}Checking Redis...${NC}"
if docker ps | grep -q redis; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${YELLOW}Starting Redis...${NC}"
    docker run -d -p 6379:6379 redis:7-alpine > /dev/null 2>&1
    sleep 2
    echo -e "${GREEN}✓ Redis started${NC}"
fi
echo ""

# Create logs directory
mkdir -p logs

# Function to start an agent
start_agent() {
    local agent_name=$1
    local agent_path=$2
    local port=$3
    
    echo -e "${YELLOW}Starting $agent_name (Port $port)...${NC}"
    cd "$agent_path"
    
    # Start in background and redirect output to log file
    python main.py > "../../logs/${agent_name}.log" 2>&1 &
    local pid=$!
    
    echo -e "${GREEN}✓ $agent_name started (PID: $pid)${NC}"
    sleep 2
    
    cd "$BASE_DIR"
}

echo "================================"
echo "Starting 6 Agents..."
echo "================================"
echo ""

# Start all agents
start_agent "intake-agent" "$BASE_DIR/agents/intake_agent" 8001
start_agent "kyc-agent" "$BASE_DIR/agents/kyc_agent" 8002
start_agent "face-agent" "$BASE_DIR/agents/face-agent" 8003
start_agent "payslip-agent" "$BASE_DIR/agents/payslip-agent" 8004
start_agent "bank-agent" "$BASE_DIR/agents/bank-agent" 8005
start_agent "credit-agent" "$BASE_DIR/agents/credit-agent" 8006

echo ""
echo "================================"
echo "Starting Orchestrator API Server"
echo "================================"
echo ""

cd "$BASE_DIR"
echo -e "${YELLOW}Starting API Server (Port 8000)...${NC}"

# Start API server in foreground (so you can see output)
python run_orchestrator_server.py

echo ""
echo -e "${GREEN}✅ ALL SYSTEMS RUNNING${NC}"
echo ""
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
echo "Agent Logs: ./logs/"
echo ""
