#!/usr/bin/env pwsh
# Bank Agent Test Script

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Bank Statement Agent Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$BANK_URL = "http://localhost:8003"
$APP_ID = "test-bank-$(Get-Random -Maximum 9999)"

# Step 1: Health check
Write-Host "Step 1: Checking Bank Agent health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Method Get -Uri "$BANK_URL/health" -ErrorAction Stop
    Write-Host "  [OK] Bank Agent: $($health.status) ($($health.version))`n" -ForegroundColor Green
} catch {
    Write-Host "  [X] Bank Agent not running" -ForegroundColor Red
    Write-Host "`nStart the service with:" -ForegroundColor Yellow
    Write-Host "  cd agents\bank-agent" -ForegroundColor Gray
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host "  python main.py" -ForegroundColor Gray
    exit 1
}

# Step 2: Check for CSV file
Write-Host "Step 2: Checking for bank statement CSV..." -ForegroundColor Yellow

# Prompt user for file path
$csvPath = Read-Host "Enter path to your bank statement CSV (or press Enter to skip)"

if ([string]::IsNullOrWhiteSpace($csvPath)) {
    Write-Host "`n[!] No file provided. Please upload your CSV to:" -ForegroundColor Yellow
    Write-Host "    agents\bank-agent\data\your_statement.csv`n" -ForegroundColor Gray
    
    Write-Host "Required CSV format:" -ForegroundColor Cyan
    Write-Host @"
date,amount,description
2025-09-05,45000,SALARY CREDIT
2025-09-10,-2500,UPI PAYMENT
2025-10-05,45100,SALARY CREDIT
2025-10-12,-3000,BILL PAYMENT
2025-11-05,45000,SALARY CREDIT

"@ -ForegroundColor Gray
    
    Write-Host "Column requirements:" -ForegroundColor Cyan
    Write-Host "  - date: Transaction date (YYYY-MM-DD or DD-MM-YYYY)" -ForegroundColor Gray
    Write-Host "  - amount: Positive=credit, Negative=debit" -ForegroundColor Gray
    Write-Host "  - description: Must contain keywords like 'SALARY', 'PAYROLL'" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

# Validate file exists
if (-not (Test-Path $csvPath)) {
    Write-Host "  [X] File not found: $csvPath" -ForegroundColor Red
    exit 1
}

Write-Host "  [OK] Found: $csvPath`n" -ForegroundColor Green

# Step 3: Parse bank statement
Write-Host "Step 3: Parsing bank statement..." -ForegroundColor Yellow

$body = @{
    application_id = $APP_ID
    evidence_id    = "bank-ev-001"
    file_uri       = $csvPath
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Method Post -Uri "$BANK_URL/bank/parse" `
        -ContentType "application/json" -Body $body -ErrorAction Stop
    
    Write-Host "  [OK] Parsing complete`n" -ForegroundColor Green
    
    # Display results
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Salary Detection Results" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "Salary Detected: " -NoNewline
    if ($result.bank_salary_detected) {
        Write-Host "YES" -ForegroundColor Green
    } else {
        Write-Host "NO" -ForegroundColor Red
    }
    
    Write-Host "`nSalary Details:" -ForegroundColor Yellow
    Write-Host "  Months detected: $($result.months_salary_detected)" -ForegroundColor Gray
    Write-Host "  Salary amounts: $($result.salary_amounts -join ', ')" -ForegroundColor Gray
    Write-Host "  Salary dates: $($result.salary_dates -join ', ')" -ForegroundColor Gray
    
    Write-Host "`nIncome Metrics:" -ForegroundColor Yellow
    Write-Host "  Average salary: ₹$($result.avg_salary)" -ForegroundColor Gray
    Write-Host "  Median salary: ₹$($result.median_salary)" -ForegroundColor Gray
    Write-Host "  Monthly income estimate: ₹$($result.monthly_income_estimate)" -ForegroundColor Gray
    
    Write-Host "`nQuality Scores:" -ForegroundColor Yellow
    Write-Host "  Payroll consistency: $([math]::Round($result.payroll_consistency * 100, 2))%" -ForegroundColor Gray
    Write-Host "  Confidence: $([math]::Round($result.confidence * 100, 2))%" -ForegroundColor Gray
    Write-Host "  Salary share of credits: $([math]::Round($result.salary_share_of_credits * 100, 2))%" -ForegroundColor Gray
    Write-Host "  Inflow std deviation: ₹$($result.inflow_std)" -ForegroundColor Gray
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Analysis Complete!" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
} catch {
    $errorDetail = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
    Write-Host "  [X] Parsing failed" -ForegroundColor Red
    
    if ($errorDetail) {
        Write-Host "`nError: $($errorDetail.detail)" -ForegroundColor Red
        
        if ($errorDetail.detail -eq "no_salary_detected") {
            Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
            Write-Host "  - Ensure descriptions contain keywords: SALARY, PAYROLL, SAL" -ForegroundColor Gray
            Write-Host "  - Check amount range: 10,000 - 500,000 INR" -ForegroundColor Gray
            Write-Host "  - Need at least 2 recurring monthly transactions" -ForegroundColor Gray
        }
    } else {
        Write-Host "`nError: $_" -ForegroundColor Red
    }
    exit 1
}
