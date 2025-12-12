# Multi-Agent AI Loan Origination System

**LangChain-powered microservices architecture for intelligent loan processing**

## 🎯 System Overview

This repository contains **two microservices** in a multi-agent lending pipeline:

1. **Intake / RAG Chat Agent** (Port 8001) - Conversational loan application intake
2. **KYC / OCR Agent** (Port 8002) - Document verification and parsing

Both agents are built with **FastAPI**, powered by **LangChain**, and expose **LangChain Tool wrappers** for orchestrator integration.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                            │
│                  (LangChain Agents + Tools)                     │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
    ┌────────────────┐                  ┌────────────────┐
    │ Intake Agent   │                  │  KYC Agent     │
    │   Port 8001    │                  │   Port 8002    │
    │                │                  │                │
    │ • RAG Chat     │                  │ • OCR          │
    │ • Slot Fill    │────────────────▶ │ • Face Detect  │
    │ • Memory       │  Doc Upload      │ • Validation   │
    └────────┬───────┘                  └────────────────┘
             │
             ▼
        ┌─────────┐
        │  Redis  │
        │ Memory  │
        └─────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- OpenAI API Key
- Redis (for Intake Agent)

### 1. Clone and Setup

```bash
cd codered

# Create environment file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Run with Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f intake_agent
docker-compose logs -f kyc_agent
```

Services will be available at:
- Intake Agent: http://localhost:8001
- KYC Agent: http://localhost:8002
- Redis: localhost:6379

### 3. Run Locally (Development)

**Terminal 1 - Start Redis:**
```powershell
docker run -d -p 6379:6379 redis:7-alpine
```

**Terminal 2 - Intake Agent:**
```powershell
cd agents\intake_agent
pip install -r requirements.txt
python main.py
```

**Terminal 3 - KYC Agent:**
```powershell
cd agents\kyc_agent
pip install -r requirements.txt
python main.py
```

## 📋 Complete Workflow Example

### Step 1: Start Conversation
```bash
curl -X POST http://localhost:8001/chat/converse \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "app-0001",
    "conversation_id": "conv-0001",
    "user_message": "I want to apply for a personal loan of 5 lakhs"
  }'
```

**Response:**
```json
{
  "application_id": "app-0001",
  "slots": {
    "loan_amount": "500000"
  },
  "assistant_reply": "Great! I can help you with that. To proceed, I need some information...",
  "next_prompt": "Could you provide your full name?"
}
```

### Step 2: Fill Required Slots
```bash
curl -X POST http://localhost:8001/chat/slot \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "app-0001",
    "conversation_id": "conv-0001",
    "slot_name": "full_name",
    "slot_value": "John Doe"
  }'
```

### Step 3: Submit Application
```bash
curl -X POST http://localhost:8001/chat/submit \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "app-0001",
    "conversation_id": "conv-0001"
  }'
```

### Step 4: Upload and Parse Documents
```bash
# Parse PAN card
curl -X POST http://localhost:8002/kyc/parse \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "app-0001",
    "evidence_id": "ev-pan-001",
    "doc_type": "pan",
    "file_path": "./data/uploads/pan_card.jpg"
  }'
```

**Response:**
```json
{
  "application_id": "app-0001",
  "evidence_id": "ev-pan-001",
  "ocr": {
    "structured_fields": {
      "pan_number": "ABCDE1234F",
      "name": "JOHN DOE"
    }
  },
  "id_crop_evidence": {
    "face_detected": true,
    "crop_file_uri": "./data/crops/app-0001_ev-pan-001_face.jpg"
  },
  "overall_confidence": 0.90
}
```

## 🛠️ LangChain Orchestrator Integration

Create an orchestrator that uses both agents as LangChain Tools:

```python
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from agents.intake_agent.langchain_tools import INTAKE_TOOLS
from agents.kyc_agent.langchain_tools import KYC_TOOLS

# Combine all tools
all_tools = INTAKE_TOOLS + KYC_TOOLS

# Initialize orchestrator agent with Groq
llm = ChatGroq(temperature=0, model="llama-3.1-70b-versatile", groq_api_key="your-key")
orchestrator = initialize_agent(
    tools=all_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Execute loan workflow
result = orchestrator.run("""
Process a loan application:
1. Collect applicant information
2. Parse PAN card document
3. Verify extracted details
4. Proceed to next stage
""")
```

## 📁 Project Structure

```
codered/
├── agents/
│   ├── intake_agent/          # Conversational RAG agent
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── langchain_pipeline.py
│   │   ├── langchain_tools.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   ├── test_intake_agent.py
│   │   └── README.md
│   │
│   └── kyc_agent/             # OCR and face detection agent
│       ├── main.py
│       ├── schemas.py
│       ├── ocr_utils.py
│       ├── vision_utils.py
│       ├── file_utils.py
│       ├── langchain_tools.py
│       ├── requirements.txt
│       ├── Dockerfile
│       ├── test_kyc_agent.py
│       └── README.md
│
├── data/
│   ├── docs/                  # FAQ documents for RAG
│   ├── uploads/               # Uploaded documents
│   └── crops/                 # Face crops from IDs
│
├── docker-compose.yml
├── .env.example
└── README.md                  # This file
```

## 🧪 Testing

Run tests for both agents:

```bash
# Intake Agent tests
cd agents/intake_agent
pytest test_intake_agent.py -v --cov

# KYC Agent tests
cd agents/kyc_agent
pytest test_kyc_agent.py -v --cov
```

## 📊 API Documentation

Both agents provide auto-generated OpenAPI docs:

- Intake Agent: http://localhost:8001/docs
- KYC Agent: http://localhost:8002/docs

## 🔑 Configuration

### Environment Variables

```bash
# Groq API (PRIMARY - faster, free tier)
GROQ_API_KEY=gsk-...

# Redis (Intake Agent)
REDIS_HOST=localhost
REDIS_PORT=6379

# Paths
DOCS_PATH=./data/docs
UPLOAD_PATH=./data/uploads
CROPS_PATH=./data/crops

# Ports
INTAKE_AGENT_PORT=8001
KYC_AGENT_PORT=8002
```

## 🚦 Health Monitoring

```bash
# Check all services
curl http://localhost:8001/health
curl http://localhost:8002/health

# Expected response
{
  "status": "healthy",
  "service": "intake_agent",
  "version": "intake-v1",
  "timestamp": "2025-12-12T10:30:00.000Z"
}
```

## 📚 Key Features

### Intake Agent
✅ RAG from FAQ documents  
✅ Conversational slot-filling  
✅ Redis-backed memory  
✅ LangChain prompt templates  
✅ Structured JSON output  
✅ Action recommendations  
✅ **Groq-powered** (ultra-fast inference)  

### KYC Agent
✅ Multi-format OCR (Image + PDF)  
✅ PAN/Aadhaar parsing  
✅ MediaPipe face detection  
✅ Face crop extraction  
✅ SHA256 file validation  
✅ Confidence scoring  

## 🎓 Learning Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## 🐛 Troubleshooting

**Redis connection failed:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
redis-cli ping  # Should return PONG
```

**OpenAI API errors:**
- We use Groq, not OpenAI! Get free key: https://console.groq.com/
- Verify GROQ_API_KEY in `.env`
- Groq has generous free tier (no credit card needed)

**OCR not working:**
```bash
# Check Tesseract installation
tesseract --version
```

**Face detection issues:**
- Ensure image resolution > 300x300
- Check image format (jpg, png)
- Verify lighting quality

## 🔜 Next Steps

Your friend Medah can build:
- **Face Verification Agent** (Port 8003)
- **Income Verification Agent** (Port 8004)
- **Risk Assessment Agent** (Port 8005)
- **Fraud Detection Agent** (Port 8006)
- **Decision Engine** (Port 8007)
- **Disbursal Agent** (Port 8008)

All following the same architecture pattern with LangChain Tool wrappers.

## 📞 Support

For issues or questions about these agents, please refer to individual agent READMEs:
- [Intake Agent README](./agents/intake_agent/README.md)
- [KYC Agent README](./agents/kyc_agent/README.md)

---

**Built with ❤️ using LangChain, FastAPI, and Python**

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** December 12, 2025
