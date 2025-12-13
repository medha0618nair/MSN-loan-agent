"""
Strict Conversational Flow for Intake Agent
Defines the exact question sequence and validators
"""

import re
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

# Define the exact conversation flow
CONVERSATION_FLOW = [
    {
        "id": "loan_type",
        "question": "What type of loan would you like to apply for? (personal/home/auto/education)",
        "field_name": "loan_type",
        "required": True,
        "conditional": False,
        "validator": "validate_loan_type"
    },
    {
        "id": "full_name",
        "question": "Great — what is your full name?",
        "field_name": "full_name",
        "required": True,
        "conditional": False,
        "validator": "validate_full_name"
    },
    {
        "id": "date_of_birth",
        "question": "What is your date of birth? (YYYY-MM-DD)",
        "field_name": "date_of_birth",
        "required": True,
        "conditional": False,
        "validator": "validate_date_of_birth"
    },
    {
        "id": "phone",
        "question": "What is your phone number?",
        "field_name": "phone",
        "required": True,
        "conditional": False,
        "validator": "validate_phone"
    },
    {
        "id": "email",
        "question": "What is your email address?",
        "field_name": "email",
        "required": True,
        "conditional": False,
        "validator": "validate_email"
    },
    {
        "id": "pan",
        "question": "What is your PAN?",
        "field_name": "pan",
        "required": True,
        "conditional": False,
        "validator": "validate_pan"
    },
    {
        "id": "employment_type",
        "question": "What is your employment type? (salaried/self-employed/student)",
        "field_name": "employment_type",
        "required": True,
        "conditional": False,
        "validator": "validate_employment_type"
    },
    {
        "id": "employer_name",
        "question": "Who is your current employer?",
        "field_name": "employer_name",
        "required": True,
        "conditional": True,  # Only ask if employment_type == "salaried"
        "condition_field": "employment_type",
        "condition_value": "salaried",
        "validator": "validate_employer_name"
    },
    {
        "id": "designation",
        "question": "What is your job designation?",
        "field_name": "designation",
        "required": True,
        "conditional": True,  # Only ask if employment_type == "salaried"
        "condition_field": "employment_type",
        "condition_value": "salaried",
        "validator": "validate_designation"
    },
    {
        "id": "years_at_job",
        "question": "How many years have you been in your current job?",
        "field_name": "years_at_job",
        "required": True,
        "conditional": False,
        "validator": "validate_years_at_job"
    },
    {
        "id": "monthly_income",
        "question": "What is your monthly income?",
        "field_name": "monthly_income",
        "required": True,
        "conditional": False,
        "validator": "validate_monthly_income"
    },
    {
        "id": "loan_amount",
        "question": "What loan amount are you requesting?",
        "field_name": "loan_amount",
        "required": True,
        "conditional": False,
        "validator": "validate_loan_amount"
    },
    {
        "id": "tenure_months",
        "question": "For how many months do you want the loan?",
        "field_name": "tenure_months",
        "required": True,
        "conditional": False,
        "validator": "validate_tenure_months"
    },
    {
        "id": "kyc_document",
        "question": "Please upload your KYC document (Aadhaar/PAN). Type 'skip' to skip this step.",
        "field_name": "kyc_document",
        "required": False,
        "conditional": False,
        "validator": "validate_document_upload",
        "is_upload": True
    },
    {
        "id": "selfie",
        "question": "Please upload a selfie for face verification. Type 'skip' to skip this step.",
        "field_name": "selfie",
        "required": False,
        "conditional": False,
        "validator": "validate_document_upload",
        "is_upload": True
    },
    {
        "id": "payslip",
        "question": "Please upload your recent payslip. Type 'skip' to skip this step.",
        "field_name": "payslip",
        "required": False,
        "conditional": False,
        "validator": "validate_document_upload",
        "is_upload": True
    },
    {
        "id": "bank_statement",
        "question": "Please upload your bank statement (last 3 months). Type 'skip' to skip this step.",
        "field_name": "bank_statement",
        "required": False,
        "conditional": False,
        "validator": "validate_document_upload",
        "is_upload": True
    }
]


# Validators
def validate_loan_type(value: str) -> Tuple[bool, Optional[str]]:
    """Validate loan type"""
    valid_types = ["personal", "home", "auto", "education"]
    normalized = value.lower().strip()
    
    if normalized in valid_types:
        return True, normalized
    
    return False, f"Invalid loan type. Please choose from: {', '.join(valid_types)}"


def validate_full_name(value: str) -> Tuple[bool, Optional[str]]:
    """Validate full name"""
    name = value.strip()
    
    if len(name) < 2:
        return False, "Please provide a valid full name (at least 2 characters)"
    
    if not all(c.isalpha() or c.isspace() for c in name):
        return False, "Name should only contain letters and spaces"
    
    return True, name


def validate_date_of_birth(value: str) -> Tuple[bool, Optional[str]]:
    """Validate date of birth"""
    try:
        dob = datetime.strptime(value.strip(), "%Y-%m-%d")
        today = datetime.now()
        age = (today - dob).days // 365
        
        if age < 18:
            return False, "You must be at least 18 years old to apply for a loan"
        
        if age > 100:
            return False, "Please enter a valid date of birth"
        
        return True, value.strip()
    except ValueError:
        return False, "Invalid date format. Please use YYYY-MM-DD format"


def validate_phone(value: str) -> Tuple[bool, Optional[str]]:
    """Validate phone number"""
    phone = value.strip().replace(" ", "").replace("-", "")
    
    # Accept 10-digit numbers or numbers with country code
    if re.match(r"^\+?91?\d{10}$", phone):
        return True, phone
    
    return False, "Please enter a valid 10-digit phone number or with country code"


def validate_email(value: str) -> Tuple[bool, Optional[str]]:
    """Validate email address"""
    email = value.strip()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    if re.match(pattern, email):
        return True, email
    
    return False, "Please enter a valid email address"


def validate_pan(value: str) -> Tuple[bool, Optional[str]]:
    """Validate PAN format"""
    pan = value.strip().upper()
    # PAN format: AAAAA9999A
    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
    
    if re.match(pattern, pan):
        return True, pan
    
    return False, "Invalid PAN format. Expected format: AAAAA9999A (e.g., ABCDE1234F)"


def validate_employment_type(value: str) -> Tuple[bool, Optional[str]]:
    """Validate employment type"""
    valid_types = ["salaried", "self-employed", "student"]
    normalized = value.lower().strip()
    
    if normalized in valid_types:
        return True, normalized
    
    return False, f"Invalid employment type. Please choose from: {', '.join(valid_types)}"


def validate_employer_name(value: str) -> Tuple[bool, Optional[str]]:
    """Validate employer name"""
    employer = value.strip()
    
    if len(employer) < 2:
        return False, "Please provide a valid employer name"
    
    return True, employer


def validate_designation(value: str) -> Tuple[bool, Optional[str]]:
    """Validate job designation"""
    designation = value.strip()
    
    if len(designation) < 2:
        return False, "Please provide a valid job designation"
    
    return True, designation


def validate_years_at_job(value: str) -> Tuple[bool, Optional[str]]:
    """Validate years at current job"""
    try:
        years = float(value.strip())
        
        if years < 0:
            return False, "Years at job cannot be negative"
        
        if years > 70:
            return False, "Please enter a valid number of years"
        
        return True, years
    except ValueError:
        return False, "Please enter a valid number"


def validate_monthly_income(value: str) -> Tuple[bool, Optional[str]]:
    """Validate monthly income"""
    try:
        income = float(value.strip())
        
        if income < 0:
            return False, "Income cannot be negative"
        
        if income > 10000000:  # Reasonable upper limit
            return False, "Please enter a valid monthly income"
        
        return True, income
    except ValueError:
        return False, "Please enter a valid income amount"


def validate_loan_amount(value: str) -> Tuple[bool, Optional[str]]:
    """Validate loan amount"""
    try:
        amount = float(value.strip())
        
        if amount <= 0:
            return False, "Loan amount must be greater than 0"
        
        if amount > 50000000:  # Reasonable upper limit
            return False, "Please enter a valid loan amount"
        
        return True, amount
    except ValueError:
        return False, "Please enter a valid loan amount"


def validate_tenure_months(value: str) -> Tuple[bool, Optional[str]]:
    """Validate loan tenure"""
    try:
        months = int(value.strip())
        
        if months < 1:
            return False, "Tenure must be at least 1 month"
        
        if months > 600:  # Max 50 years
            return False, "Tenure cannot exceed 600 months"
        
        return True, months
    except ValueError:
        return False, "Please enter a valid number of months"


def validate_document_upload(value: str) -> Tuple[bool, Optional[str]]:
    """Validate document upload or skip"""
    normalized = value.strip().lower()
    
    if normalized == "skip":
        return True, "skip"
    
    # In real scenario, would validate file path/URL
    if len(normalized) > 0:
        return True, normalized
    
    return False, "Please provide a file path or type 'skip' to skip this document"


# Flow manager
class ConversationFlowManager:
    """Manages the conversation flow state and transitions"""
    
    def __init__(self):
        self.flow = CONVERSATION_FLOW
        self.validators = {
            "validate_loan_type": validate_loan_type,
            "validate_full_name": validate_full_name,
            "validate_date_of_birth": validate_date_of_birth,
            "validate_phone": validate_phone,
            "validate_email": validate_email,
            "validate_pan": validate_pan,
            "validate_employment_type": validate_employment_type,
            "validate_employer_name": validate_employer_name,
            "validate_designation": validate_designation,
            "validate_years_at_job": validate_years_at_job,
            "validate_monthly_income": validate_monthly_income,
            "validate_loan_amount": validate_loan_amount,
            "validate_tenure_months": validate_tenure_months,
            "validate_document_upload": validate_document_upload,
        }
    
    def get_first_question(self) -> Dict[str, Any]:
        """Get the first question (always loan_type)"""
        return self.flow[0]
    
    def get_question_by_id(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Get a question by its ID"""
        for q in self.flow:
            if q["id"] == question_id:
                return q
        return None
    
    def get_next_question(self, current_question_id: str, collected_slots: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get the next question in the flow based on current position and collected data"""
        current_index = None
        
        # Find current question index
        for i, q in enumerate(self.flow):
            if q["id"] == current_question_id:
                current_index = i
                break
        
        if current_index is None:
            return None
        
        # Look for next non-conditional question or check conditions
        for i in range(current_index + 1, len(self.flow)):
            next_q = self.flow[i]
            
            # Check if question is conditional
            if next_q.get("conditional", False):
                condition_field = next_q.get("condition_field")
                condition_value = next_q.get("condition_value")
                
                # Only ask if condition is met
                if collected_slots.get(condition_field) == condition_value:
                    return next_q
            else:
                # Non-conditional question, ask it
                return next_q
        
        # All questions answered
        return None
    
    def validate_answer(self, question_id: str, answer: str) -> Tuple[bool, Optional[str]]:
        """Validate an answer for a given question"""
        question = self.get_question_by_id(question_id)
        
        if not question:
            return False, "Question not found"
        
        validator_name = question.get("validator")
        validator_func = self.validators.get(validator_name)
        
        if not validator_func:
            return False, "No validator found"
        
        return validator_func(answer)
    
    def is_flow_complete(self, collected_slots: Dict[str, Any]) -> bool:
        """Check if all required questions have been answered"""
        for q in self.flow:
            # Skip conditional questions that don't apply
            if q.get("conditional", False):
                condition_field = q.get("condition_field")
                condition_value = q.get("condition_value")
                
                if collected_slots.get(condition_field) != condition_value:
                    continue  # This question doesn't apply
            
            # Check if required field is present
            if q.get("required", False):
                if q["field_name"] not in collected_slots:
                    return False
        
        return True
    
    def get_all_questions_answered(self, collected_slots: Dict[str, Any]) -> list[str]:
        """Get list of all questions that have been answered"""
        answered = []
        for q in self.flow:
            if q["field_name"] in collected_slots:
                answered.append(q["id"])
        return answered
