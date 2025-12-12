# End-to-end test: Intake + KYC flow
# Tests: collect slots, upload PAN, verify OCR matching

param(
    [string]$IntakeUrl = "http://localhost:8001",
    [string]$KycUrl = "http://localhost:8002"
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Intake + KYC End-to-End Test" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Test IDs
$appId = "test-app-$(Get-Random -Minimum 1000 -Maximum 9999)"
$convId = "test-conv-$(Get-Random -Minimum 1000 -Maximum 9999)"

Write-Host "Application ID: $appId" -ForegroundColor Yellow
Write-Host "Conversation ID: $convId" -ForegroundColor Yellow
Write-Host ""

# ============ Step 1: Health Checks ============
Write-Host "[STEP 1] Health Checks" -ForegroundColor Green
Write-Host "---" -ForegroundColor Green

try {
    $intakeHealth = Invoke-WebRequest -Uri "$IntakeUrl/health" -Method Get -TimeoutSec 5 | ConvertFrom-Json
    Write-Host "OK - Intake Agent healthy at $IntakeUrl" -ForegroundColor Green
    Write-Host "  Version: $($intakeHealth.version)" -ForegroundColor Gray
} catch {
    Write-Host "FAILED - Intake Agent NOT responding at $IntakeUrl" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

try {
    $kycHealth = Invoke-WebRequest -Uri "$KycUrl/health" -Method Get -TimeoutSec 5 | ConvertFrom-Json
    Write-Host "OK - KYC Agent healthy at $KycUrl" -ForegroundColor Green
    Write-Host "  Version: $($kycHealth.version)" -ForegroundColor Gray
} catch {
    Write-Host "FAILED - KYC Agent NOT responding at $KycUrl" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============ Step 2: Conversational Intake ============
Write-Host "[STEP 2] Collect User Data (Chat)" -ForegroundColor Green
Write-Host "---" -ForegroundColor Green

$converseReq = @{
    application_id = $appId
    conversation_id = $convId
    user_message = "My name is John Doe, email is john@example.com, phone is 9876543210, I need 500000 rupees for home renovation, I earn 75000 per month, and my PAN is ABCDE1234F"
} | ConvertTo-Json

try {
    $converseResp = Invoke-WebRequest -Uri "$IntakeUrl/chat/converse" -Method Post -Body $converseReq -ContentType "application/json" | ConvertFrom-Json
    
    Write-Host "OK - Chat processed successfully" -ForegroundColor Green
    Write-Host "  Extracted slots:" -ForegroundColor Gray
    $converseResp.slots | Get-Member -MemberType NoteProperty | ForEach-Object {
        Write-Host "    - $($_.Name)" -ForegroundColor Gray
    }
    Write-Host "  Assistant: $($converseResp.assistant_reply)" -ForegroundColor Gray
    
} catch {
    Write-Host "FAILED - Chat processing error" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============ Step 3: Create Test PAN Image ============
Write-Host "[STEP 3] Create Test PAN Image" -ForegroundColor Green
Write-Host "---" -ForegroundColor Green

$uploadDir = "c:\Users\Nithin J\OneDrive\Desktop\codered\agents\kyc_agent\data\uploads"
$testImagePath = "$uploadDir\test_pan_$($appId).txt"

# Create upload directory if not exists
if (-not (Test-Path $uploadDir)) {
    New-Item -ItemType Directory -Path $uploadDir -Force | Out-Null
    Write-Host "OK - Created upload directory: $uploadDir" -ForegroundColor Green
}

# Create test PAN content
$panContent = "INCOME TAX DEPARTMENT`nPAN CARD`nPAN Number: ABCDE1234F`nName: JOHN DOE`nDate of Birth: 01/01/1985`nDate of Issue: 15/03/2010"

# Save test file
$panContent | Out-File -FilePath $testImagePath -Encoding UTF8 -Force
Write-Host "OK - Test PAN file created: $testImagePath" -ForegroundColor Green

Write-Host ""

# ============ Step 4: Upload PAN and Trigger KYC Parse ============
Write-Host "[STEP 4] Upload PAN and Trigger KYC Parse" -ForegroundColor Green
Write-Host "---" -ForegroundColor Green

$uploadReq = @{
    application_id = $appId
    conversation_id = $convId
    doc_type = "pan"
    file_path = $testImagePath
    evidence_id = "pan-ev-001"
} | ConvertTo-Json

try {
    Write-Host "  Sending upload request to Intake..." -ForegroundColor Gray
    $uploadResp = Invoke-WebRequest -Uri "$IntakeUrl/chat/upload" -Method Post -Body $uploadReq -ContentType "application/json" | ConvertFrom-Json
    
    Write-Host "OK - Upload and KYC completed" -ForegroundColor Green
    
    # Check for validation errors
    if ($uploadResp.actions) {
        Write-Host "  Actions returned:" -ForegroundColor Gray
        foreach ($action in $uploadResp.actions) {
            $statusColor = if ($action.type -eq "kyc_success") { "Green" } elseif ($action.type -like "*error*") { "Red" } else { "Yellow" }
            Write-Host "    [$($action.type)] $($action.message)" -ForegroundColor $statusColor
        }
    }
    
    # Show KYC result if available
    if ($uploadResp.kyc_result) {
        Write-Host "  KYC Results:" -ForegroundColor Gray
        Write-Host "    Overall Confidence: $($uploadResp.kyc_result.overall_confidence)" -ForegroundColor Gray
        
        if ($uploadResp.kyc_result.ocr.structured_fields) {
            Write-Host "    Extracted Fields:" -ForegroundColor Gray
            $uploadResp.kyc_result.ocr.structured_fields | Get-Member -MemberType NoteProperty | ForEach-Object {
                $value = $uploadResp.kyc_result.ocr.structured_fields.($_.Name)
                Write-Host "      - $($_.Name): $value" -ForegroundColor Gray
            }
        }
    }
    
} catch {
    Write-Host "FAILED - Upload error" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============ Step 5: Verify Slot Matching ============
Write-Host "[STEP 5] Verify Slot vs OCR Matching" -ForegroundColor Green
Write-Host "---" -ForegroundColor Green

$panFromSlot = $converseResp.slots.pan_number
$panFromOcr = $uploadResp.kyc_result.ocr.structured_fields.pan_number

if ($panFromSlot -eq $panFromOcr) {
    Write-Host "OK - PAN matches: $panFromSlot" -ForegroundColor Green
} else {
    Write-Host "WARNING - PAN mismatch" -ForegroundColor Yellow
    Write-Host "  User stated: $panFromSlot" -ForegroundColor Yellow
    Write-Host "  OCR found: $panFromOcr" -ForegroundColor Yellow
}

Write-Host ""

# ============ Step 6: Submit Application ============
Write-Host "[STEP 6] Submit Application" -ForegroundColor Green
Write-Host "---" -ForegroundColor Green

$submitReq = @{
    application_id = $appId
    conversation_id = $convId
} | ConvertTo-Json

try {
    $submitResp = Invoke-WebRequest -Uri "$IntakeUrl/chat/submit" -Method Post -Body $submitReq -ContentType "application/json" | ConvertFrom-Json
    
    Write-Host "OK - Application submitted" -ForegroundColor Green
    Write-Host "  Final message: $($submitResp.assistant_reply)" -ForegroundColor Gray
    
    if ($submitResp.actions) {
        foreach ($action in $submitResp.actions) {
            $statusColor = if ($action.type -eq "submit_success") { "Green" } else { "Yellow" }
            Write-Host "    [$($action.type)] $($action.message)" -ForegroundColor $statusColor
        }
    }
    
} catch {
    Write-Host "FAILED - Submit error" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "SUCCESS - All tests passed" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
