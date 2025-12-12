# MSN Loan Agent - Multi-Agent Merge Script (PowerShell/Windows)
# Usage: powershell -ExecutionPolicy Bypass -File merge-agents-powershell.ps1
# Edit the paths below before running

$ErrorActionPreference = "Stop"

# ============================================================================
# CONFIGURATION - EDIT THESE PATHS
# ============================================================================

$NITHIN_PROJECT_PATH = "C:\path\to\nithin-project"
$MEDHA_PROJECT_PATH = "C:\path\to\medha-project"
$REPO_URL = "https://github.com/medha0618nair/MSN-loan-agent.git"
$LOCAL_REPO_FOLDER = "$env:USERPROFILE\MSN-loan-agent"

# Get username for branch naming
$USERNAME = $env:USERNAME
$BRANCH_NAME = "add-agents-$USERNAME"

# ============================================================================
# STEP 1: Clone the remote repo
# ============================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Step 1: Cloning remote repository..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

if (Test-Path $LOCAL_REPO_FOLDER) {
    Write-Host "⚠️  Folder $LOCAL_REPO_FOLDER already exists. Skipping clone." -ForegroundColor Yellow
    Set-Location $LOCAL_REPO_FOLDER
} else {
    git clone $REPO_URL $LOCAL_REPO_FOLDER
    Set-Location $LOCAL_REPO_FOLDER
}

try {
    git pull origin main 2>$null
} catch {
    git pull origin master 2>$null
}

# ============================================================================
# STEP 2: Create agent subfolders
# ============================================================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Step 2: Creating agent subfolders..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$AGENT_FOLDERS = @(
    "intake-agent",
    "kyc-agent",
    "bank-agent",
    "credit-decision-agent",
    "face-agent",
    "payslip-agent",
    "orchestrator-agent"
)

foreach ($folder in $AGENT_FOLDERS) {
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
    Write-Host "✓ Created: $folder"
}

# ============================================================================
# STEP 3: Copy Nithin's agents
# ============================================================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Step 3: Copying Nithin's agent folders..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$NITHIN_AGENTS = @(
    "intake-agent",
    "kyc-agent",
    "bank-agent",
    "credit-decision-agent"
)

foreach ($agent in $NITHIN_AGENTS) {
    $SOURCE = "$NITHIN_PROJECT_PATH\$agent"
    $DEST = "$LOCAL_REPO_FOLDER\$agent"
    
    if (Test-Path $SOURCE) {
        robocopy $SOURCE $DEST /E /NFL /NDL /NJS /NC /NS /NP | Out-Null
        Write-Host "✓ Copied: $agent from Nithin's project"
    } else {
        Write-Host "⚠️  WARNING: $SOURCE not found. Skipping." -ForegroundColor Yellow
    }
}

# ============================================================================
# STEP 4: Copy Medha's agents
# ============================================================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Step 4: Copying Medha's agent folders..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$MEDHA_AGENTS = @(
    "face-agent",
    "payslip-agent"
)

foreach ($agent in $MEDHA_AGENTS) {
    $SOURCE = "$MEDHA_PROJECT_PATH\$agent"
    $DEST = "$LOCAL_REPO_FOLDER\$agent"
    
    if (Test-Path $SOURCE) {
        robocopy $SOURCE $DEST /E /NFL /NDL /NJS /NC /NS /NP | Out-Null
        Write-Host "✓ Copied: $agent from Medha's project"
    } else {
        Write-Host "⚠️  WARNING: $SOURCE not found. Skipping." -ForegroundColor Yellow
    }
}

# ============================================================================
# STEP 5: Create top-level README if missing
# ============================================================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Step 5: Creating top-level README (if missing)..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

if (-not (Test-Path "README.md")) {
    $README_CONTENT = @"
# MSN Loan Agent - Multi-Agent Lending System

A comprehensive multi-agent system for loan origination and income verification.

## Project Structure

``````
├── intake-agent/              # Loan application intake
├── kyc-agent/                 # Know Your Customer verification
├── bank-agent/                # Bank statement analysis
├── credit-decision-agent/     # Credit decision engine
├── face-agent/                # Face verification and liveness detection
├── payslip-agent/             # Income verification from payslips
├── orchestrator-agent/        # Multi-agent orchestrator
└── README.md
``````

## Agents

### Nithin's Agents
- **intake-agent**: Handles loan application submissions and initial data collection
- **kyc-agent**: Performs KYC verification and compliance checks
- **bank-agent**: Analyzes bank statements for financial health assessment
- **credit-decision-agent**: Makes credit decisions based on collected data

### Medha's Agents
- **face-agent**: Face verification using ArcFace ONNX embeddings with liveness detection
- **payslip-agent**: Income verification by extracting structured data from payslips (PDF/PNG/JPG)

## Getting Started

1. **Clone the repository**
   ``````bash
   git clone https://github.com/medha0618nair/MSN-loan-agent.git
   cd MSN-loan-agent
   ``````

2. **Install dependencies for each agent**
   ``````bash
   cd <agent-name>
   pip install -r requirements.txt
   ``````

3. **Run individual agents**
   Each agent has its own FastAPI server:
   ``````bash
   cd face-agent && python main.py  # Port 8000
   cd payslip-agent && python main.py  # Port 8001
   ``````

4. **Run orchestrator**
   ``````bash
   cd orchestrator-agent && python main.py  # Port 8010
   ``````

## API Endpoints

### Face Verification Agent (Port 8000)
- `POST /face/verify` - Verify face match between ID and selfie

### Payslip Income Verification Agent (Port 8001)
- `POST /payslip/verify` - Extract income information from payslip
- `POST /payslip/test` - Test with sample payslip data

## Development

- Each agent is independent and can be deployed separately
- Use FastAPI for HTTP endpoints
- Store results in respective databases
- Orchestrator coordinates multi-agent workflows

## Testing

Run tests for each agent:
``````bash
cd <agent-name>
pytest tests/
``````

## Contributing

1. Create a feature branch: `git checkout -b feature/agent-name`
2. Make changes and add tests
3. Submit a pull request with detailed description

## License

MIT

## Contact

- Nithin: intake, kyc, bank, credit-decision agents
- Medha: face-agent, payslip-agent
"@
    Set-Content -Path "README.md" -Value $README_CONTENT
    Write-Host "✓ Created top-level README.md"
} else {
    Write-Host "✓ README.md already exists"
}

# ============================================================================
# STEP 6: Create feature branch, commit, and push
# ============================================================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Step 6: Git workflow - branching, committing, and pushing..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# Create feature branch
git checkout -b $BRANCH_NAME 2>$null
if ($?) {
    Write-Host "✓ Created and switched to branch: $BRANCH_NAME"
} else {
    git checkout $BRANCH_NAME
    Write-Host "✓ Switched to existing branch: $BRANCH_NAME"
}

# Add all files
git add .
Write-Host "✓ Staged all files"

# Commit
$COMMIT_MESSAGE = "Add agents: intake, kyc, bank, credit-decision, face, payslip by $USERNAME"
git commit -m $COMMIT_MESSAGE 2>$null
if ($?) {
    Write-Host "✓ Created commit"
} else {
    Write-Host "ℹ️  No changes to commit"
}

# Attempt to push
Write-Host ""
Write-Host "Attempting to push to origin..."

$push_output = git push origin $BRANCH_NAME 2>&1
$push_success = $?

if ($push_success) {
    Write-Host "✓ Pushed to origin/$BRANCH_NAME" -ForegroundColor Green
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host "✅ SUCCESS! Pull Request URL:" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host ""
    Write-Host "https://github.com/medha0618nair/MSN-loan-agent/pull/new/$BRANCH_NAME"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠️  PUSH FAILED: You do not have push access to the main repository." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📌 FORK WORKFLOW REQUIRED:" -ForegroundColor Yellow
    Write-Host "   1. Fork the repo: https://github.com/medha0618nair/MSN-loan-agent" -ForegroundColor Yellow
    Write-Host "   2. Add your fork as a remote:" -ForegroundColor Yellow
    Write-Host "      git remote add fork https://github.com/$USERNAME/MSN-loan-agent.git" -ForegroundColor Yellow
    Write-Host "   3. Push to your fork:" -ForegroundColor Yellow
    Write-Host "      git push fork $BRANCH_NAME" -ForegroundColor Yellow
    Write-Host "   4. Open PR from your fork → main repo" -ForegroundColor Yellow
    Write-Host "      GitHub will show 'Create Pull Request' button after push" -ForegroundColor Yellow
}

# ============================================================================
# STEP 7: Print PR Checklist
# ============================================================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📋 PR CHECKLIST (Copy to PR description)" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "## Merge Checklist" -ForegroundColor Yellow
Write-Host ""
Write-Host "- [ ] All agent folders present: intake, kyc, bank, credit-decision, face, payslip"
Write-Host "- [ ] Each agent has README.md with setup and usage instructions"
Write-Host "- [ ] Each agent has requirements.txt or dependencies listed"
Write-Host "- [ ] Agent ports configured and documented (face:8000, payslip:8001, etc.)"
Write-Host "- [ ] Tests pass: ``pytest <agent-name>/tests/``"
Write-Host "- [ ] Top-level README.md updated with project structure"
Write-Host "- [ ] No merge conflicts with main branch"
Write-Host "- [ ] Code review approved"
Write-Host ""
Write-Host "## Agent Status" -ForegroundColor Yellow
Write-Host "- [ ] intake-agent: Ready"
Write-Host "- [ ] kyc-agent: Ready"
Write-Host "- [ ] bank-agent: Ready"
Write-Host "- [ ] credit-decision-agent: Ready"
Write-Host "- [ ] face-agent: Ready (Port 8000)"
Write-Host "- [ ] payslip-agent: Ready (Port 8001)"
Write-Host "- [ ] orchestrator-agent: Ready"
Write-Host ""

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✅ Merge script completed!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
