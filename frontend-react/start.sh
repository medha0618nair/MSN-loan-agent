#!/bin/bash
# Quick start script for MSN Loan Agent Frontend

echo "=========================================="
echo "MSN Loan Agent Frontend - Quick Start"
echo "=========================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 14+ first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

# Check if npm dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

echo "=========================================="
echo "Configuration:"
echo "=========================================="
echo "REACT_APP_INTAKE_URL=http://localhost:8001"
echo "REACT_APP_KYC_URL=http://localhost:8002"
echo "REACT_APP_FACE_URL=http://localhost:8003"
echo "REACT_APP_PAYSLIP_URL=http://localhost:8004"
echo "REACT_APP_BANK_URL=http://localhost:8005"
echo "REACT_APP_CREDIT_URL=http://localhost:8006"
echo "REACT_APP_ORCH_URL=http://localhost:9000"
echo ""

echo "=========================================="
echo "✨ Starting development server..."
echo "=========================================="
echo "Frontend will open at: http://localhost:3000"
echo ""
echo "To stop: Press Ctrl+C"
echo ""

npm start
