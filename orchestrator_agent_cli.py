#!/usr/bin/env python3
"""
Master Orchestrator CLI - Simple command-line interface

Usage:
    python orchestrator_agent.py health                    # Check all agent health
    python orchestrator_agent.py process APP-001 config.json  # Process application
    python orchestrator_agent.py status APP-001            # Check status
    python orchestrator_agent.py demo                      # Run demo
"""

import argparse
import json
import asyncio
import sys
from pathlib import Path

from orchestrator_agent import MasterOrchestrator


async def cmd_health():
    """Check health of all agents."""
    print("\n🏥 CHECKING AGENT HEALTH\n")
    print("="*70)
    
    orchestrator = MasterOrchestrator()
    health_status = await orchestrator.check_all_agents_health()
    
    print("\nAgent Status:")
    print("-"*70)
    
    all_healthy = True
    for agent, status in health_status.items():
        icon = "✅" if status else "❌"
        status_text = "HEALTHY" if status else "OFFLINE"
        print(f"{icon} {agent.upper():15} - {status_text}")
        if not status:
            all_healthy = False
    
    print("-"*70)
    
    if all_healthy:
        print("\n✅ All agents are healthy and ready!\n")
        return 0
    else:
        print("\n⚠️  Some agents are offline. Please start them first.\n")
        print("Start agents with:")
        print("  docker-compose up -d\n")
        return 1


async def cmd_process(app_id: str, config_file: str):
    """Process a loan application."""
    print(f"\n📋 PROCESSING APPLICATION: {app_id}\n")
    print("="*70)
    
    # Load configuration
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_file}\n")
        return 1
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in config file: {config_file}\n")
        return 1
    
    orchestrator = MasterOrchestrator()
    
    applicant_data = config.get("applicant_info", {})
    documents = config.get("documents", {})
    
    print(f"Applicant: {applicant_data.get('name', 'Unknown')}")
    print(f"Documents: {', '.join(documents.keys())}")
    print("\n" + "="*70 + "\n")
    
    try:
        # Process application
        result = await orchestrator.process_application(
            app_id,
            applicant_data,
            documents
        )
        
        # Print summary
        print("\n" + "="*70)
        print("FINAL DECISION")
        print("="*70)
        
        final_status = result.get("final_status", "UNKNOWN")
        loan_amount = result.get("recommendation", {}).get("loan_amount", "N/A")
        interest_rate = result.get("recommendation", {}).get("interest_rate", "N/A")
        
        status_icon = {
            "APPROVED": "✅",
            "REJECTED": "❌",
            "MANUAL_REVIEW": "⚠️"
        }.get(final_status, "❓")
        
        print(f"\nStatus: {status_icon} {final_status}")
        print(f"Reason: {result.get('reason', 'N/A')}")
        print(f"Loan Amount: ₹{loan_amount}")
        print(f"Interest Rate: {interest_rate}%")
        
        print("\n" + "="*70 + "\n")
        
        # Save report
        report_file = f"{app_id}_result.json"
        with open(report_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"📄 Full report saved to: {report_file}\n")
        return 0
    
    except Exception as e:
        print(f"\n❌ Error processing application: {e}\n")
        return 1


async def cmd_status(app_id: str):
    """Check application status."""
    print(f"\n📊 APPLICATION STATUS: {app_id}\n")
    print("="*70)
    
    orchestrator = MasterOrchestrator()
    
    # Note: In real implementation, would fetch from database
    # For now, just show the structure
    print("\nTo get application status in production:")
    print("  - Store results in database")
    print("  - Query by application_id")
    print("  - Return current processing stage and evidence\n")
    
    return 0


async def cmd_demo():
    """Run demo application."""
    print("\n🎬 RUNNING DEMO APPLICATION\n")
    print("="*70)
    
    orchestrator = MasterOrchestrator()
    
    # Check health first
    print("\n1️⃣  Checking agent health...")
    health = await orchestrator.check_all_agents_health()
    healthy_count = sum(1 for v in health.values() if v)
    print(f"   Result: {healthy_count}/{len(health)} agents healthy")
    
    if healthy_count < len(health):
        print("\n   ⚠️  Some agents are not running. Using mock data.\n")
    
    # Demo application
    app_id = "DEMO-20240115-001"
    applicant_data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "+91-9123456789",
        "employment_status": "salaried",
        "annual_income": 1000000,
        "current_employer": "FinTech Corp",
        "designation": "Product Manager",
        "years_at_current_employer": 4,
        "loan_amount_requested": 750000,
        "loan_tenure_months": 60
    }
    
    documents = {
        "aadhaar": "/demo/aadhaar.pdf",
        "selfie": "/demo/selfie.jpg",
        "payslip": "/demo/payslip.pdf",
        "bank_statement": "/demo/bank_statement.pdf"
    }
    
    print(f"\n2️⃣  Application Details:")
    print(f"   ID: {app_id}")
    print(f"   Applicant: {applicant_data['name']}")
    print(f"   Income: ₹{applicant_data['annual_income']:,.0f}")
    print(f"   Loan Amount: ₹{applicant_data['loan_amount_requested']:,.0f}")
    
    print(f"\n3️⃣  Processing through all stages...")
    print("="*70)
    
    try:
        result = await orchestrator.process_application(
            app_id,
            applicant_data,
            documents
        )
        
        print("\n" + "="*70)
        print("DEMO RESULT")
        print("="*70)
        
        print(f"\n✅ Status: {result['final_status']}")
        print(f"📝 Reason: {result['reason']}")
        print(f"💰 Loan Amount: ₹{result['recommendation']['loan_amount']:,.0f}")
        print(f"📊 Interest Rate: {result['recommendation']['interest_rate']}%")
        
        print("\n" + "="*70 + "\n")
        
        # Save demo result
        with open(f"{app_id}_result.json", 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"📄 Demo result saved to: {app_id}_result.json\n")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Demo failed: {e}\n")
        return 1


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Master Orchestrator - Multi-Agent Loan Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Check all agents:
    python orchestrator_agent.py health
  
  Process application:
    python orchestrator_agent.py process APP-001 config.json
  
  Check status:
    python orchestrator_agent.py status APP-001
  
  Run demo:
    python orchestrator_agent.py demo

Workflow Order:
  1. Intake Agent    (:8001) - Collect info
  2. KYC Agent       (:8002) - Verify identity
  3. Face Agent      (:8003) - Verify face
  4. Payslip Agent   (:8004) - Verify income
  5. Bank Agent      (:8005) - Analyze financials
  6. Credit Agent    (:8006) - Final decision
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Health command
    subparsers.add_parser('health', help='Check agent health')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process application')
    process_parser.add_argument('app_id', help='Application ID')
    process_parser.add_argument('config_file', help='JSON config file')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check status')
    status_parser.add_argument('app_id', help='Application ID')
    
    # Demo command
    subparsers.add_parser('demo', help='Run demo')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'health':
            return await cmd_health()
        elif args.command == 'process':
            return await cmd_process(args.app_id, args.config_file)
        elif args.command == 'status':
            return await cmd_status(args.app_id)
        elif args.command == 'demo':
            return await cmd_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
