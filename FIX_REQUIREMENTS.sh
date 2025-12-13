#!/bin/bash
# Fix all agent requirements - compatible versions

BASE="/Users/apple/Desktop/codered final/MSN-loan-agent"

echo "🔧 Fixing dependencies for all agents..."

# KYC Agent
echo "📦 Updating kyc_agent requirements..."
cat > "$BASE/agents/kyc_agent/requirements.txt" << 'EOF'
# KYC Agent Requirements
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.8.2
python-multipart==0.0.6

# OCR and document processing
pytesseract==0.3.10
Pillow==10.1.0
pdfplumber==0.10.3
pdf2image==1.16.3

# Vision and face detection
opencv-python==4.8.1.78
mediapipe==0.10.8
numpy==1.24.3

# LangChain
langchain==0.2.16
langchain-groq==0.1.9

# Utilities
python-dotenv==1.0.0
requests==2.31.0
EOF

# Face Agent
echo "📦 Updating face-agent requirements..."
cat > "$BASE/agents/face-agent/requirements.txt" << 'EOF'
# Face Agent Requirements
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.8.2
python-multipart==0.0.6

# Face detection and processing
mediapipe==0.10.8
opencv-python==4.8.1.78
Pillow==10.1.0
numpy==1.24.3

# LangChain
langchain==0.2.16
langchain-groq==0.1.9

# Utilities
python-dotenv==1.0.0
requests==2.31.0
EOF

# Payslip Agent
echo "📦 Updating payslip-agent requirements..."
cat > "$BASE/agents/payslip-agent/requirements.txt" << 'EOF'
# Payslip Agent Requirements
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.8.2
python-multipart==0.0.6

# Document processing
pdfplumber==0.10.3
pytesseract==0.3.10
pdf2image==1.16.3
Pillow==10.1.0

# OCR
pytesseract==0.3.10

# LangChain
langchain==0.2.16
langchain-groq==0.1.9

# Utilities
python-dotenv==1.0.0
requests==2.31.0
EOF

# Bank Agent
echo "📦 Updating bank-agent requirements..."
cat > "$BASE/agents/bank-agent/requirements.txt" << 'EOF'
# Bank Agent Requirements
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.8.2
python-multipart==0.0.6

# Document processing
pdfplumber==0.10.3
pdf2image==1.16.3
pytesseract==0.3.10
Pillow==10.1.0

# Data processing
pandas==2.2.0
numpy==1.24.3

# LangChain
langchain==0.2.16
langchain-groq==0.1.9

# Utilities
python-dotenv==1.0.0
requests==2.31.0
EOF

# Credit Agent
echo "📦 Updating credit-agent requirements..."
cat > "$BASE/agents/credit-agent/requirements.txt" << 'EOF'
# Credit Agent Requirements
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.8.2
python-multipart==0.0.6

# Data processing
pandas==2.2.0
numpy==1.24.3
scikit-learn==1.8.0

# LangChain
langchain==0.2.16
langchain-groq==0.1.9

# Utilities
python-dotenv==1.0.0
requests==2.31.0
EOF

echo "✅ All requirements files updated!"
