# Intake / RAG Chat Agent

**LangChain-powered conversational agent for loan application intake with RAG capabilities.**

## 🎯 Purpose

The Intake Agent is the first touchpoint in the multi-agent loan origination pipeline. It handles:
- Natural language conversation with applicants
- RAG-based FAQ answering from knowledge base documents
- Intelligent slot-filling for loan application data
- Conversation memory using Redis
- Structured JSON output for orchestrator integration

## 🏗️ Architecture

```
User Input → FastAPI → LangChain Pipeline → RAG/Slots → Structured JSON
                            ↓
                       Redis Memory
                       FAISS Vector Store
```

## 🔧 Technology Stack

- **FastAPI**: High-performance async web framework
- **LangChain**: Orchestration, RAG, memory, prompt templates
- **Groq**: Ultra-fast LLM inference (Llama 3.1)
- **HuggingFace**: Free local embeddings
- **FAISS**: Vector similarity search for RAG
- **Redis**: Conversation memory and slot storage
- **Pydantic**: Strict schema validation

## 📦 Installation

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp ../.env.example .env
# Edit .env and add your GROQ_API_KEY
# Get free API key from: https://console.groq.com/

# Run Redis (using Docker)
docker run -d -p 6379:6379 redis:7-alpine

# Run the agent
python main.py
```

The service will start on `http://localhost:8001`

### Docker Deployment

```bash
# Build image
docker build -t intake-agent .

# Run container
docker run -d -p 8001:8001 \
  -e GROQ_API_KEY=your-key-here \
  -e REDIS_HOST=redis \
  -v ./data/docs:/app/data/docs \
  intake-agent
```

## 🚀 API Endpoints

### 1. Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "intake_agent",
  "version": "intake-v1",
  "timestamp": "2025-12-12T10:30:00.000Z"
}
```

### 2. Conversational RAG
```bash
POST /chat/converse
```

**Request:**
```json
{
  "application_id": "app-0001",
  "conversation_id": "conv-0001",
  "user_message": "What documents do I need for a loan?",
  "context": {}
}
```

**Response:**
```json
{
  "application_id": "app-0001",
  "conversation_id": "conv-0001",
  "slots": {
    "full_name": "John Doe",
    "email": "john@example.com"
  },
  "required_uploads": ["pan", "payslip"],
  "actions": [
    {
      "type": "upload_request",
      "doc_type": "pan",
      "message": "Please upload your PAN document"
    }
  ],
  "agent_version": "intake-v1",
  "ts": "2025-12-12T10:30:00.000Z",
  "assistant_reply": "You need PAN card, salary slips, and bank statements...",
  "rag_context": "Retrieved from knowledge base...",
  "next_prompt": "Could you provide your full name?"
}
```

### 3. Slot Update
```bash
POST /chat/slot
```

**Request:**
```json
{
  "application_id": "app-0001",
  "conversation_id": "conv-0001",
  "slot_name": "full_name",
  "slot_value": "John Doe"
}
```

### 4. Submit Application
```bash
POST /chat/submit
```

**Request:**
```json
{
  "application_id": "app-0001",
  "conversation_id": "conv-0001"
}
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-cov httpx

# Run tests
pytest test_intake_agent.py -v

# With coverage
pytest test_intake_agent.py --cov=. --cov-report=html
```

## 🛠️ LangChain Tool Integration

The agent can be wrapped as a LangChain Tool for orchestrator use:

```python
from langchain_tools import INTAKE_TOOLS
from langchain.agents import initialize_agent

# Create agent with intake tools
agent = initialize_agent(
    tools=INTAKE_TOOLS,
    llm=llm,
    agent="zero-shot-react-description"
)

# Use the tool
result = agent.run(
    "Start loan intake for application app-0001"
)
```

## 📁 Project Structure

```
intake_agent/
├── main.py                 # FastAPI application
├── schemas.py              # Pydantic models
├── langchain_pipeline.py   # LangChain RAG and slot-filling
├── langchain_tools.py      # Tool wrappers for orchestrator
├── requirements.txt        # Dependencies
├── Dockerfile              # Container image
├── test_intake_agent.py    # Unit tests
└── README.md               # This file
```

## 🔑 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------||
| `GROQ_API_KEY` | Groq API key (required) - Get from https://console.groq.com/ | - |
| `REDIS_HOST` | Redis hostname | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `DOCS_PATH` | Path to FAQ documents | `./data/docs` |

## 📚 Adding FAQ Documents

Place Markdown files in `./data/docs/`:

```markdown
# Loan FAQ

## What is the maximum loan amount?
Up to ₹10,00,000 based on your income profile.

## What documents are required?
- PAN card
- Salary slips (last 3 months)
- Bank statements (last 6 months)
```

The agent will automatically index these for RAG retrieval.

## 🔗 Integration with Orchestrator

The orchestrator can call this agent via:
1. **Direct HTTP calls** to the REST API
2. **LangChain Tools** using `langchain_tools.py`

Example orchestrator code:
```python
from agents.intake_agent.langchain_tools import intake_converse_tool

input_data = json.dumps({
    "application_id": "app-0001",
    "conversation_id": "conv-0001",
    "user_message": "I need a loan of ₹500000"
})

result = intake_converse_tool.run(input_data)
response = json.loads(result)
```

## 🐛 Troubleshooting

**Redis connection failed:**
- Ensure Redis is running: `docker ps | grep redis`
- Check connection: `redis-cli ping`

**RAG not working:**
- Verify documents exist in `./data/docs/`
- Check GROQ_API_KEY is valid (get from https://console.groq.com/)
- Review logs for embedding errors

**Slot extraction inaccurate:**
- Groq's Llama 3.1-70b is already excellent for extraction
- Add more examples to prompt template
- Adjust temperature in langchain_pipeline.py

## 📄 License

Part of the multi-agent loan origination system.

---

**Next Agent:** KYC/OCR Agent (port 8002)
