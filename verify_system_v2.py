#!/usr/bin/env python3
"""
System v2 Verification Script
Check that all components are in place
"""

import os
import sys
from pathlib import Path

def check_file(filepath, description):
    """Check if file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}")
    return exists

def main():
    print("\n" + "="*70)
    print("🔍 SYSTEM v2 VERIFICATION")
    print("="*70 + "\n")
    
    base_dir = "/Users/apple/Desktop/codered final/MSN-loan-agent"
    
    all_good = True
    
    # Section A: Intake Agent
    print("📋 SECTION A: INTAKE AGENT v2\n")
    all_good &= check_file(f"{base_dir}/agents/intake_agent/chat_flow_v2.py", "chat_flow_v2.py (Flow + Validators)")
    all_good &= check_file(f"{base_dir}/agents/intake_agent/storage_v2.py", "storage_v2.py (State Persistence)")
    all_good &= check_file(f"{base_dir}/agents/intake_agent/main_v2.py", "main_v2.py (FastAPI Server)")
    
    # Section B: Orchestrator
    print("\n📋 SECTION B: ORCHESTRATOR v2\n")
    all_good &= check_file(f"{base_dir}/orchestrator_agent/config_v2.py", "config_v2.py (Configuration)")
    all_good &= check_file(f"{base_dir}/orchestrator_agent/main_v2.py", "main_v2.py (FastAPI Server)")
    
    # Section C: Startup Scripts
    print("\n📋 SECTION C: STARTUP SCRIPTS\n")
    all_good &= check_file(f"{base_dir}/START_SYSTEM_v2.sh", "START_SYSTEM_v2.sh (Start All)")
    all_good &= check_file(f"{base_dir}/start_intake_v2.sh", "start_intake_v2.sh (Start Intake)")
    all_good &= check_file(f"{base_dir}/start_orchestrator_v2.sh", "start_orchestrator_v2.sh (Start Orchestrator)")
    
    # Section D: Client
    print("\n📋 SECTION D: CLIENT\n")
    all_good &= check_file(f"{base_dir}/submit_application_v2.py", "submit_application_v2.py (Client App)")
    
    # Section E: Documentation
    print("\n📋 SECTION E: DOCUMENTATION\n")
    all_good &= check_file(f"{base_dir}/SYSTEM_v2_README.md", "SYSTEM_v2_README.md (Full Docs)")
    all_good &= check_file(f"{base_dir}/IMPLEMENTATION_SUMMARY_v2.md", "IMPLEMENTATION_SUMMARY_v2.md (Summary)")
    all_good &= check_file(f"{base_dir}/QUICK_START_v2.md", "QUICK_START_v2.md (Quick Start)")
    
    # Results
    print("\n" + "="*70)
    if all_good:
        print("✅ ALL FILES PRESENT - System v2 is ready to run!")
        print("="*70 + "\n")
        print("🚀 Next steps:")
        print("  1. cd \"/Users/apple/Desktop/codered final/MSN-loan-agent\"")
        print("  2. bash START_SYSTEM_v2.sh")
        print("  3. python3 submit_application_v2.py")
        print("\n" + "="*70 + "\n")
        return 0
    else:
        print("❌ SOME FILES MISSING - Check above")
        print("="*70 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
