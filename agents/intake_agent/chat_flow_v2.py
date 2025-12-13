"""
Intake Agent - Strict Conversational Flow v2
Sequential question-answer flow with file uploads
"""

import re
from typing import Dict, Any, Optional, Tuple
from enum import Enum

class QuestionStage(Enum):
    """All stages in strict order"""
    LOAN_TYPE = "loan_type"
    FULL_NAME = "full_name"
    DATE_OF_BIRTH = "date_of_birth"
    PHONE = "phone"
    EMAIL = "email"
    PAN = "pan"
    EMPLOYMENT_TYPE = "employment_type"
    EMPLOYER_NAME = "employer_name"
    DESIGNATION = "designation"
    YEARS_AT_JOB = "years_at_job"
    MONTHLY_INCOME = "monthly_income"
    LOAN_AMOUNT = "loan_amount"
    TENURE_MONTHS = "tenure_months"
    KYC_FILE = "kyc_file"
    SELFIE_FILE = "selfie_file"
    PAYSLIP_FILE = "payslip_file"
    BANK_STATEMENT_FILE = "bank_statement_file"

class ConversationFlowV2:
    """Manages strict sequential conversation flow"""
    
    FLOW_SEQUENCE = [
        QuestionStage.LOAN_TYPE,
        QuestionStage.FULL_NAME,
        QuestionStage.DATE_OF_BIRTH,
        QuestionStage.PHONE,
        QuestionStage.EMAIL,
        QuestionStage.PAN,
        QuestionStage.EMPLOYMENT_TYPE,
        QuestionStage.EMPLOYER_NAME,
        QuestionStage.DESIGNATION,
        QuestionStage.YEARS_AT_JOB,
        QuestionStage.MONTHLY_INCOME,
        QuestionStage.LOAN_AMOUNT,
        QuestionStage.TENURE_MONTHS,
        QuestionStage.KYC_FILE,
        QuestionStage.SELFIE_FILE,
        QuestionStage.PAYSLIP_FILE,
        QuestionStage.BANK_STATEMENT_FILE,
    ]
    
    QUESTIONS = {
        QuestionStage.LOAN_TYPE: "What type of loan do you need? (personal/home/auto/education)",
        QuestionStage.FULL_NAME: "What is your full name?",
        QuestionStage.DATE_OF_BIRTH: "What is your date of birth? (YYYY-MM-DD)",
        QuestionStage.PHONE: "What is your phone number? (10 digits)",
        QuestionStage.EMAIL: "What is your email address?",
        QuestionStage.PAN: "What is your PAN? (Format: AAAAA9999A)",
        QuestionStage.EMPLOYMENT_TYPE: "What is your employment type? (salaried/self-employed/student)",
        QuestionStage.EMPLOYER_NAME: "What is your current employer name?",
        QuestionStage.DESIGNATION: "What is your job designation?",
        QuestionStage.YEARS_AT_JOB: "How many years have you been in this job?",
        QuestionStage.MONTHLY_INCOME: "What is your monthly income (₹)?",
        QuestionStage.LOAN_AMOUNT: "What loan amount do you need (₹)?",
        QuestionStage.TENURE_MONTHS: "What loan duration do you want (months)?",
        QuestionStage.KYC_FILE: "Please upload your KYC document (Aadhaar/PAN/Passport)",
        QuestionStage.SELFIE_FILE: "Please upload your selfie for face verification",
        QuestionStage.PAYSLIP_FILE: "Please upload your payslip (or type 'skip')",
        QuestionStage.BANK_STATEMENT_FILE: "Please upload your bank statement (or type 'skip')",
    }
    
    REQUIRED_FILES = {QuestionStage.KYC_FILE, QuestionStage.SELFIE_FILE}
    CONDITIONAL_FILES = {
        QuestionStage.PAYSLIP_FILE: lambda data: data.get("employment_type") == "salaried"
    }
    
    def __init__(self):
        pass
    
    def get_first_question(self) -> Tuple[QuestionStage, str]:
        """Get first question"""
        stage = self.FLOW_SEQUENCE[0]
        return stage, self.QUESTIONS[stage]
    
    def get_next_question(self, current_stage: QuestionStage, collected_data: Dict[str, Any]) -> Optional[Tuple[QuestionStage, str]]:
        """Get next question based on current stage and data"""
        
        current_index = self.FLOW_SEQUENCE.index(current_stage)
        
        for i in range(current_index + 1, len(self.FLOW_SEQUENCE)):
            next_stage = self.FLOW_SEQUENCE[i]
            
            # Skip conditional questions
            if next_stage == QuestionStage.EMPLOYER_NAME and collected_data.get("employment_type") != "salaried":
                continue
            if next_stage == QuestionStage.DESIGNATION and collected_data.get("employment_type") != "salaried":
                continue
            if next_stage == QuestionStage.YEARS_AT_JOB and collected_data.get("employment_type") != "salaried":
                continue
            
            # Skip payslip for non-salaried (they don't need it)
            if next_stage == QuestionStage.PAYSLIP_FILE and collected_data.get("employment_type") != "salaried":
                continue
            
            # For salaried employees: NEVER skip bank statement, always ask it after payslip
            # But DO skip payslip if not salaried
            
            return next_stage, self.QUESTIONS[next_stage]
        
        return None, None
    
    def validate_answer(self, stage: QuestionStage, answer: str) -> Tuple[bool, str]:
        """Validate answer for a stage. Returns (is_valid, value_or_error_msg)"""
        
        answer = answer.strip()
        
        if stage == QuestionStage.LOAN_TYPE:
            if answer.lower() in ["personal", "home", "auto", "education"]:
                return True, answer.lower()
            return False, "Invalid loan type. Please choose from: personal, home, auto, education"
        
        elif stage == QuestionStage.FULL_NAME:
            if len(answer) >= 2 and all(c.isalpha() or c.isspace() for c in answer):
                return True, answer
            return False, "Full name must be at least 2 characters and contain only letters"
        
        elif stage == QuestionStage.DATE_OF_BIRTH:
            if re.match(r"^\d{4}-\d{2}-\d{2}$", answer):
                return True, answer
            return False, "Invalid date format. Use YYYY-MM-DD (e.g., 1990-05-15)"
        
        elif stage == QuestionStage.PHONE:
            if re.match(r"^\d{10}$", answer):
                return True, answer
            return False, "Phone number must be 10 digits"
        
        elif stage == QuestionStage.EMAIL:
            if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", answer):
                return True, answer
            return False, "Invalid email format"
        
        elif stage == QuestionStage.PAN:
            if re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", answer.upper()):
                return True, answer.upper()
            return False, "Invalid PAN format. Must be like: AAAAA9999A"
        
        elif stage == QuestionStage.EMPLOYMENT_TYPE:
            if answer.lower() in ["salaried", "self-employed", "student"]:
                return True, answer.lower()
            return False, "Invalid employment type. Choose from: salaried, self-employed, student"
        
        elif stage == QuestionStage.EMPLOYER_NAME:
            if len(answer) >= 2:
                return True, answer
            return False, "Employer name must be at least 2 characters"
        
        elif stage == QuestionStage.DESIGNATION:
            if len(answer) >= 2:
                return True, answer
            return False, "Designation must be at least 2 characters"
        
        elif stage == QuestionStage.YEARS_AT_JOB:
            try:
                years = float(answer)
                if 0 <= years <= 70:
                    return True, years
                return False, "Years at job must be between 0 and 70"
            except:
                return False, "Please enter a valid number"
        
        elif stage == QuestionStage.MONTHLY_INCOME:
            try:
                income = float(answer)
                if income > 0:
                    return True, income
                return False, "Monthly income must be greater than 0"
            except:
                return False, "Please enter a valid number"
        
        elif stage == QuestionStage.LOAN_AMOUNT:
            try:
                amount = float(answer)
                if amount > 0:
                    return True, amount
                return False, "Loan amount must be greater than 0"
            except:
                return False, "Please enter a valid number"
        
        elif stage == QuestionStage.TENURE_MONTHS:
            try:
                months = int(answer)
                if 1 <= months <= 600:
                    return True, months
                return False, "Tenure must be between 1 and 600 months"
            except:
                return False, "Please enter a valid number"
        
        # File uploads
        elif stage in [QuestionStage.KYC_FILE, QuestionStage.SELFIE_FILE, QuestionStage.PAYSLIP_FILE, QuestionStage.BANK_STATEMENT_FILE]:
            answer_lower = answer.lower().strip()
            
            # Check for skip or optional responses
            if answer_lower in ["skip", "s", "no", "n", "-"]:
                # Check if file is required (considering conditionals)
                is_required = stage in self.REQUIRED_FILES
                if stage in self.CONDITIONAL_FILES:
                    is_required = self.CONDITIONAL_FILES[stage](self.collected_data)
                
                if is_required:
                    return False, f"{stage.value} is required. Please provide a file path or type 'skip'."
                return True, None
            
            # File path validation
            if answer.startswith("./") or answer.startswith("/"):
                return True, answer
            
            return False, "Please provide a valid file path (e.g., ./images/file.jpg) or type 'skip'"
        
        return True, answer
    
    def is_flow_complete(self, collected_data: Dict[str, Any]) -> bool:
        """Check if all required data collected"""
        
        required_fields = [
            "loan_type", "full_name", "date_of_birth", "phone", "email", "pan",
            "employment_type", "monthly_income", "loan_amount", "tenure_months",
            "kyc_file", "selfie_file"
        ]
        
        # Add conditional required fields
        if collected_data.get("employment_type") == "salaried":
            required_fields.extend(["employer_name", "designation", "years_at_job", "payslip_file"])
        
        for field in required_fields:
            if field not in collected_data or collected_data[field] is None:
                return False
        
        return True
    
    def validate_against_ocr(self, collected_data: Dict[str, Any], ocr_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate collected data against OCR-extracted document data
        
        Args:
            collected_data: Data collected from user (name, DOB, PAN)
            ocr_data: Data extracted from document via OCR
        
        Returns:
            (is_valid, message)
        """
        if not ocr_data:
            return True, "No OCR data to verify against"
        
        # Validate PAN number
        user_pan = collected_data.get("pan", "").upper().strip()
        ocr_pan = ocr_data.get("pan_number", "").upper().strip()
        
        if ocr_pan and user_pan != ocr_pan:
            return False, f"PAN mismatch: You entered {user_pan}, but document shows {ocr_pan}"
        
        # Validate name
        user_name = collected_data.get("full_name", "").upper().strip()
        ocr_name = ocr_data.get("name", "").upper().strip()
        
        if ocr_name:
            # Check if user name is contained in OCR name (allows partial matches)
            if user_name not in ocr_name and ocr_name not in user_name:
                # Try to match just first/last names
                user_parts = user_name.split()
                ocr_parts = ocr_name.split()
                
                # Check if any part matches
                has_match = any(part in ocr_parts for part in user_parts)
                if not has_match:
                    return False, f"Name mismatch: You entered '{user_name}', but document shows '{ocr_name}'"
        
        # Validate DOB
        user_dob = collected_data.get("date_of_birth", "").strip()
        ocr_dob = ocr_data.get("dob", "").strip()
        
        if ocr_dob:
            # Normalize DOB formats for comparison
            # Convert YYYY-MM-DD to DD/MM/YYYY if needed
            if "-" in user_dob and "/" not in user_dob:
                # YYYY-MM-DD format
                parts = user_dob.split("-")
                if len(parts) == 3:
                    user_dob_norm = f"{parts[2]}/{parts[1]}/{parts[0]}"
                else:
                    user_dob_norm = user_dob
            else:
                user_dob_norm = user_dob.replace("-", "/").replace(".", "/")
            
            ocr_dob_norm = ocr_dob.replace("-", "/").replace(".", "/")
            
            if user_dob_norm != ocr_dob_norm:
                return False, f"DOB mismatch: You entered {user_dob}, but document shows {ocr_dob}"
        
        return True, "All details verified against document"