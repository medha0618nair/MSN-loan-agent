# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Local Python (Fastest)

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run
python main.py

# 3. Test
curl http://localhost:8000/health
```

### Option 2: Docker (Recommended for Production)

```bash
# 1. Build
docker build -t face-verification-agent:1.0 .

# 2. Run
docker run -p 8000:8000 -v $(pwd)/data:/app/data face-verification-agent:1.0

# 3. Test
curl http://localhost:8000/health
```

### Option 3: Docker Compose (All-in-One)

```bash
# 1. Start
docker-compose up -d

# 2. Check status
docker-compose logs -f face-verification-agent

# 3. Test
curl http://localhost:8000/health

# 4. Stop
docker-compose down
```

---

## 📝 Example API Call

Create a test with sample images:

```bash
# Copy test images to data directory
mkdir -p data/app-test-001
# Place your test images here:
# - data/app-test-001/id_crop.jpg
# - data/app-test-001/selfie.jpg

# Call the API
curl -X POST http://localhost:8000/face/verify \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "app-test-001",
    "id_crop_evidence": {
      "evidence_id": "ev-idcrop-001",
      "file_uri": "./data/app-test-001/id_crop.jpg"
    },
    "selfie_evidence": {
      "evidence_id": "ev-selfie-001",
      "file_uri": "./data/app-test-001/selfie.jpg"
    },
    "requested_checks": ["similarity", "liveness"]
  }'
```

---

## 🧪 Run Tests

```bash
# All tests
pytest tests/test_face.py -v

# Specific test
pytest tests/test_face.py::TestFaceUtils::test_compute_similarity_identical_embeddings -v

# With coverage
pytest tests/test_face.py --cov=. --cov-report=html
open htmlcov/index.html
```

---

## 📚 Documentation

- **Full API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`
- **README**: See `README.md` for complete documentation
- **Contracts**: See INPUT/OUTPUT CONTRACTS in README.md

---

## 🔧 Configuration

Edit environment variables:

```bash
export HOST=0.0.0.0
export PORT=8000
```

Or create `.env`:
```
HOST=0.0.0.0
PORT=8000
```

---

## 📊 What Gets Generated

After verification, the system creates:

1. **Embeddings** - 512-dim face vectors stored in SQLite
2. **Verification Records** - Similarity, liveness, match confidence scores
3. **Metadata** - Face detection confidence, file integrity hashes

Query stored data:
```python
from db import EmbeddingDB

db = EmbeddingDB()
embeddings = db.get_embeddings_by_application("app-test-001")
result = db.get_verification_result("result-id")
```

---

## ✅ Verification Results Interpretation

| Metric | Range | Interpretation |
|--------|-------|-----------------|
| `similarity` | 0.0-1.0 | Face match (>0.85 = match) |
| `liveness_score` | 0.0-1.0 | Authenticity (>0.90 = live) |
| `match_confidence` | 0.0-1.0 | Combined score (>0.85 = pass) |

---

## 🐛 Troubleshooting

**Issue**: `ModuleNotFoundError`
```bash
pip install -r requirements.txt --upgrade
```

**Issue**: Port 8000 already in use
```bash
# Use different port
PORT=8001 python main.py
```

**Issue**: Face detection fails
- Ensure image is clear, frontal face
- Image size ≥ 300x300 pixels
- Good lighting (avoid shadows)

---

## 📞 Integration with LangChain

```python
from main import face_verify

# Direct call
result = face_verify(
    application_id="app-0001",
    id_crop_file_uri="./data/app-0001/id_crop.jpg",
    selfie_file_uri="./data/app-0001/selfie.jpg"
)
print(result)
```

---

## Next Steps

1. ✅ **Test locally** - Verify setup works
2. 📊 **Prepare test images** - Add sample images to `data/` folder
3. 🧪 **Run test suite** - Ensure all tests pass
4. 🐳 **Build Docker image** - For production deployment
5. 🔌 **Integrate with orchestrator** - Connect to LangChain agent

---

**Questions?** Check README.md for complete documentation.
