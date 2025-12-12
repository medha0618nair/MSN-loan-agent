#!/usr/bin/env pwsh
# Complete PAN verification flow test
# Tests: conversation -> upload PAN -> OCR extraction -> verification

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PAN Verification Flow Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$INTAKE_URL = "http://localhost:8001"
$KYC_URL = "http://localhost:8002"
$APP_ID = "test-pan-flow-$(Get-Random -Maximum 9999)"
$CONV_ID = "conv-001"
$PAN_FILE = "c:\Users\Nithin J\OneDrive\Desktop\codered\agents\kyc_agent\data\uploads\WhatsApp Image 2025-12-11 at 7.30.39 PM (1).jpeg"

# Step 1: Health check both services
Write-Host "Step 1: Checking services health..." -ForegroundColor Yellow
try {
    $intakeHealth = Invoke-RestMethod -Method Get -Uri "$INTAKE_URL/health" -ErrorAction Stop
    Write-Host "  [OK] Intake service: $($intakeHealth.status)" -ForegroundColor Green
    
    $kycHealth = Invoke-RestMethod -Method Get -Uri "$KYC_URL/health" -ErrorAction Stop
    Write-Host "  [OK] KYC service: $($kycHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "  [X] Service health check failed: $_" -ForegroundColor Red
    Write-Host "`nMake sure both services are running:" -ForegroundColor Yellow
    Write-Host "  Terminal 1: cd agents\intake_agent; python main.py" -ForegroundColor Gray
    Write-Host "  Terminal 2: cd agents\kyc_agent; `$env:PATH += ';C:\Program Files\Tesseract-OCR'; python main.py" -ForegroundColor Gray
    exit 1
}

# Step 2: Start conversation with user details
Write-Host "`nStep 2: Providing user information via conversation..." -ForegroundColor Yellow
$conversationBody = @{
    application_id = $APP_ID
    conversation_id = $CONV_ID
    user_message = "My name is NITHIN J, email nithin@example.com, phone 9876543210, I need a loan of 500000 for home renovation, my PAN is DIJPN7537R"
    context = @{}
} | ConvertTo-Json

try {
    $converseResp = Invoke-RestMethod -Method Post -Uri "$INTAKE_URL/chat/converse" `
        -ContentType "application/json" -Body $conversationBody -ErrorAction Stop
    
    Write-Host "  [OK] Conversation successful" -ForegroundColor Green
    Write-Host "    Assistant: $($converseResp.assistant_reply)" -ForegroundColor Gray
    Write-Host "    Slots collected: $($converseResp.slots.PSObject.Properties.Name.Count)" -ForegroundColor Gray
    
    # Display collected slots
    Write-Host "`n  Collected Information:" -ForegroundColor Cyan
    $converseResp.slots.PSObject.Properties | ForEach-Object {
        Write-Host "    - $($_.Name): $($_.Value)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [X] Conversation failed: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Upload PAN card for OCR verification
Write-Host "`nStep 3: Uploading PAN card for OCR verification..." -ForegroundColor Yellow

if (-not (Test-Path $PAN_FILE)) {
    Write-Host "  [X] PAN file not found: $PAN_FILE" -ForegroundColor Red
    exit 1
}

$uploadBody = @{
    application_id = $APP_ID
    conversation_id = $CONV_ID
    doc_type = "pan"
    file_path = $PAN_FILE
    evidence_id = "pan-evidence-001"
} | ConvertTo-Json

try {
    $uploadResp = Invoke-RestMethod -Method Post -Uri "$INTAKE_URL/chat/upload" `
        -ContentType "application/json" -Body $uploadBody -ErrorAction Stop
    
    Write-Host "  [OK] Upload and OCR successful" -ForegroundColor Green
    
    # Display OCR results
    if ($uploadResp.kyc_result) {
        $ocr = $uploadResp.kyc_result.ocr
        $structured = $ocr.structured_fields
        
        Write-Host "`n  OCR Extracted Data:" -ForegroundColor Cyan
        Write-Host "    - PAN Number: $($structured.pan_number)" -ForegroundColor Gray
        Write-Host "    - Name: $($structured.name)" -ForegroundColor Gray
        Write-Host "    - Confidence: $([math]::Round($uploadResp.kyc_result.overall_confidence * 100, 2))%" -ForegroundColor Gray
        
        # Check validation
        if ($uploadResp.kyc_result.validation_errors -and $uploadResp.kyc_result.validation_errors.Count -gt 0) {
            Write-Host "`n  Validation Errors:" -ForegroundColor Red
            $uploadResp.kyc_result.validation_errors | ForEach-Object {
                Write-Host "    [X] $_" -ForegroundColor Red
            }
        } else {
            Write-Host "`n  [OK] No validation errors" -ForegroundColor Green
        }
        
        # Check for mismatches
        $mismatches = $uploadResp.actions | Where-Object { $_.type -eq "kyc_slot_mismatch" }
        if ($mismatches -and $mismatches.Count -gt 0) {
            Write-Host "`n  Slot Mismatches:" -ForegroundColor Yellow
            $mismatches | ForEach-Object {
                Write-Host "    [!] $($_.message)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  [OK] Provided PAN matches OCR extracted PAN" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "  [X] Upload failed: $_" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "    Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    exit 1
}

# Step 4: Display final application state
Write-Host "`nStep 4: Final Application State" -ForegroundColor Yellow
Write-Host "  Application ID: $APP_ID" -ForegroundColor Gray
Write-Host "  Total Actions: $($uploadResp.actions.Count)" -ForegroundColor Gray

$uploadResp.actions | ForEach-Object {
    $icon = switch ($_.type) {
        "kyc_success" { "[OK]" }
        "kyc_validation_error" { "[X]" }
        "kyc_slot_mismatch" { "[!]" }
        "upload_request" { "[-]" }
        default { "[·]" }
    }
    $color = switch ($_.type) {
        "kyc_success" { "Green" }
        "kyc_validation_error" { "Red" }
        "kyc_slot_mismatch" { "Yellow" }
        default { "Gray" }
    }
    Write-Host "    $icon $($_.message)" -ForegroundColor $color
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Verification Complete!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Summary:" -ForegroundColor White
Write-Host "  • User details collected from conversation" -ForegroundColor Gray
Write-Host "  • PAN card uploaded and processed via OCR" -ForegroundColor Gray
Write-Host "  • Extracted PAN: $($uploadResp.kyc_result.ocr.structured_fields.pan_number)" -ForegroundColor Gray
Write-Host "  • Extracted Name: $($uploadResp.kyc_result.ocr.structured_fields.name)" -ForegroundColor Gray

if ($uploadResp.kyc_result.validation_errors.Count -eq 0 -and 
    -not ($uploadResp.actions | Where-Object { $_.type -eq "kyc_slot_mismatch" })) {
    Write-Host "`n[OK] All verifications passed!" -ForegroundColor Green
} else {
    Write-Host "`n[!] Some validations require attention" -ForegroundColor Yellow
}

Write-Host ""
