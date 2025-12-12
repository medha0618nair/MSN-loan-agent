# KYC / OCR Agent

**Document parsing and verification agent with OCR and face detection capabilities.**

## 🎯 Purpose

The KYC Agent handles document verification in the loan origination pipeline. It performs:
- OCR text extraction from images and PDFs
- PAN card parsing with regex validation
- Face detection and cropping from ID documents
- Payslip and bank statement parsing
- File integrity validation (SHA256)

## 🏗️ Architecture

```
Document Upload → FastAPI → OCR → Structured Fields
                            ↓
                       Face Detection
                       Field Extraction
                       Validation
                            ↓
                       JSON Response
```

## 🔧 Technology Stack

- **FastAPI**: High-performance async web framework
- **Tesseract OCR**: Text extraction from images
- **pdfplumber**: PDF text extraction
- **OpenCV**: Image processing
- **MediaPipe**: Advanced face detection
- **LangChain**: Tool wrapper for orchestrator

## 📦 Installation

### System Requirements

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp ../.env.example .env

# Run the agent
python main.py
```

The service will start on `http://localhost:8002`

### Docker Deployment

```bash
# Build image
docker build -t kyc-agent .

# Run container
docker run -d -p 8002:8002 \
  -v ./data/uploads:/app/data/uploads \
  -v ./data/crops:/app/data/crops \
  kyc-agent
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
  "service": "kyc_agent",
  "version": "kyc-v1",
  "timestamp": "2025-12-12T10:30:00.000Z"
}
```

### 2. Parse Document
```bash
POST /kyc/parse
```

**Request:**
```json
{
  "application_id": "app-0001",
  "evidence_id": "ev-pan-001",
  "doc_type": "pan",
  "file_path": "./data/uploads/pan_card.jpg"
}
```

**Response:**
```json
{
  "application_id": "app-0001",
  "evidence_id": "ev-pan-001",
  "doc_type": "pan",
  "file_uri": "./data/uploads/pan_card.jpg",
  "file_sha256": "a1b2c3d4...",
  "ocr": {
    "raw_text": "INCOME TAX DEPARTMENT\nPAN: ABCDE1234F\nName: JOHN DOE",
    "structured_fields": {
      "pan_number": "ABCDE1234F",
      "name": "JOHN DOE",
      "confidence": 0.9
    },
    "confidence_scores": {
      "overall": 0.85
    }
  },
  "id_crop_evidence": {
    "crop_file_uri": "./data/crops/app-0001_ev-pan-001_face.jpg",
    "face_detected": true,
    "face_confidence": 0.92,
    "face_bbox": [120, 80, 150, 180]
  },
  "overall_confidence": 0.90,
  "agent_version": "kyc-v1",
  "ts": "2025-12-12T10:30:00.000Z",
  "validation_errors": []
}
```

## 📄 Supported Document Types

### 1. PAN Card (`doc_type: "pan"`)
- Extracts PAN number (regex: `[A-Z]{5}[0-9]{4}[A-Z]{1}`)
- Detects and crops face photo
- Validates PAN format

### 2. Payslip (`doc_type: "payslip"`)
- Extracts salary amounts
- Identifies gross salary
- Extracts contact information

### 3. Bank Statement (`doc_type: "bank_statement"`)
- Extracts account numbers
- Parses transaction data
- Identifies email/phone

### 4. Aadhaar (`doc_type: "aadhaar"`)
- Extracts Aadhaar number
- Detects and crops face photo
- Extracts address details

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest test_kyc_agent.py -v

# Test with sample document
curl -X POST http://localhost:8002/kyc/parse \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "test-001",
    "evidence_id": "ev-001",
    "doc_type": "pan",
    "file_path": "./test_pan.jpg"
  }'
```

## 🛠️ LangChain Tool Integration

```python
from langchain_tools import kyc_parse_tool
import json

# Use as LangChain tool
input_data = json.dumps({
    "application_id": "app-0001",
    "evidence_id": "ev-pan-001",
    "doc_type": "pan",
    "file_path": "./data/uploads/pan.jpg"
})

result = kyc_parse_tool.run(input_data)
parsed = json.loads(result)

print(f"PAN: {parsed['ocr']['structured_fields']['pan_number']}")
print(f"Confidence: {parsed['overall_confidence']}")
```

## 📁 Project Structure

```
kyc_agent/
├── main.py                 # FastAPI application
├── schemas.py              # Pydantic models
├── ocr_utils.py           # OCR processing
├── vision_utils.py        # Face detection
├── file_utils.py          # File handling
├── langchain_tools.py     # Tool wrappers
├── requirements.txt       # Dependencies
├── Dockerfile             # Container image
├── test_kyc_agent.py      # Unit tests
└── README.md              # This file
```

## 🔑 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `UPLOAD_PATH` | Path for uploaded documents | `./data/uploads` |
| `CROPS_PATH` | Path for face crops | `./data/crops` |

## 🎨 Face Detection

The agent uses a two-tier approach:

1. **MediaPipe** (Primary): State-of-the-art ML-based detection
2. **OpenCV Haar Cascade** (Fallback): Classical computer vision

Face crops are saved with naming pattern: `{application_id}_{evidence_id}_face.jpg`

## 📊 OCR Confidence Scoring

Confidence calculation:
- **Image OCR**: Average of Tesseract per-word confidence
- **PDF text**: Fixed 0.95 (native text extraction)
- **Overall**: Weighted average of OCR + face detection confidence

## 🔐 Security Features

- SHA256 file integrity validation
- File type validation (jpg, png, pdf only)
- Size limits (configurable)
- Path traversal protection

## 🐛 Troubleshooting

**Tesseract not found:**
```bash
# Check installation
tesseract --version

# Ubuntu: Install
sudo apt-get install tesseract-ocr

# Set path (if needed)
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/
```

**Face detection not working:**
- Ensure image has sufficient resolution (min 300x300)
- Check image is not rotated or skewed
- Verify lighting conditions are adequate

**Low OCR accuracy:**
- Increase image resolution
- Ensure good scan quality
- Use native PDF text when possible
- Try image preprocessing (contrast, denoise)

## 📈 Performance

- **OCR**: ~2-5 seconds per page
- **Face detection**: ~1-2 seconds
- **PDF processing**: ~1 second per page
- **Throughput**: ~20-30 documents/minute

## 📄 Example cURL Commands

```bash
# Parse PAN card
curl -X POST http://localhost:8002/kyc/parse \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "app-0001",
    "evidence_id": "ev-pan-001",
    "doc_type": "pan",
    "file_path": "./data/uploads/pan.jpg"
  }'

# Health check
curl http://localhost:8002/health
```

## 🔗 Integration Points

**Upstream:** Intake Agent (receives document upload notifications)  
**Downstream:** Face Verification Agent (uses face crops)  
**Orchestrator:** Called via LangChain Tool wrapper

## 📄 License

Part of the multi-agent loan origination system.

---

**Previous Agent:** Intake Agent (port 8001)  
**Next Agent:** Face Verification Agent (port 8003)
