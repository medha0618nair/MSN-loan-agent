# Intake Agent - Multi-Turn Tests
$base = "http://localhost:8001"

Write-Host "========================================" -ForegroundColor Green
Write-Host "Intake Agent - Multi-Turn Tests" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# ----------------------
# Scenario 1: Slow fill (hello -> name -> email -> phone -> purpose/amount)
# ----------------------
$app_id = "test-slowfill-$(Get-Random -Minimum 1000 -Maximum 9999)"
$conv_id = "conv-$(Get-Random -Minimum 1000 -Maximum 9999)"
Write-Host "App ID: $app_id" -ForegroundColor Yellow

$messages = @(
    "Hello",
    "I'm Riya Sen",
    "Email is riya.sen@example.com",
    "Phone is +91 98765 43210",
    "I need 550000 for home renovation"
)

foreach ($m in $messages) {
    $body = @{
        application_id = $app_id
        conversation_id = $conv_id
        user_message = $m
    } | ConvertTo-Json

    try {
        $resp = Invoke-RestMethod -Uri "$base/chat/converse" -Method POST -ContentType "application/json" -Body $body
        $slotsNow = ($resp.slots.Keys | Sort-Object) -join ', '
        Write-Host "User: $m" -ForegroundColor Magenta
        Write-Host "Assistant: $($resp.assistant_reply)" -ForegroundColor Cyan
        Write-Host "Slots now: $slotsNow" -ForegroundColor Yellow
        Write-Host "---" -ForegroundColor DarkGray
    }
    catch {
        Write-Host "ERROR: $($_)" -ForegroundColor Red
    }
}

$submit_body = @{
    application_id = $app_id
    conversation_id = $conv_id
} | ConvertTo-Json

try {
    $resp = Invoke-RestMethod -Uri "$base/chat/submit" -Method POST -ContentType "application/json" -Body $submit_body
    Write-Host "Status: SLOW FILL SUBMIT" -ForegroundColor Green
    Write-Host "Collected Slots:" -ForegroundColor Yellow
    foreach ($key in $resp.slots.Keys | Sort-Object) {
        Write-Host "  - $key : $($resp.slots[$key])" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "ERROR: $($_)" -ForegroundColor Red
}

# ----------------------
# Scenario 2: Off-topic then course-correct back to loan data
# ----------------------
$app_id2 = "test-offtopic-$(Get-Random -Minimum 1000 -Maximum 9999)"
$conv_id2 = "conv-$(Get-Random -Minimum 1000 -Maximum 9999)"
Write-Host "`nApp ID: $app_id2 (off-topic correction)" -ForegroundColor Yellow

$messages2 = @(
    "Hey there",
    "What is your favorite movie?",
    "Sorry, for my loan my name is Karan Mehta",
    "Email karan.mehta@example.com",
    "Phone +91 99880 12345",
    "Need 750000 for business expansion"
)

foreach ($m in $messages2) {
    $body = @{
        application_id = $app_id2
        conversation_id = $conv_id2
        user_message = $m
    } | ConvertTo-Json

    try {
        $resp = Invoke-RestMethod -Uri "$base/chat/converse" -Method POST -ContentType "application/json" -Body $body
        $slotsNow = ($resp.slots.Keys | Sort-Object) -join ', '
        Write-Host "User: $m" -ForegroundColor Magenta
        Write-Host "Assistant: $($resp.assistant_reply)" -ForegroundColor Cyan
        Write-Host "Slots now: $slotsNow" -ForegroundColor Yellow
        Write-Host "---" -ForegroundColor DarkGray
    }
    catch {
        Write-Host "ERROR: $($_)" -ForegroundColor Red
    }
}

$submit_body2 = @{
    application_id = $app_id2
    conversation_id = $conv_id2
} | ConvertTo-Json

try {
    $resp = Invoke-RestMethod -Uri "$base/chat/submit" -Method POST -ContentType "application/json" -Body $submit_body2
    Write-Host "Status: OFF-TOPIC FLOW SUBMIT" -ForegroundColor Green
    Write-Host "Collected Slots:" -ForegroundColor Yellow
    foreach ($key in $resp.slots.Keys | Sort-Object) {
        Write-Host "  - $key : $($resp.slots[$key])" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "ERROR: $($_)" -ForegroundColor Red
}

# ----------------------
# Scenario 3: Corrections and overwrites
# ----------------------
$app_id3 = "test-correction-$(Get-Random -Minimum 1000 -Maximum 9999)"
$conv_id3 = "conv-$(Get-Random -Minimum 1000 -Maximum 9999)"
Write-Host "`nApp ID: $app_id3 (corrections)" -ForegroundColor Yellow

$messages3 = @(
    "Hello, I'm Anita Rao",
    "Email anita@oldmail.com",
    "Actually my email is anita.rao@example.com",
    "Phone 9876543210",
    "I need 300000 for education"
)

foreach ($m in $messages3) {
    $body = @{
        application_id = $app_id3
        conversation_id = $conv_id3
        user_message = $m
    } | ConvertTo-Json

    try {
        $resp = Invoke-RestMethod -Uri "$base/chat/converse" -Method POST -ContentType "application/json" -Body $body
        $slotsNow = ($resp.slots.Keys | Sort-Object) -join ', '
        Write-Host "User: $m" -ForegroundColor Magenta
        Write-Host "Assistant: $($resp.assistant_reply)" -ForegroundColor Cyan
        Write-Host "Slots now: $slotsNow" -ForegroundColor Yellow
        Write-Host "---" -ForegroundColor DarkGray
    }
    catch {
        Write-Host "ERROR: $($_)" -ForegroundColor Red
    }
}

$submit_body3 = @{
    application_id = $app_id3
    conversation_id = $conv_id3
} | ConvertTo-Json

try {
    $resp = Invoke-RestMethod -Uri "$base/chat/submit" -Method POST -ContentType "application/json" -Body $submit_body3
    Write-Host "Status: CORRECTION FLOW SUBMIT" -ForegroundColor Green
    Write-Host "Collected Slots:" -ForegroundColor Yellow
    foreach ($key in $resp.slots.Keys | Sort-Object) {
        Write-Host "  - $key : $($resp.slots[$key])" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "ERROR: $($_)" -ForegroundColor Red
}

Write-Host "`nDone." -ForegroundColor Green
