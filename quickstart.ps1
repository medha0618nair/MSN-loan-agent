# Quick Start Guide

## Prerequisites Check
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Cyan

# Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check Docker
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✅ Docker found" -ForegroundColor Green
} else {
    Write-Host "⚠️  Docker not found. Install for full functionality" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🏦 MULTI-AGENT LOAN ORIGINATION SYSTEM - QUICK START" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Check environment file
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter after updating .env file"
}

# Menu
Write-Host "Choose deployment option:" -ForegroundColor Cyan
Write-Host "1. Docker Compose (Recommended)" -ForegroundColor White
Write-Host "2. Local Development" -ForegroundColor White
Write-Host "3. Run Tests" -ForegroundColor White
Write-Host "4. View Documentation" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🐳 Starting services with Docker Compose..." -ForegroundColor Cyan
        docker-compose up -d
        
        Write-Host ""
        Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        Write-Host ""
        Write-Host "✅ Services started!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📍 Service URLs:" -ForegroundColor Cyan
        Write-Host "  Intake Agent:  http://localhost:8001" -ForegroundColor White
        Write-Host "  Intake Docs:   http://localhost:8001/docs" -ForegroundColor White
        Write-Host "  KYC Agent:     http://localhost:8002" -ForegroundColor White
        Write-Host "  KYC Docs:      http://localhost:8002/docs" -ForegroundColor White
        Write-Host ""
        Write-Host "🧪 Test endpoints:" -ForegroundColor Cyan
        Write-Host '  curl http://localhost:8001/health' -ForegroundColor Gray
        Write-Host '  curl http://localhost:8002/health' -ForegroundColor Gray
        Write-Host ""
        Write-Host "📊 View logs:" -ForegroundColor Cyan
        Write-Host "  docker-compose logs -f intake_agent" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🛑 Stop services:" -ForegroundColor Cyan
        Write-Host "  docker-compose down" -ForegroundColor Gray
    }
    
    "2" {
        Write-Host ""
        Write-Host "💻 Local Development Setup" -ForegroundColor Cyan
        Write-Host ""
        
        # Start Redis
        Write-Host "🔴 Starting Redis..." -ForegroundColor Yellow
        docker run -d -p 6379:6379 --name redis-loan redis:7-alpine
        
        Write-Host ""
        Write-Host "📦 Installing Intake Agent dependencies..." -ForegroundColor Yellow
        Set-Location "agents\intake_agent"
        pip install -r requirements.txt
        Set-Location "..\..\"
        
        Write-Host ""
        Write-Host "📦 Installing KYC Agent dependencies..." -ForegroundColor Yellow
        Set-Location "agents\kyc_agent"
        pip install -r requirements.txt
        Set-Location "..\..\"
        
        Write-Host ""
        Write-Host "✅ Setup complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "To run agents, open separate terminals:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Terminal 1 - Intake Agent:" -ForegroundColor White
        Write-Host "  cd agents\intake_agent" -ForegroundColor Gray
        Write-Host "  python main.py" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Terminal 2 - KYC Agent:" -ForegroundColor White
        Write-Host "  cd agents\kyc_agent" -ForegroundColor Gray
        Write-Host "  python main.py" -ForegroundColor Gray
    }
    
    "3" {
        Write-Host ""
        Write-Host "🧪 Running Tests..." -ForegroundColor Cyan
        Write-Host ""
        
        # Install pytest if needed
        pip install pytest pytest-cov httpx
        
        Write-Host ""
        Write-Host "Testing Intake Agent..." -ForegroundColor Yellow
        Set-Location "agents\intake_agent"
        pytest test_intake_agent.py -v
        Set-Location "..\..\"
        
        Write-Host ""
        Write-Host "Testing KYC Agent..." -ForegroundColor Yellow
        Set-Location "agents\kyc_agent"
        pytest test_kyc_agent.py -v
        Set-Location "..\..\"
        
        Write-Host ""
        Write-Host "✅ Tests complete!" -ForegroundColor Green
    }
    
    "4" {
        Write-Host ""
        Write-Host "📚 Documentation" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Main README:        README.md" -ForegroundColor White
        Write-Host "Intake Agent:       agents\intake_agent\README.md" -ForegroundColor White
        Write-Host "KYC Agent:          agents\kyc_agent\README.md" -ForegroundColor White
        Write-Host "Orchestrator Demo:  orchestrator_example.py" -ForegroundColor White
        Write-Host ""
        Write-Host "Opening main README..." -ForegroundColor Yellow
        Start-Process "README.md"
    }
    
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
