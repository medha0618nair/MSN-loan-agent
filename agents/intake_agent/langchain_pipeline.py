"""
LangChain pipeline for Intake Agent.
Handles RAG, conversation memory, slot-filling, and structured output parsing.
"""
import os
import json
import re
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from pydantic import BaseModel, Field
import redis

logger = logging.getLogger(__name__)


class SlotExtractionOutput(BaseModel):
    """Structured output for slot extraction."""
    extracted_slots: Dict[str, Any] = Field(default_factory=dict)
    missing_slots: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    next_question: Optional[str] = None


class IntakePipeline:
    """LangChain-powered Intake Agent pipeline."""
    
    def __init__(
        self,
        groq_api_key: str,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        docs_path: str = "./data/docs",
        model_name: str = "llama-3.3-70b-versatile"
    ):
        self.groq_api_key = groq_api_key
        self.model_name = model_name
        self.docs_path = Path(docs_path)
        # In-memory fallbacks when Redis is not available
        self._slots_mem: Dict[str, Dict[str, Any]] = {}
        self._conv_mem: Dict[str, List[str]] = {}
        self._uploads_mem: Dict[str, set[str]] = {}
        
        # Initialize Redis for memory
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True,
                socket_connect_timeout=2
            )
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory fallback.")
            self.redis_client = None
        
        # Initialize LLM with Groq (faster inference)
        # In langchain 0.2.x, ChatGroq expects `model` param
        self.llm = ChatGroq(
            temperature=0.7,
            model=model_name,
            api_key=groq_api_key
        )
        logger.info(f"ChatGroq initialized with model '{model_name}' (API key set: {bool(groq_api_key)})")
        
        # Initialize RAG components
        self.vector_store = None
        self.qa_chain = None
        self._initialize_rag()
        
        # Slot-filling prompt template
        self.slot_prompt = PromptTemplate(
            input_variables=["user_message", "current_slots", "conversation_history"],
            template="""You are a loan application intake assistant. Your ONLY job is to extract structured data from user messages.

CRITICAL: You MUST respond ONLY with valid JSON. No other text.

Current collected slots: {current_slots}
Conversation history: {conversation_history}
User message: {user_message}

Extract ALL information from the user message that matches these slots:
- full_name: Full legal name (e.g., "John Doe")
- email: Email address (e.g., "john@example.com")
- phone: Phone number (e.g., "+91-9876543210")
- loan_amount: Requested loan amount in rupees (numeric only, e.g., "300000")
- loan_purpose: Purpose of loan (e.g., "home renovation", "education")
- employment_status: Employment type (e.g., "salaried", "self-employed", "business")
- monthly_income: Monthly income in rupees (numeric only, e.g., "75000")
- pan_number: PAN card number (e.g., "ABCDE1234F")

REQUIRED slots that must be present to proceed: full_name, email, phone, loan_amount, loan_purpose

Return ONLY this JSON (no markdown, no extra text):
{{
  "extracted_slots": {{"slot_name": "value", ...}},
  "missing_slots": ["slot_name", ...],
  "confidence": 0.85,
  "next_question": "What is your monthly income?"
}}

Rules:
1. Extract ONLY what the user explicitly provided
2. Do NOT assume or infer values
3. Keep values clean (no extra spaces, no currency symbols)
4. If a value is partially mentioned, include it
5. List ALL missing required slots
6. Suggest ONE next question based on most critical missing slot
"""
        )
        
        # Conversational prompt
        self.converse_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a friendly loan application assistant powered by RAG.
            Use the provided context to answer questions accurately.
            If you don't know something, say so and offer to connect with a human agent.
            Always be helpful and guide users through the application process."""),
            ("human", "{user_message}"),
            ("ai", "Context from knowledge base:\n{rag_context}")
        ])
    
    def _initialize_rag(self):
        """Initialize RAG with FAISS vector store."""
        try:
            if not self.docs_path.exists():
                logger.warning(f"Docs path {self.docs_path} does not exist. Creating it.")
                self.docs_path.mkdir(parents=True, exist_ok=True)
                # Create sample FAQ
                sample_faq = self.docs_path / "sample_faq.md"
                sample_faq.write_text("""# Loan Application FAQ

## What documents do I need?
You need PAN card, Aadhaar card, salary slips (last 3 months), and bank statements.

## What is the maximum loan amount?
The maximum loan amount is ₹10,00,000 depending on your income and credit profile.

## How long does approval take?
Typical approval takes 24-48 hours after document verification.

## What is the interest rate?
Interest rates start from 10.5% per annum based on your profile.

## Can I prepay my loan?
Yes, prepayment is allowed after 6 months with no penalty.
""", encoding="utf-8")
                logger.info("Created sample FAQ document")
            
            # Load documents (manual to avoid loader edge cases)
            documents: List[Document] = []
            for path in self.docs_path.rglob("*.md"):
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    if text and text.strip():
                        documents.append(Document(page_content=text, metadata={"source": str(path)}))
                except Exception as read_err:
                    logger.warning(f"Failed to read {path}: {read_err}")
            
            if not documents:
                logger.warning("No documents found for RAG. Using empty vector store.")
                return
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            # Create embeddings and vector store (using HuggingFace - CPU)
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            if not splits:
                logger.warning("No text splits produced from documents; skipping RAG init.")
                self.vector_store = None
                self.qa_chain = None
                return
            self.vector_store = FAISS.from_documents(splits, embeddings)
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            
            logger.info(f"RAG initialized with {len(splits)} document chunks")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG: {e}")
            self.vector_store = None
            self.qa_chain = None
    
    
    def _get_conversation_memory(self, conversation_id: str) -> List[str]:
        """Retrieve conversation history from Redis."""
        if not self.redis_client:
            return self._conv_mem.get(conversation_id, [])
        
        try:
            key = f"conv:{conversation_id}"
            history = self.redis_client.lrange(key, 0, -1)
            return history
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            return []
    
    def _save_conversation_turn(self, conversation_id: str, user_msg: str, assistant_msg: str):
        """Save conversation turn to Redis."""
        if not self.redis_client:
            self._conv_mem.setdefault(conversation_id, [])
            self._conv_mem[conversation_id].append(f"User: {user_msg}")
            self._conv_mem[conversation_id].append(f"Assistant: {assistant_msg}")
            return
        
        try:
            key = f"conv:{conversation_id}"
            self.redis_client.rpush(key, f"User: {user_msg}")
            self.redis_client.rpush(key, f"Assistant: {assistant_msg}")
            self.redis_client.expire(key, 86400)  # 24 hour TTL
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
    
    def _get_slots(self, application_id: str) -> Dict[str, Any]:
        """Retrieve current slots from Redis."""
        if not self.redis_client:
            return self._slots_mem.get(application_id, {})
        
        try:
            key = f"slots:{application_id}"
            slots = self.redis_client.hgetall(key)
            return slots
        except Exception as e:
            logger.error(f"Failed to retrieve slots: {e}")
            return {}
    
    def _save_slot(self, application_id: str, slot_name: str, slot_value: Any):
        """Save slot to Redis."""
        if not self.redis_client:
            self._slots_mem.setdefault(application_id, {})
            self._slots_mem[application_id][slot_name] = slot_value
            return
        
        try:
            key = f"slots:{application_id}"
            self.redis_client.hset(key, slot_name, str(slot_value))
            self.redis_client.expire(key, 86400)  # 24 hour TTL
        except Exception as e:
            logger.error(f"Failed to save slot: {e}")

    def mark_upload(self, application_id: str, doc_type: str):
        """Mark a document upload as received (in-memory fallback)."""
        if not self.redis_client:
            self._uploads_mem.setdefault(application_id, set())
            self._uploads_mem[application_id].add(doc_type)
            return
        try:
            key = f"upload:{application_id}:{doc_type}"
            self.redis_client.set(key, "1", ex=86400)
        except Exception as e:
            logger.error(f"Failed to mark upload: {e}")

    def has_upload(self, application_id: str, doc_type: str) -> bool:
        """Check if an upload is already recorded."""
        if not self.redis_client:
            return doc_type in self._uploads_mem.get(application_id, set())
        try:
            key = f"upload:{application_id}:{doc_type}"
            return bool(self.redis_client.get(key))
        except Exception as e:
            logger.error(f"Failed to read upload marker: {e}")
            return False
    
    def rag_query(self, query: str) -> Dict[str, Any]:
        """Execute RAG query."""
        if not self.qa_chain:
            return {
                "answer": "Knowledge base is not initialized.",
                "source_documents": []
            }
        try:
            logger.info("Calling Groq QA chain for RAG query via ChatCompletions API")
            result = self.qa_chain({"query": query})
            return {
                "answer": result.get("result", ""),
                "source_documents": [doc.page_content for doc in result.get("source_documents", [])]
            }
        except Exception as e:
            logger.error(f"RAG query failed using Groq API: {e}")
            return {
                "answer": "I encountered an error processing your question with the LLM. Please try again.",
                "source_documents": []
            }
    
    def extract_slots(
        self,
        user_message: str,
        application_id: str,
        conversation_id: str
    ) -> SlotExtractionOutput:
        """Extract slots from user message using LLM with strict JSON output."""
        current_slots = self._get_slots(application_id)
        history = self._get_conversation_memory(conversation_id)
        
        # Create chain for slot extraction
        chain = LLMChain(llm=self.llm, prompt=self.slot_prompt)
        
        try:
            logger.info(f"Extracting slots from message: {user_message[:50]}...")
            result = chain.run(
                user_message=user_message,
                current_slots=str(current_slots),
                conversation_history="\n".join(history[-6:])  # Last 3 turns
            )
            
            # Parse result - strict JSON extraction
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                output = SlotExtractionOutput(**parsed)
                logger.info(f"Extracted slots: {list(output.extracted_slots.keys())}")
            else:
                logger.warning(f"No JSON found in response: {result[:100]}")
                # Fallback
                output = SlotExtractionOutput(
                    extracted_slots={},
                    missing_slots=["full_name", "email", "phone", "loan_amount", "loan_purpose"],
                    confidence=0.3,
                    next_question="Could you please start by providing your full legal name?"
                )
            
            # Save extracted slots immediately
            for slot_name, slot_value in output.extracted_slots.items():
                self._save_slot(application_id, slot_name, slot_value)
                logger.info(f"Saved slot: {slot_name}={slot_value}")
            
            return output
            
        except json.JSONDecodeError as je:
            logger.error(f"JSON parse error during slot extraction: {je}")
            return SlotExtractionOutput(
                extracted_slots={},
                missing_slots=["full_name", "email", "phone", "loan_amount"],
                confidence=0.0,
                next_question="Let me start over. What is your full legal name?"
            )
        except Exception as e:
            logger.error(f"Slot extraction failed: {e}")
            return SlotExtractionOutput(
                extracted_slots={},
                missing_slots=["full_name", "email", "phone", "loan_amount"],
                confidence=0.0,
                next_question="Could you provide your basic information to proceed?"
            )

    def _fallback_extract(self, user_message: str) -> Dict[str, Any]:
        """Lightweight regex-based extraction to avoid empty turns when LLM fails."""
        slots: Dict[str, Any] = {}
        # Name
        m = re.search(r"\b(?:i am|i'm|i’m)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)", user_message, re.IGNORECASE)
        if m:
            slots["full_name"] = m.group(1).strip()
        # Email
        m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", user_message)
        if m:
            slots["email"] = m.group(0)
        # Phone (10+ digits)
        m = re.search(r"\+?\d[\d\s\-()]{8,}\d", user_message)
        if m:
            digits = re.sub(r"\D", "", m.group(0))
            if len(digits) >= 10:
                slots["phone"] = "+" + digits if not digits.startswith("+") else digits
        # Loan amount
        m = re.search(r"\b(\d{4,9})\b", user_message.replace(",", ""))
        if m:
            slots["loan_amount"] = m.group(1)
        # Purpose
        m = re.search(r"for\s+([A-Za-z ]{3,50})", user_message, re.IGNORECASE)
        if m:
            slots["loan_purpose"] = m.group(1).strip()
        return slots
    
    def conversational_reply(
        self,
        user_message: str,
        conversation_id: str,
        application_id: str
    ) -> Dict[str, str]:
        """Generate conversational reply with RAG context and slot extraction."""
        # Get RAG context
        rag_result = self.rag_query(user_message)
        rag_context = rag_result["answer"]
        
        # Extract slots from this message
        slot_data = self.extract_slots(user_message, application_id, conversation_id)

        # If LLM returned nothing, try regex fallback to keep flow moving
        if not slot_data.extracted_slots:
            fallback = self._fallback_extract(user_message)
            if fallback:
                for k, v in fallback.items():
                    self._save_slot(application_id, k, v)
                slot_data.extracted_slots = fallback
        
        # Get current slots after extraction
        current_slots = self._get_slots(application_id)
        
        # Define required slots for Stage 1 (Data Input)
        required_slots = ["full_name", "email", "phone", "loan_amount", "loan_purpose"]
        collected_required = [s for s in required_slots if s in current_slots]
        all_required_collected = len(collected_required) == len(required_slots)
        
        # Generate reply
        try:
            # Build reply incorporating RAG answer + slot collection status
            reply_lines = []
            
            # Check if all required slots are now collected
            if all_required_collected and user_message.lower().strip() in [
                "i have provided all my information. can you confirm everything is correct?",
                "i have provided all my information. can you confirm everything is correct",
                "confirm",
                "yes",
            ]:
                # Stage 1 complete message
                reply_lines.append("✓ Stage 1 Complete: Loan Application Data\n")
                reply_lines.append("Your basic information has been recorded:")
                for slot in required_slots:
                    if slot in current_slots:
                        reply_lines.append(f"  • {slot.replace('_', ' ').title()}: {current_slots[slot]}")
                
                reply_lines.append("\nStage 2: Document Verification\n")
                reply_lines.append("To process your loan application, we need the following documents:")
                reply_lines.append("  • Government-issued ID (Aadhaar/Passport/Driving License)")
                reply_lines.append("  • Proof of Address (utility bill or bank statement, not older than 90 days)")
                reply_lines.append("  • Proof of Income (last 3 salary slips or latest bank statements)")
                reply_lines.append("  • PAN Card")
                reply_lines.append("\nPlease upload the documents to continue with your loan application.")
            else:
                # Normal conversational flow with data collection
                # Only surface RAG context when user asks a question and when it is not an error message
                if "?" in user_message and rag_context and not rag_context.startswith("I encountered an error processing your question"):
                    reply_lines.append(rag_context)
                
                # Add extraction summary if slots were found
                if slot_data.extracted_slots:
                    extracted_str = ", ".join([f"{k}='{v}'" for k, v in slot_data.extracted_slots.items()])
                    reply_lines.append(f"\n✓ Recorded: {extracted_str}")
                else:
                    # Friendly greeting-style prompt when we have nothing yet
                    missing = [s for s in required_slots if s not in current_slots]
                    if len(collected_required) == 0:
                        reply_lines.append("\nHi! I can help with your loan application. Can you share your full name and email to get started?")
                    elif missing:
                        need_str = ", ".join([s.replace('_', ' ') for s in missing[:2]])
                        reply_lines.append(f"\nI’m capturing your details. I still need: {need_str}.")
                    else:
                        reply_lines.append("\nI’ve logged that. Let’s continue.")
                
                # Add progress summary with what we have
                progress = f"{len(collected_required)}/{len(required_slots)}"
                have = ", ".join([k.replace('_', ' ') for k in collected_required]) if collected_required else "none yet"
                reply_lines.append(f"\nProgress: {progress} required fields collected (have: {have})")
                
                # Add next prompt for missing data
                if not all_required_collected:
                    missing = [s for s in required_slots if s not in current_slots]
                    reply_lines.append(f"\nStill needed: {', '.join([s.replace('_', ' ').title() for s in missing])}")
                    next_q = slot_data.next_question or "Could you share the remaining details?"
                    reply_lines.append(f"\n{next_q}")
                else:
                    reply_lines.append("\n✓ All required information collected! Type 'confirm' when ready to proceed to document verification.")
            
            reply = "\n".join(reply_lines)
            
            # Save conversation
            self._save_conversation_turn(conversation_id, user_message, reply)
            
            return {
                "assistant_reply": reply,
                "rag_context": "\n".join(rag_result["source_documents"][:2])
            }
        except Exception as e:
            logger.error(f"Conversational reply failed: {e}")
            return {
                "assistant_reply": "I'm here to help with your loan application. Please share your details or ask a question.",
                "rag_context": ""
            }
