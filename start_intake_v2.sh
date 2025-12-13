#!/bin/bash
# Start Intake Agent v2 on port 8001

cd "$(dirname "$0")/agents/intake_agent"

echo "🚀 Starting Intake Agent v2 on port 8001..."
python3 main_v2.py &

INTAKE_PID=$!
echo "Intake Agent PID: $INTAKE_PID"
wait $INTAKE_PID
