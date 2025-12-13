# Face & Liveness Verification Agent

A FastAPI microservice for facial identity verification and liveness detection in a multi-agent loan-origination system. Wrapped as a LangChain Tool for orchestrator integration.

## Overview

This agent verifies:
1. **Face Similarity** - Compares ID document face crop with user selfie using FaceNet embeddings
2. **Liveness Detection** - Validates selfie authenticity using facial landmarks and motion analysis
3. **Match Confidence** - Weighted score combining similarity and liveness (70% similarity + 30% liveness)

**System Position:**
```
User → Intake → KYC → [FACE VERIFICATION] → Income → Risk → Fraud → Decision → Disbursal
```

## Architecture

```
FastAPI Endpoint (/face/verify)
    ↓
Face Detection (MediaPipe)
    ↓
Embedding Generation (FaceNet)
    ↓
Liveness Analysis (MediaPipe Face Mesh)
    ↓
Similarity Computation (Cosine Distance)
    ↓
Database Storage (SQLite)
    ↓
LangChain Tool Wrapper (for orchestrator)
```

## Installation

### 1. Clone and Setup

```bash
cd face-verification-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
python main.py
```

Server starts at `http://localhost:8000`

## API Endpoints

### Health Check

```bash
curl -X GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "face-v1",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### Face Verification

```bash
curl -X POST http://localhost:8000/face/verify \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "app-0001",
    "id_crop_evidence": {
      "evidence_id": "ev-idcrop-001",
      "file_uri": "./data/app-0001/ev-idcrop-001.jpg",
      "file_sha256": "abc123..."
    },
    "selfie_evidence": {
      "evidence_id": "ev-selfie-001",
      "file_uri": "./data/app-0001/ev-selfie-001.jpg",
      "file_sha256": "def456..."
    },
    "requested_checks": ["similarity", "liveness"]
  }'
```

**Response:**
```json
{
  "application_id": "app-0001",
  "similarity": 0.8945,
  "similarity_metric": "cosine",
  "liveness_score": 0.9512,
  "match_confidence": 0.8701,
  "embedding_id_selfie": "emb-3a7f1b2c",
  "embedding_id_idcrop": "emb-5e2d4c9f",
  "agent_version": "face-v1",
  "ts": "2024-01-15T10:30:45.123456"
}
```

## Input/Output Contracts

### Input Contract (POST /face/verify)

```json
{
  "application_id": "string (required)",
  "id_crop_evidence": {
    "evidence_id": "string (required)",
    "file_uri": "string (required)",
    "file_sha256": "string (optional)"
  },
  "selfie_evidence": {
    "evidence_id": "string (required)",
    "file_uri": "string (required)",
    "file_sha256": "string (optional)"
  },
  "requested_checks": ["similarity", "liveness"]
}
```

### Output Contract

```json
{
  "application_id": "string",
  "similarity": "float (0.0-1.0)",
  "similarity_metric": "cosine",
  "liveness_score": "float (0.0-1.0)",
  "match_confidence": "float (0.0-1.0)",
  "embedding_id_selfie": "string",
  "embedding_id_idcrop": "string",
  "agent_version": "face-v1",
  "ts": "ISO 8601 timestamp"
}
```

## LangChain Tool Integration

Import and use in orchestrator:

```python
from main import face_verify

# Direct function call
result = face_verify(
    application_id="app-0001",
    id_crop_file_uri="./data/app-0001/id_crop.jpg",
    selfie_file_uri="./data/app-0001/selfie.jpg",
    id_crop_evidence_id="ev-idcrop-001",
    selfie_evidence_id="ev-selfie-001",
    requested_checks=["similarity", "liveness"]
)

print(result)
# {
#     'application_id': 'app-0001',
#     'similarity': 0.89,
#     'similarity_metric': 'cosine',
#     'liveness_score': 0.95,
#     'match_confidence': 0.87,
#     ...
# }
```

Or use with LangChain agents:

```python
from langchain.agents import AgentExecutor, Tool
from main import face_verify

# Create tool for agent
face_tool = Tool(
    name="face_verify",
    func=face_verify,
    description="Verify face identity and liveness for loan application"
)

# Use in agent chain...
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | FastAPI | REST API endpoints |
| Detection | MediaPipe | Face detection & landmarks |
| Embeddings | FaceNet-PyTorch | 512-dim face embeddings |
| Liveness | MediaPipe + CV2 | Blink & motion analysis |
| Storage | SQLite + JSON | Embedding persistence |
| Orchestration | LangChain | Multi-agent coordination |
| Containerization | Docker | Production deployment |

## Configuration

Set environment variables:

```bash
export HOST=0.0.0.0
export PORT=8000
export DATABASE_PATH=./embeddings.db
```

Or in `.env` file:
```
HOST=0.0.0.0
PORT=8000
DATABASE_PATH=./embeddings.db
```

## Docker Deployment

### Build Image

```bash
docker build -t face-verification-agent:1.0 .
```

### Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  --name face-agent \
  face-verification-agent:1.0
```

### Check Health

```bash
docker exec face-agent curl http://localhost:8000/health
```

## Testing

### Run Test Suite

```bash
pytest tests/test_face.py -v
```

### Run with Coverage

```bash
pytest tests/test_face.py --cov=. --cov-report=html
```

### Test Categories

1. **Face Utils Tests**
   - Similarity computation
   - Image loading
   - Face detection failures

2. **Liveness Tests**
   - Eye aspect ratio (EAR) calculation
   - Blink detection
   - Facial landmark validation

3. **Database Tests**
   - Embedding storage/retrieval
   - Verification result tracking
   - Query operations

4. **Integration Tests**
   - Matching face pairs (high similarity)
   - Non-matching faces (low similarity)
   - No-face error handling
   - Input/output contract validation

### Example Test Output

```
tests/test_face.py::TestFaceUtils::test_compute_similarity_identical_embeddings PASSED
tests/test_face.py::TestFaceUtils::test_compute_similarity_different_embeddings PASSED
tests/test_face.py::TestLivenessDetector::test_eye_aspect_ratio_open_eye PASSED
tests/test_face.py::TestEmbeddingDB::test_store_and_retrieve_embedding PASSED
tests/test_face.py::TestFaceVerificationIntegration::test_verify_face_matching_pair PASSED
tests/test_face.py::TestInputOutputContracts::test_output_contract_structure PASSED
=============================== 6 passed in 2.34s ===============================
```

## File Structure

```
face-verification-agent/
├── main.py                    # FastAPI app + LangChain tool
├── face_utils.py             # Face detection & embeddings
├── liveness.py               # Liveness detection
├── db.py                     # SQLite embedding storage
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container config
├── README.md                 # This file
├── tests/
│   └── test_face.py         # Comprehensive test suite
└── data/                     # Image data directory
    ├── app-0001/
    │   ├── ev-idcrop-001.jpg
    │   └── ev-selfie-001.jpg
    └── ...
```

## API Error Responses

### 400 Bad Request - No Face Detected

```json
{
  "detail": "Failed to detect face in ID crop: ./data/app-0001/ev-idcrop-001.jpg"
}
```

### 400 Bad Request - Invalid Image Path

```json
{
  "detail": "Image not found: ./data/nonexistent.jpg"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error: [error message]"
}
```

## Performance Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Response Time | < 3s | Per verification |
| Face Detection | 99%+ | With clear frontal faces |
| Embedding Quality | 512-dim | FaceNet output |
| Liveness Accuracy | 90%+ | Against spoofing attacks |
| Throughput | 100+ req/min | Single instance |
| Database | SQLite | <100K embeddings |

## Security Considerations

1. **Image Storage** - Images stored with file_uri only (no raw data stored)
2. **Embedding Privacy** - Embeddings stored as JSON (not raw pixel data)
3. **Evidence Tracking** - SHA256 hashing for file integrity
4. **Access Control** - Implement API authentication in production
5. **Data Retention** - Auto-delete embeddings after 90 days (configurable)

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'torch'

**Solution:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Issue: No module named 'mediapipe'

**Solution:**
```bash
pip install mediapipe==0.10.1
```

### Issue: Face detection fails on low-quality images

**Solution:**
- Ensure image resolution ≥ 300x300 pixels
- Check lighting conditions (avoid backlighting)
- Ensure face is frontal (not severely angled)

### Issue: Embedding database locked

**Solution:**
```bash
# Close all connections and restart
rm embeddings.db
python main.py
```

## Performance Optimization

### 1. Batch Processing (if needed)

```python
from face_utils import FaceUtils
from db import EmbeddingDB

# Process multiple applicants
for app_id in app_ids:
    # Parallel processing
    pass
```

### 2. Caching

Enable embedding caching for frequently verified faces:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_embedding(embedding_id: str):
    return db.get_embedding(embedding_id)
```

### 3. Database Optimization

Cleanup old embeddings periodically:
```bash
# Schedule in cron
0 2 * * * python -c "from db import EmbeddingDB; EmbeddingDB().delete_old_embeddings(90)"
```

## Maintenance

### Regular Tasks

```bash
# Clean old embeddings (90+ days)
python -c "from db import EmbeddingDB; db = EmbeddingDB(); db.delete_old_embeddings(90)"

# Monitor logs
tail -f embeddings.db

# Backup database
cp embeddings.db embeddings.db.backup.$(date +%s)
```

## Contributing

1. Add tests for new features
2. Run full test suite: `pytest tests/ -v`
3. Maintain >80% code coverage
4. Follow PEP 8 style guide

## License

Proprietary - MSN UNISYS Loan Origination System

## Support

For issues or questions:
- Check logs: Application uses standard Python logging
- Review test cases for usage examples
- Refer to input/output contracts for API specs
