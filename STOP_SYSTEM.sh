#!/bin/bash
# Stop all running services

echo "⏹️  Stopping all services..."

# Kill all Python processes running main_v2.py
pkill -f "python3 main_v2" || true

# Kill any processes from .pids file
if [ -f .pids ]; then
    while IFS= read -r pid; do
        kill $pid 2>/dev/null || true
    done < .pids
    rm .pids
fi

sleep 1

echo "✅ All services stopped"
echo ""

# Show remaining Python processes
echo "Remaining Python processes:"
ps aux | grep python3 | grep -v grep || echo "  (none)"
