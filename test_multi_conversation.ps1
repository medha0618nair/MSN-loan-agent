#!/usr/bin/env pwsh
# Multi-conversation test - simulate multiple back-and-forth exchanges

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Multi-Conversation Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$INTAKE_URL = "http://localhost:8001"
$APP_ID = "test-conv-$(Get-Random -Maximum 9999)"
$CONV_ID = "conv-001"

# Health check
Write-Host "Checking Intake service health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Method Get -Uri "$INTAKE_URL/health" -ErrorAction Stop
    Write-Host "  [OK] Intake service: $($health.status)`n" -ForegroundColor Green
} catch {
    Write-Host "  [X] Service not running. Start with: cd agents\intake_agent; python main.py" -ForegroundColor Red
    exit 1
}

# Helper function to send message
function Send-Message {
    param(
        [string]$Message,
        [string]$Label
    )
    
    Write-Host "User: $Message" -ForegroundColor Cyan
    
    $body = @{
        application_id = $APP_ID
        conversation_id = $CONV_ID
        user_message = $Message
        context = @{}
    } | ConvertTo-Json
    
    $resp = Invoke-RestMethod -Method Post -Uri "$INTAKE_URL/chat/converse" `
        -ContentType "application/json" -Body $body -ErrorAction Stop
    
    Write-Host "Assistant: $($resp.assistant_reply)" -ForegroundColor Gray
    
    # Show collected slots
    $slotCount = $resp.slots.PSObject.Properties.Name.Count
    if ($slotCount -gt 0) {
        Write-Host "`nCollected slots ($slotCount):" -ForegroundColor Yellow
        $resp.slots.PSObject.Properties | ForEach-Object {
            Write-Host "  - $($_.Name): $($_.Value)" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    return $resp
}

# Conversation Flow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Multi-Turn Conversation" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Turn 1: Initial greeting
Write-Host "[Turn 1]" -ForegroundColor Magenta
$resp1 = Send-Message -Message "Hi, I need a loan" -Label "Greeting"

# Turn 2: Provide name and email
Write-Host "[Turn 2]" -ForegroundColor Magenta
$resp2 = Send-Message -Message "My name is Rajesh Kumar and email is rajesh.kumar@example.com" -Label "Name + Email"

# Turn 3: Provide phone
Write-Host "[Turn 3]" -ForegroundColor Magenta
$resp3 = Send-Message -Message "My phone number is 9876543210" -Label "Phone"

# Turn 4: Provide loan details
Write-Host "[Turn 4]" -ForegroundColor Magenta
$resp4 = Send-Message -Message "I need 750000 rupees for business expansion" -Label "Loan Amount + Purpose"

# Turn 5: Provide PAN
Write-Host "[Turn 5]" -ForegroundColor Magenta
$resp5 = Send-Message -Message "My PAN is ABCDE1234F" -Label "PAN Number"

# Turn 6: Additional info
Write-Host "[Turn 6]" -ForegroundColor Magenta
$resp6 = Send-Message -Message "I am self employed and my monthly income is around 80000" -Label "Employment + Income"

# Turn 7: Ask about loan eligibility (RAG query)
Write-Host "[Turn 7 - RAG Query]" -ForegroundColor Magenta
$resp7 = Send-Message -Message "What are the eligibility criteria for a business loan?" -Label "Eligibility Question"

# Turn 8: Ask about interest rates (RAG query)
Write-Host "[Turn 8 - RAG Query]" -ForegroundColor Magenta
$resp8 = Send-Message -Message "What is the interest rate for business loans?" -Label "Interest Rate Question"

# Turn 9: Ask about documents (RAG query)
Write-Host "[Turn 9 - RAG Query]" -ForegroundColor Magenta
$resp9 = Send-Message -Message "What documents do I need to submit for the loan?" -Label "Documents Question"

# Turn 10: Ask about loan tenure (RAG query)
Write-Host "[Turn 10 - RAG Query]" -ForegroundColor Magenta
$resp10 = Send-Message -Message "How long is the repayment period for business loans?" -Label "Tenure Question"

# Turn 11: Ask about processing time (RAG query)
Write-Host "[Turn 11 - RAG Query]" -ForegroundColor Magenta
$resp11 = Send-Message -Message "How long does it take to process my loan application?" -Label "Processing Time Question"

# Turn 12: Provide additional details
Write-Host "[Turn 12]" -ForegroundColor Magenta
$resp12 = Send-Message -Message "I also have a property worth 50 lakhs as collateral" -Label "Collateral Info"

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Conversation Summary" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Application ID: $APP_ID" -ForegroundColor White
Write-Host "Conversation ID: $CONV_ID" -ForegroundColor White
Write-Host "Total Turns: 12`n" -ForegroundColor White

Write-Host "Final Collected Information:" -ForegroundColor Yellow
$resp12.slots.PSObject.Properties | ForEach-Object {
    Write-Host "  [OK] $($_.Name): $($_.Value)" -ForegroundColor Green
}

# Check completeness
$required = @("full_name", "email", "phone", "loan_amount", "loan_purpose")
$collected = $resp12.slots.PSObject.Properties.Name
$missing = $required | Where-Object { $_ -notin $collected }

Write-Host "`nStatus:" -ForegroundColor Yellow
if ($missing.Count -eq 0) {
    Write-Host "  [OK] All required fields collected!" -ForegroundColor Green
} else {
    Write-Host "  [!] Missing fields: $($missing -join ', ')" -ForegroundColor Yellow
}

Write-Host ""
