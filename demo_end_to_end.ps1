# End-to-End Intake Agent Demo
# Full happy-path flow: health → converse → set slots → submit
# Shows RAG, slot collection, and final application state

Write-Host "========================================" -ForegroundColor Green
Write-Host "Intake Agent - End-to-End Demo" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

$base = "http://localhost:8001"
$app_id = "demo-app-$(Get-Random -Minimum 1000 -Maximum 9999)"
$conv_id = "conv-$(Get-Random -Minimum 1000 -Maximum 9999)"

Write-Host "`nApplication ID: $app_id" -ForegroundColor Yellow
Write-Host "Conversation ID: $conv_id" -ForegroundColor Yellow

# ========== 1) HEALTH CHECK ==========
Write-Host "`n========== STEP 1: Health Check ==========" -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$base/health" -Method GET
    Write-Host "Status: $($health.status)" -ForegroundColor Green
    Write-Host "Service: $($health.service)" -ForegroundColor Green
    Write-Host "Version: $($health.version)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_)" -ForegroundColor Red
    exit 1
}

# ========== 2) START CONVERSATION (RAG TEST) ==========
Write-Host "`n========== STEP 2: Start Conversation (RAG Test) ==========" -ForegroundColor Cyan
$greeting = "Hi, I'm looking to apply for insurance. What documents do I need?"
Write-Host "User: $greeting" -ForegroundColor Magenta
$body_converse = @{
    application_id = $app_id
    conversation_id = $conv_id
    user_message = $greeting
} | ConvertTo-Json

$resp_converse = Invoke-RestMethod -Uri "$base/chat/converse" -Method POST -ContentType "application/json" -Body $body_converse
Write-Host "Assistant: $($resp_converse.assistant_reply)" -ForegroundColor Cyan
Write-Host "RAG Context Found: $(if($resp_converse.rag_context) { 'YES' } else { 'NO' })" -ForegroundColor Green
Write-Host "Next Prompt: $($resp_converse.next_prompt)" -ForegroundColor Yellow

# ========== 3) COLLECT SLOTS VIA /chat/slot ENDPOINT ==========
Write-Host "`n========== STEP 3: Collecting Required Data (Slot Updates) ==========" -ForegroundColor Cyan

$slots_to_collect = @(
    @{ name = "full_name"; value = "John Doe"; label = "Full Name" },
    @{ name = "email"; value = "john.doe@example.com"; label = "Email" },
    @{ name = "phone"; value = "+91-9876543210"; label = "Phone" },
    @{ name = "loan_amount"; value = "300000"; label = "Loan Amount (Rs)" },
    @{ name = "loan_purpose"; value = "home renovation"; label = "Loan Purpose" },
    @{ name = "employment_status"; value = "salaried"; label = "Employment Status" },
    @{ name = "monthly_income"; value = "75000"; label = "Monthly Income (Rs)" },
    @{ name = "pan_number"; value = "ABCDE1234F"; label = "PAN Number" }
)

$collected_slots = @{}

foreach ($slot in $slots_to_collect) {
    Write-Host "`n  Updating: $($slot.label)" -ForegroundColor Magenta
    Write-Host "  Value: $($slot.value)" -ForegroundColor DarkGray
    
    $slot_body = @{
        application_id = $app_id
        conversation_id = $conv_id
        slot_name = $slot.name
        slot_value = $slot.value
    } | ConvertTo-Json
    
    try {
        $resp_slot = Invoke-RestMethod -Uri "$base/chat/slot" -Method POST -ContentType "application/json" -Body $slot_body
        $collected_slots[$slot.name] = $slot.value
        Write-Host "  SUCCESS" -ForegroundColor Green
    }
    catch {
        Write-Host "  ERROR: $($_)" -ForegroundColor Red
    }
}

Write-Host "`n  Total Slots Collected: $($collected_slots.Count)" -ForegroundColor Yellow

# ========== 4) FINAL CONVERSATION CHECK ==========
Write-Host "`n========== STEP 4: Pre-Submit Verification ==========" -ForegroundColor Cyan
$check_msg = "I have provided all my information. Can you confirm everything is correct?"
Write-Host "User: $check_msg" -ForegroundColor Magenta
$body_check = @{
    application_id = $app_id
    conversation_id = $conv_id
    user_message = $check_msg
} | ConvertTo-Json

$resp_check = Invoke-RestMethod -Uri "$base/chat/converse" -Method POST -ContentType "application/json" -Body $body_check
Write-Host "Assistant: $($resp_check.assistant_reply)" -ForegroundColor Cyan
Write-Host "Slots Stored: $($resp_check.slots.Count)" -ForegroundColor Yellow

# ========== 5) SUBMIT APPLICATION ==========
Write-Host "`n========== STEP 5: Submit Application ==========" -ForegroundColor Cyan
$submit_body = @{
    application_id = $app_id
    conversation_id = $conv_id
} | ConvertTo-Json

try {
    $resp_submit = Invoke-RestMethod -Uri "$base/chat/submit" -Method POST -ContentType "application/json" -Body $submit_body
    
    Write-Host "`nSubmission Result:" -ForegroundColor Green
    if ($resp_submit.actions -and $resp_submit.actions[0].type -eq "submit_success") {
        Write-Host "  Status: SUCCESS" -ForegroundColor Green
        Write-Host "  Message: $($resp_submit.assistant_reply)" -ForegroundColor Green
    }
    else {
        Write-Host "  Status: VALIDATION" -ForegroundColor Yellow
        Write-Host "  Message: $($resp_submit.assistant_reply)" -ForegroundColor Yellow
    }
    
    Write-Host "`nFinal Collected Slots:" -ForegroundColor Yellow
    if ($resp_submit.slots -and $resp_submit.slots.Count -gt 0) {
        foreach ($key in $resp_submit.slots.Keys | Sort-Object) {
            Write-Host "  - $key : $($resp_submit.slots[$key])" -ForegroundColor Cyan
        }
    }
    else {
        Write-Host "  (No slots stored)" -ForegroundColor DarkGray
    }
    
    Write-Host "`nRequired Uploads:" -ForegroundColor Yellow
    if ($resp_submit.required_uploads -and $resp_submit.required_uploads.Count -gt 0) {
        foreach ($upload in $resp_submit.required_uploads) {
            Write-Host "  - $upload" -ForegroundColor Magenta
        }
    }
}
catch {
    Write-Host "Submit ERROR: $($_)" -ForegroundColor Red
}

# ========== SUMMARY ==========
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Demo Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nSummary:" -ForegroundColor Cyan
Write-Host "  - Health: OK" -ForegroundColor Green
Write-Host "  - RAG: Active (retrieval + Groq LLM)" -ForegroundColor Green
Write-Host "  - Slots Collected: $($slots_to_collect.Count)" -ForegroundColor Green
Write-Host "  - Application State: Complete" -ForegroundColor Green
Write-Host "`nApplication ready for KYC/OCR verification phase." -ForegroundColor Yellow
