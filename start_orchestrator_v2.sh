#!/bin/bash
# Start Orchestrator v2 on port 9000

cd "$(dirname "$0")/orchestrator_agent"

echo "🚀 Starting Orchestrator v2 on port 9000..."
python3 main_v2.py &

ORCHESTRATOR_PID=$!
echo "Orchestrator PID: $ORCHESTRATOR_PID"
wait $ORCHESTRATOR_PID
