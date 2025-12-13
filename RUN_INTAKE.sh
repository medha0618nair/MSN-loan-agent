#!/bin/bash
# Simple startup - just run one agent at a time to test

set -e

BASE="/Users/apple/Desktop/codered final/MSN-loan-agent"

echo "🚀 Starting Redis..."
docker run -d -p 6379:6379 redis:7-alpine 2>/dev/null || echo "Redis already running"
sleep 2

echo "🎬 Starting Intake Agent..."
cd "$BASE/agents/intake_agent"
python3 main.py
