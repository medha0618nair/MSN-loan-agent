#!/usr/bin/env python3
"""
CLI tool for orchestrating multi-agent loan application processing.

Usage:
    python orchestrator_cli.py health                    # Check agent health
    python orchestrator_cli.py process <app_id> <config_file>  # Process application
    python orchestrator_cli.py status <app_id>           # Check application status
    python orchestrator_cli.py report <app_id>           # Generate application report
    python orchestrator_cli.py demo                      # Run demo application
"""

import argparse
import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class OrchestratorCLI:
    """Command-line interface for orchestrator."""
    
    def __init__(self):
        """Initialize CLI."""
        self.orchestrator = None
    
    async def health_check(self, args) -> None:
        """Check health of all agents."""
        print("🏥 Checking agent health...\n")
        
        from complete_orchestrator import LoanOrchestratorV2
        orchestrator = LoanOrchestratorV2()
        
        try:
            health_status = await orchestrator.check_all_agents_health()
            
            print("Agent Status:")
            print("-" * 50)
            
            all_healthy = True
            for agent_name, is_healthy in health_status.items():
                status_icon = "✅" if is_healthy else "❌"
                status_text = "Healthy" if is_healthy else "Unhealthy"
                print(f"{status_icon} {agent_name:15} - {status_text}")
                if not is_healthy:
                    all_healthy = False
            
            print("-" * 50)
            if all_healthy:
                print("\n✅ All agents are healthy and ready!")
                return 0
            else:
                print("\n⚠️  Some agents are not responding. Check if services are running.")
                return 1
        
        except Exception as e:
            print(f"❌ Error checking health: {e}")
            return 1
    
    async def process_application(self, args) -> None:
        """Process a loan application."""
        app_id = args.app_id
        config_file = args.config_file
        
        print(f"📋 Processing application: {app_id}\n")
        
        # Load configuration
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file not found: {config_file}")
            return 1
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in config file: {config_file}")
            return 1
        
        from complete_orchestrator import LoanOrchestratorV2
        
        try:
            orchestrator = LoanOrchestratorV2()
            
            # Extract applicant info and documents
            applicant_info = config.get("applicant_info", {})
            documents = config.get("documents", {})
            
            print(f"👤 Applicant: {applicant_info.get('name', 'Unknown')}")
            print(f"📄 Documents: {', '.join(documents.keys())}\n")
            
            # Process application
            result = await orchestrator.process_complete_application(
                app_id,
                applicant_info,
                documents
            )
            
            if result.get("status") == "completed":
                print(f"✅ Application processed successfully!\n")
                print("Results:")
                print("-" * 50)
                
                # Print summary
                for agent_name, agent_result in result.get("results", {}).items():
                    print(f"\n{agent_name.upper()}:")
                    if isinstance(agent_result, dict):
                        print(json.dumps(agent_result, indent=2)[:500] + "...")
                    else:
                        print(str(agent_result)[:500] + "...")
                
                print("\n" + "-" * 50)
                print(f"\n📄 Full report saved to: {app_id}_report.json")
                
                # Save full report
                with open(f"{app_id}_report.json", 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                
                return 0
            else:
                print(f"❌ Application processing failed")
                print(json.dumps(result, indent=2, default=str))
                return 1
        
        except Exception as e:
            print(f"❌ Error processing application: {e}")
            return 1
    
    async def get_status(self, args) -> None:
        """Get application status."""
        app_id = args.app_id
        
        print(f"📊 Application Status: {app_id}\n")
        
        from complete_orchestrator import LoanOrchestratorV2
        
        try:
            orchestrator = LoanOrchestratorV2()
            status = orchestrator.get_application_status(app_id)
            
            if "error" in status:
                print(f"⚠️  Application not found")
                return 1
            
            print(f"Status: {status.get('status', 'unknown')}")
            print(f"Created: {status.get('created_at', 'N/A')}")
            
            if status.get('status') == 'completed':
                print(f"Completed: {status.get('completed_at', 'N/A')}")
            
            print("\nProcessing Results:")
            for agent_name, result in status.get('results', {}).items():
                print(f"  • {agent_name}: {'✅' if result else '⏳'}")
            
            return 0
        
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return 1
    
    async def generate_report(self, args) -> None:
        """Generate application report."""
        app_id = args.app_id
        
        from complete_orchestrator import LoanOrchestratorV2
        
        try:
            orchestrator = LoanOrchestratorV2()
            report = orchestrator.generate_report(app_id)
            
            print(report)
            
            # Save to file
            report_file = f"{app_id}_report.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            
            print(f"\n📄 Report saved to: {report_file}")
            return 0
        
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return 1
    
    async def run_demo(self, args) -> None:
        """Run demo application."""
        print("🎬 Running demo application processing...\n")
        
        from complete_orchestrator import LoanOrchestratorV2
        
        try:
            orchestrator = LoanOrchestratorV2()
            
            # Demo application
            app_id = "DEMO-" + Path.cwd().name + "-001"
            applicant_info = {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+91-9876543210",
                "employment_status": "salaried",
                "annual_income": 800000,
                "current_employer": "TechCorp Inc",
                "designation": "Senior Engineer",
                "years_at_current_employer": 5,
                "cibil_score": 750,
                "loan_amount_requested": 500000,
                "loan_tenure_months": 60,
                "loan_purpose": "Home Purchase"
            }
            
            print(f"📋 Application ID: {app_id}")
            print(f"👤 Applicant: {applicant_info['name']}")
            print(f"💼 Employer: {applicant_info['current_employer']}")
            print(f"💰 Annual Income: ₹{applicant_info['annual_income']:,.0f}")
            print(f"📊 CIBIL Score: {applicant_info['cibil_score']}")
            print(f"🏦 Loan Amount: ₹{applicant_info['loan_amount_requested']:,.0f}")
            print("\n" + "="*50 + "\n")
            
            # Check health first
            print("1️⃣  Checking agent health...")
            health = await orchestrator.check_all_agents_health()
            
            healthy_agents = sum(1 for v in health.values() if v)
            print(f"   ✅ {healthy_agents}/{len(health)} agents healthy\n")
            
            if healthy_agents < len(health):
                print("   ⚠️  Some agents are not running. Demo will use mock responses.\n")
            
            # Process application
            print("2️⃣  Processing application through all agents...")
            print("   ├─ Intake Agent")
            print("   ├─ Face Verification")
            print("   ├─ KYC Processing")
            print("   ├─ Payslip Verification")
            print("   ├─ Bank Statement Analysis")
            print("   ├─ Credit Scoring")
            print("   └─ Application Submission")
            print()
            
            # Simulate processing
            result = {
                "application_id": app_id,
                "status": "completed",
                "created_at": "2024-01-15T10:30:00.000Z",
                "completed_at": "2024-01-15T10:45:00.000Z",
                "applicant_info": applicant_info,
                "results": {
                    "intake": {
                        "status": "success",
                        "conversation_id": f"conv-{app_id}",
                        "slots_collected": ["name", "email", "phone", "employment_status", "income"],
                        "completion_percentage": 100
                    },
                    "face": {
                        "status": "success",
                        "verified": True,
                        "liveness_score": 0.98,
                        "match_confidence": 0.99
                    },
                    "kyc": {
                        "status": "success",
                        "documents_verified": ["aadhaar", "pan"],
                        "verification_score": 0.99
                    },
                    "income": {
                        "payslip": {
                            "status": "success",
                            "monthly_salary": 66666.67,
                            "annual_salary": 800000
                        },
                        "bank_statement": {
                            "status": "success",
                            "average_balance": 150000,
                            "transaction_volume": 2400000
                        }
                    },
                    "credit": {
                        "status": "success",
                        "credit_score": 750,
                        "risk_level": "Low",
                        "recommended_loan_amount": 600000,
                        "recommended_tenure_months": 60,
                        "interest_rate": 8.5
                    }
                }
            }
            
            print("✅ Application processed successfully!\n")
            print("="*50)
            print("\n📊 SUMMARY REPORT\n")
            
            print("✅ Face Verification:")
            print(f"   Liveness Score: {result['results']['face']['liveness_score']*100:.1f}%")
            print(f"   Match Confidence: {result['results']['face']['match_confidence']*100:.1f}%\n")
            
            print("✅ KYC Verification:")
            print(f"   Documents: {', '.join(result['results']['kyc']['documents_verified'])}")
            print(f"   Verification Score: {result['results']['kyc']['verification_score']*100:.1f}%\n")
            
            print("✅ Income Verification:")
            print(f"   Monthly Salary: ₹{result['results']['income']['payslip']['monthly_salary']:,.2f}")
            print(f"   Annual Salary: ₹{result['results']['income']['payslip']['annual_salary']:,.0f}")
            print(f"   Average Bank Balance: ₹{result['results']['income']['bank_statement']['average_balance']:,.0f}\n")
            
            print("✅ Credit Scoring:")
            print(f"   Credit Score: {result['results']['credit']['credit_score']}")
            print(f"   Risk Level: {result['results']['credit']['risk_level']}")
            print(f"   Recommended Loan: ₹{result['results']['credit']['recommended_loan_amount']:,.0f}")
            print(f"   Interest Rate: {result['results']['credit']['interest_rate']}%\n")
            
            print("="*50)
            print("\n✅ Application approved for processing!")
            print(f"\n📄 Full report saved to: {app_id}_demo_report.json")
            
            # Save report
            with open(f"{app_id}_demo_report.json", 'w') as f:
                json.dump(result, f, indent=2)
            
            return 0
        
        except Exception as e:
            print(f"❌ Error running demo: {e}")
            return 1


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Orchestrator CLI for Multi-Agent Loan Processing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Check agent health:
    python orchestrator_cli.py health
  
  Process application:
    python orchestrator_cli.py process APP-001 config.json
  
  Get application status:
    python orchestrator_cli.py status APP-001
  
  Generate report:
    python orchestrator_cli.py report APP-001
  
  Run demo:
    python orchestrator_cli.py demo
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Health check command
    subparsers.add_parser('health', help='Check agent health')
    
    # Process application command
    process_parser = subparsers.add_parser('process', help='Process loan application')
    process_parser.add_argument('app_id', help='Application ID')
    process_parser.add_argument('config_file', help='JSON config file with applicant and document info')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check application status')
    status_parser.add_argument('app_id', help='Application ID')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate application report')
    report_parser.add_argument('app_id', help='Application ID')
    
    # Demo command
    subparsers.add_parser('demo', help='Run demo application')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = OrchestratorCLI()
    
    if args.command == 'health':
        return await cli.health_check(args)
    elif args.command == 'process':
        return await cli.process_application(args)
    elif args.command == 'status':
        return await cli.get_status(args)
    elif args.command == 'report':
        return await cli.generate_report(args)
    elif args.command == 'demo':
        return await cli.run_demo(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
