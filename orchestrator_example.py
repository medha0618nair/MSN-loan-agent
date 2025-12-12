"""
Example Orchestrator using LangChain to coordinate Intake and KYC agents.
This demonstrates how to use both agents as LangChain Tools.
"""
import os
import json
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_message_histories import ChatMessageHistory

# Import agent tools
import sys
sys.path.append('./agents/intake_agent')
sys.path.append('./agents/kyc_agent')

from agents.intake_agent.langchain_tools import INTAKE_TOOLS
from agents.kyc_agent.langchain_tools import KYC_TOOLS


class LoanOrchestrator:
    """
    Orchestrator that coordinates multiple agents using LangChain.
    """
    
    def __init__(self, groq_api_key: str):
        self.llm = ChatGroq(
            temperature=0,
            model="llama-3.1-70b-versatile",
            groq_api_key=groq_api_key
        )
        
        # Combine all agent tools
        self.tools = INTAKE_TOOLS + KYC_TOOLS
        
        # Initialize memory
        self.memory = ChatMessageHistory()
        
        # Initialize agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def process_loan_application(self, application_id: str):
        """
        End-to-end loan application processing.
        """
        print(f"🚀 Starting loan application processing for {application_id}")
        
        # Step 1: Intake
        print("\n📝 Step 1: Collecting applicant information...")
        intake_result = self.agent.run(f"""
        Start a loan intake conversation for application {application_id}.
        Conversation ID: conv-{application_id}.
        Ask the user what they need help with.
        """)
        print(f"Intake Result: {intake_result}")
        
        return intake_result
    
    def collect_information(self, application_id: str, user_input: str):
        """
        Process user input and collect information.
        """
        print(f"\n💬 Processing user input: {user_input}")
        
        result = self.agent.run(f"""
        For application {application_id}, conversation conv-{application_id}:
        Process this user message: "{user_input}"
        
        Extract any information and update slots accordingly.
        If documents are mentioned, prepare for KYC processing.
        """)
        
        return result
    
    def process_document(self, application_id: str, doc_type: str, file_path: str):
        """
        Process uploaded document through KYC agent.
        """
        print(f"\n📄 Step 2: Processing {doc_type} document...")
        
        evidence_id = f"ev-{doc_type}-001"
        
        kyc_result = self.agent.run(f"""
        Parse the {doc_type} document for application {application_id}.
        Evidence ID: {evidence_id}
        File path: {file_path}
        
        Extract all relevant information and validate the document.
        """)
        
        return kyc_result
    
    def submit_application(self, application_id: str):
        """
        Submit the completed application.
        """
        print(f"\n✅ Step 3: Submitting application...")
        
        submit_result = self.agent.run(f"""
        Submit the completed application {application_id} with conversation conv-{application_id}.
        Verify all required information is collected.
        """)
        
        return submit_result


def main():
    """
    Demo orchestrator workflow.
    """
    print("=" * 80)
    print("🏦 LOAN ORIGINATION ORCHESTRATOR - DEMO")
    print("=" * 80)
    
    # Initialize orchestrator
    api_key = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
    orchestrator = LoanOrchestrator(groq_api_key=api_key)
    
    # Simulate workflow
    app_id = "app-demo-001"
    
    try:
        # Step 1: Start intake
        orchestrator.process_loan_application(app_id)
        
        # Step 2: Simulate user providing information
        user_messages = [
            "My name is John Doe and I need a loan of 500000 rupees",
            "My email is john.doe@example.com and phone is 9876543210",
            "I work as a software engineer and my monthly income is 75000"
        ]
        
        for msg in user_messages:
            orchestrator.collect_information(app_id, msg)
        
        # Step 3: Process documents (mock)
        print("\n" + "=" * 80)
        print("📤 User would now upload documents...")
        print("For demo purposes, skipping actual document processing")
        print("In production, call: orchestrator.process_document(app_id, 'pan', file_path)")
        
        # Step 4: Submit
        orchestrator.submit_application(app_id)
        
        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
