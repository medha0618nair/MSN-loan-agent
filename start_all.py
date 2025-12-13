#!/usr/bin/env python3
"""
Automated Startup - Start all agents and orchestrator server
Run: python start_all.py
"""

import os
import subprocess
import sys
import time
import signal
import atexit

BASE_DIR = "/Users/apple/Desktop/codered final/MSN-loan-agent"
AGENTS_DIR = os.path.join(BASE_DIR, "agents")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Create logs directory
os.makedirs(LOGS_DIR, exist_ok=True)

processes = []

def cleanup():
    """Kill all processes on exit"""
    print("\n\n🛑 Shutting down all services...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except:
            proc.kill()
    print("✅ All services stopped")

# Register cleanup on exit
atexit.register(cleanup)
signal.signal(signal.SIGINT, lambda sig, frame: exit(0))

def start_redis():
    """Start Redis if not running"""
    print("🔍 Checking Redis...")
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=redis"],
        capture_output=True, text=True
    )
    
    if "redis" not in result.stdout:
        print("🚀 Starting Redis...")
        subprocess.Popen(
            ["docker", "run", "-d", "-p", "6379:6379", "redis:7-alpine"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)
        print("✅ Redis started")
    else:
        print("✅ Redis already running")

def start_agent(agent_name, agent_path, port):
    """Start an agent"""
    print(f"🚀 Starting {agent_name} (Port {port})...")
    log_file = os.path.join(LOGS_DIR, f"{agent_name}.log")
    
    os.chdir(agent_path)
    with open(log_file, "w") as log:
        proc = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=log,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid  # Create new process group
        )
        processes.append(proc)
    
    time.sleep(2)
    print(f"✅ {agent_name} started (PID: {proc.pid})")
    
    os.chdir(BASE_DIR)

def main():
    print("=" * 60)
    print("🎬 MSN LOAN ORCHESTRATOR - STARTUP")
    print("=" * 60)
    print()
    
    # Start Redis
    start_redis()
    print()
    
    print("=" * 60)
    print("Starting 6 Agents...")
    print("=" * 60)
    print()
    
    # Start all agents
    try:
        start_agent("intake-agent", os.path.join(AGENTS_DIR, "intake_agent"), 8001)
        start_agent("kyc-agent", os.path.join(AGENTS_DIR, "kyc_agent"), 8002)
        start_agent("face-agent", os.path.join(AGENTS_DIR, "face-agent"), 8003)
        start_agent("payslip-agent", os.path.join(AGENTS_DIR, "payslip-agent"), 8004)
        start_agent("bank-agent", os.path.join(AGENTS_DIR, "bank-agent"), 8005)
        start_agent("credit-agent", os.path.join(AGENTS_DIR, "credit-agent"), 8006)
    except Exception as e:
        print(f"❌ Error starting agents: {e}")
        cleanup()
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Starting Orchestrator API Server")
    print("=" * 60)
    print()
    
    print("🚀 Starting API Server (Port 8000)...")
    
    # Start API server in foreground
    os.chdir(BASE_DIR)
    subprocess.run([sys.executable, "run_orchestrator_server.py"])

if __name__ == "__main__":
    main()
