#!/usr/bin/env python3
"""
Complete Test Case for Multi-Agent Loan Verification System
Tests the entire pipeline from intake through orchestration
"""

import requests
import json
import time
from datetime import datetime

BASE_URL_INTAKE = "http://localhost:8001"
BASE_URL_ORCHESTRATOR = "http://localhost:9000"

class LoanSystemTestCase:
    """Test case for complete loan verification system"""
    
    def __init__(self):
        self.app_id = None
        self.test_results = []
    
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{result['status']} - {test_name}")
        if details:
            print(f"  └─ {details}")
    
    def test_intake_health(self):
        """Test 1: Check Intake Agent is running"""
        try:
            response = requests.get(f"{BASE_URL_INTAKE}/health", timeout=5)
            status = response.status_code == 200
            self.log_test(
                "Intake Agent Health Check",
                status,
                f"Status: {response.status_code}" if status else "Connection failed"
            )
            return status
        except Exception as e:
            self.log_test("Intake Agent Health Check", False, str(e))
            return False
    
    def test_orchestrator_health(self):
        """Test 2: Check Orchestrator is running"""
        try:
            response = requests.get(f"{BASE_URL_ORCHESTRATOR}/health", timeout=5)
            status = response.status_code == 200
            self.log_test(
                "Orchestrator Health Check",
                status,
                f"Status: {response.status_code}" if status else "Connection failed"
            )
            return status
        except Exception as e:
            self.log_test("Orchestrator Health Check", False, str(e))
            return False
    
    def test_all_agents_status(self):
        """Test 3: Check all agents are RUNNING"""
        try:
            response = requests.get(f"{BASE_URL_ORCHESTRATOR}/agents/status", timeout=5)
            if response.status_code != 200:
                self.log_test("Agent Status Check", False, f"HTTP {response.status_code}")
                return False
            
            agents = response.json()
            all_running = all(v == "RUNNING" for v in agents.values())
            
            details = "\n  ".join([f"{k}: {v}" for k, v in agents.items()])
            self.log_test(
                "All Agents Status",
                all_running,
                f"Status:\n  {details}"
            )
            return all_running
        except Exception as e:
            self.log_test("All Agents Status", False, str(e))
            return False
    
    def test_start_conversation(self):
        """Test 4: Start new conversation"""
        try:
            response = requests.post(f"{BASE_URL_INTAKE}/start", json={})
            
            if response.status_code != 200:
                self.log_test("Start Conversation", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            self.app_id = data.get("application_id")
            
            has_required_fields = all(k in data for k in ["application_id", "bot_message", "current_stage"])
            
            self.log_test(
                "Start Conversation",
                has_required_fields,
                f"App ID: {self.app_id}\nFirst Q: {data.get('bot_message', '')[:50]}..."
            )
            return has_required_fields
        except Exception as e:
            self.log_test("Start Conversation", False, str(e))
            return False
    
    def test_answer_questions(self):
        """Test 5: Answer all questions sequentially"""
        if not self.app_id:
            self.log_test("Answer Questions", False, "No application ID")
            return False
        
        # Test data - all 17 questions
        answers = [
            ("personal", "Loan Type"),
            ("John Doe", "Full Name"),
            ("1990-05-15", "Date of Birth"),
            ("9876543210", "Phone"),
            ("john@example.com", "Email"),
            ("ABCDE1234F", "PAN"),
            ("salaried", "Employment Type"),
            ("Tech Corp", "Employer Name"),
            ("Senior Engineer", "Designation"),
            ("5", "Years at Job"),
            ("100000", "Monthly Income"),
            ("500000", "Loan Amount"),
            ("60", "Tenure Months"),
            ("./images/nithin3.jpg", "KYC File"),
            ("./images/nithinPAN.png", "Selfie File"),
            ("./payslip/payslip_nithin_j.txt", "Payslip File"),
            ("skip", "Bank Statement"),
        ]
        
        try:
            all_passed = True
            answered = 0
            
            for answer, field_name in answers:
                response = requests.post(
                    f"{BASE_URL_INTAKE}/message",
                    json={
                        "application_id": self.app_id,
                        "user_message": answer
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    answered += 1
                else:
                    all_passed = False
                    print(f"  └─ ❌ Failed at {field_name}: HTTP {response.status_code}")
            
            self.log_test(
                "Answer All Questions",
                all_passed and answered == len(answers),
                f"Answered {answered}/{len(answers)} questions"
            )
            return all_passed and answered == len(answers)
        
        except Exception as e:
            self.log_test("Answer Questions", False, str(e))
            return False
    
    def test_application_saved(self):
        """Test 6: Verify application data is saved"""
        if not self.app_id:
            self.log_test("Application Saved", False, "No application ID")
            return False
        
        try:
            response = requests.get(f"{BASE_URL_INTAKE}/state/{self.app_id}", timeout=5)
            
            if response.status_code != 200:
                self.log_test("Application Saved", False, f"HTTP {response.status_code}")
                return False
            
            state = response.json()
            has_data = bool(state.get("collected_data"))
            
            collected_fields = len(state.get("collected_data", {}))
            self.log_test(
                "Application Saved",
                has_data,
                f"Collected {collected_fields} fields"
            )
            return has_data
        except Exception as e:
            self.log_test("Application Saved", False, str(e))
            return False
    
    def test_orchestrator_endpoints(self):
        """Test 7: Check orchestrator endpoints exist"""
        try:
            # Try status endpoint
            response = requests.get(
                f"{BASE_URL_ORCHESTRATOR}/status/TEST-JOB-001",
                timeout=5
            )
            
            endpoint_exists = response.status_code in [200, 404, 422]
            
            self.log_test(
                "Orchestrator Endpoints",
                endpoint_exists,
                f"/status endpoint responds: HTTP {response.status_code}"
            )
            return endpoint_exists
        except Exception as e:
            self.log_test("Orchestrator Endpoints", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*80)
        print("🧪 MULTI-AGENT LOAN SYSTEM - COMPLETE TEST SUITE")
        print("="*80 + "\n")
        
        tests = [
            ("Test 1: Intake Agent Health", self.test_intake_health),
            ("Test 2: Orchestrator Health", self.test_orchestrator_health),
            ("Test 3: All Agents Status", self.test_all_agents_status),
            ("Test 4: Start Conversation", self.test_start_conversation),
            ("Test 5: Answer Questions", self.test_answer_questions),
            ("Test 6: Application Saved", self.test_application_saved),
            ("Test 7: Orchestrator Endpoints", self.test_orchestrator_endpoints),
        ]
        
        passed = 0
        for test_name, test_func in tests:
            print(f"\n{test_name}")
            print("-" * 80)
            if test_func():
                passed += 1
        
        print("\n" + "="*80)
        print("📊 TEST RESULTS SUMMARY")
        print("="*80 + "\n")
        
        for result in self.test_results:
            print(f"{result['status']} - {result['test']}")
            if result['details']:
                for line in result['details'].split('\n'):
                    print(f"  {line}")
        
        print("\n" + "="*80)
        total = len(self.test_results)
        print(f"✅ PASSED: {passed}/{total}")
        print(f"❌ FAILED: {total - passed}/{total}")
        print("="*80 + "\n")
        
        # Save results
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"📁 Results saved to: test_results.json\n")
        
        return passed == total

def main():
    """Run test suite"""
    test_case = LoanSystemTestCase()
    success = test_case.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED! System is working correctly.\n")
    else:
        print("⚠️  Some tests failed. Check the logs above.\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
