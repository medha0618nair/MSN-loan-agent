# Test Intake Agent Endpoints
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🧪 INTAKE AGENT TEST SUITE" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8001"

# Test 1: Health Check
Write-Host "1️⃣  Health Check" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
Write-Host "   Status: $($response.status)" -ForegroundColor Green
Write-Host "   Service: $($response.service)" -ForegroundColor Green
Write-Host ""

# Test 2: Start Conversation
Write-Host "2️⃣  Start Loan Application Conversation" -ForegroundColor Yellow
$converseBody = @{
    application_id = "app-demo-001"
    conversation_id = "conv-demo-001"
    user_message = "Hi, I want to apply for a personal loan of 5 lakhs"
    context = @{}
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$baseUrl/chat/converse" -Method POST -Body $converseBody -ContentType "application/json"
Write-Host "   Assistant: $($response.assistant_reply)" -ForegroundColor Cyan
Write-Host "   Slots collected: $($response.slots | ConvertTo-Json -Compress)" -ForegroundColor Green
Write-Host ""

# Test 3: Provide More Information
Write-Host "3️⃣  User Provides Name and Contact" -ForegroundColor Yellow
$converseBody2 = @{
    application_id = "app-demo-001"
    conversation_id = "conv-demo-001"
    user_message = "My name is John Doe, email is john.doe@example.com and phone is 9876543210"
    context = @{}
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "$baseUrl/chat/converse" -Method POST -Body $converseBody2 -ContentType "application/json"
Write-Host "   Assistant: $($response2.assistant_reply)" -ForegroundColor Cyan
Write-Host "   Slots collected: $($response2.slots | ConvertTo-Json -Compress)" -ForegroundColor Green
Write-Host ""

# Test 4: Update Specific Slot
Write-Host "4️⃣  Explicitly Set Loan Purpose" -ForegroundColor Yellow
$slotBody = @{
    application_id = "app-demo-001"
    conversation_id = "conv-demo-001"
    slot_name = "loan_purpose"
    slot_value = "Home renovation"
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Uri "$baseUrl/chat/slot" -Method POST -Body $slotBody -ContentType "application/json"
Write-Host "   Updated: $($response3.assistant_reply)" -ForegroundColor Green
Write-Host "   All slots: $($response3.slots | ConvertTo-Json)" -ForegroundColor Cyan
Write-Host ""

# Test 5: Submit Application
Write-Host "5️⃣  Submit Application" -ForegroundColor Yellow
$submitBody = @{
    application_id = "app-demo-001"
    conversation_id = "conv-demo-001"
} | ConvertTo-Json

$response4 = Invoke-RestMethod -Uri "$baseUrl/chat/submit" -Method POST -Body $submitBody -ContentType "application/json"
Write-Host "   Result: $($response4.assistant_reply)" -ForegroundColor Green
Write-Host "   Actions: $($response4.actions | ConvertTo-Json)" -ForegroundColor Cyan
Write-Host ""

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "✅ ALL TESTS COMPLETED!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "View full API documentation at: http://localhost:8001/docs" -ForegroundColor Yellow
Write-Host ""
