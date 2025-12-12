#!/bin/bash

# MSN Loan Agent - Multi-Agent Merge Script (Bash/Linux/macOS)
# Usage: bash merge-agents-bash.sh
# Edit the paths below before running

set -e  # Exit on error

# ============================================================================
# CONFIGURATION - EDIT THESE PATHS
# ============================================================================

NITHIN_PROJECT_PATH="/path/to/nithin-project"
MEDHA_PROJECT_PATH="/path/to/medha-project"
REPO_URL="https://github.com/medha0618nair/MSN-loan-agent.git"
LOCAL_REPO_FOLDER="$HOME/MSN-loan-agent"

# Get username for branch naming
USERNAME="${USER:-$(whoami)}"
BRANCH_NAME="add-agents-${USERNAME}"

# ============================================================================
# STEP 1: Clone the remote repo
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Cloning remote repository..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "$LOCAL_REPO_FOLDER" ]; then
    echo "⚠️  Folder $LOCAL_REPO_FOLDER already exists. Skipping clone."
    cd "$LOCAL_REPO_FOLDER"
else
    git clone "$REPO_URL" "$LOCAL_REPO_FOLDER"
    cd "$LOCAL_REPO_FOLDER"
fi

git pull origin main || git pull origin master

# ============================================================================
# STEP 2: Create agent subfolders
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Creating agent subfolders..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

AGENT_FOLDERS=(
    "intake-agent"
    "kyc-agent"
    "bank-agent"
    "credit-decision-agent"
    "face-agent"
    "payslip-agent"
    "orchestrator-agent"
)

for folder in "${AGENT_FOLDERS[@]}"; do
    mkdir -p "$folder"
    echo "✓ Created: $folder"
done

# ============================================================================
# STEP 3: Copy Nithin's agents
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Copying Nithin's agent folders..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

NITHIN_AGENTS=(
    "intake-agent"
    "kyc-agent"
    "bank-agent"
    "credit-decision-agent"
)

for agent in "${NITHIN_AGENTS[@]}"; do
    SOURCE="${NITHIN_PROJECT_PATH}/${agent}"
    DEST="${LOCAL_REPO_FOLDER}/${agent}"
    
    if [ -d "$SOURCE" ]; then
        cp -r "$SOURCE"/* "$DEST/" 2>/dev/null || true
        echo "✓ Copied: $agent from Nithin's project"
    else
        echo "⚠️  WARNING: $SOURCE not found. Skipping."
    fi
done

# ============================================================================
# STEP 4: Copy Medha's agents
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Copying Medha's agent folders..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

MEDHA_AGENTS=(
    "face-agent"
    "payslip-agent"
)

for agent in "${MEDHA_AGENTS[@]}"; do
    SOURCE="${MEDHA_PROJECT_PATH}/${agent}"
    DEST="${LOCAL_REPO_FOLDER}/${agent}"
    
    if [ -d "$SOURCE" ]; then
        cp -r "$SOURCE"/* "$DEST/" 2>/dev/null || true
        echo "✓ Copied: $agent from Medha's project"
    else
        echo "⚠️  WARNING: $SOURCE not found. Skipping."
    fi
done

# ============================================================================
# STEP 5: Create top-level README if missing
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Creating top-level README (if missing)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "README.md" ]; then
    cat > README.md << 'READMEEOF'
# MSN Loan Agent - Multi-Agent Lending System

A comprehensive multi-agent system for loan origination and income verification.

## Project Structure

```
├── intake-agent/              # Loan application intake
├── kyc-agent/                 # Know Your Customer verification
├── bank-agent/                # Bank statement analysis
├── credit-decision-agent/     # Credit decision engine
├── face-agent/                # Face verification and liveness detection
├── payslip-agent/             # Income verification from payslips
├── orchestrator-agent/        # Multi-agent orchestrator
└── README.md
```

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
   ```bash
   git clone https://github.com/medha0618nair/MSN-loan-agent.git
   cd MSN-loan-agent
   ```

2. **Install dependencies for each agent**
   ```bash
   cd <agent-name>
   pip install -r requirements.txt
   ```

3. **Run individual agents**
   Each agent has its own FastAPI server:
   ```bash
   cd face-agent && python3 main.py  # Port 8000
   cd payslip-agent && python3 main.py  # Port 8001
   ```

4. **Run orchestrator**
   ```bash
   cd orchestrator-agent && python3 main.py  # Port 8010
   ```

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
```bash
cd <agent-name>
pytest tests/
```

## Contributing

1. Create a feature branch: `git checkout -b feature/agent-name`
2. Make changes and add tests
3. Submit a pull request with detailed description

## License

MIT

## Contact

- Nithin: intake, kyc, bank, credit-decision agents
- Medha: face-agent, payslip-agent
READMEEOF
    echo "✓ Created top-level README.md"
else
    echo "✓ README.md already exists"
fi

# ============================================================================
# STEP 6: Create feature branch, commit, and push
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 6: Git workflow - branching, committing, and pushing..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create feature branch
git checkout -b "$BRANCH_NAME" 2>/dev/null || git checkout "$BRANCH_NAME"
echo "✓ Switched to branch: $BRANCH_NAME"

# Add all files
git add .
echo "✓ Staged all files"

# Commit
COMMIT_MESSAGE="Add agents: intake, kyc, bank, credit-decision, face, payslip by ${USERNAME}"
git commit -m "$COMMIT_MESSAGE" 2>/dev/null || echo "ℹ️  No changes to commit"

# Attempt to push
echo ""
echo "Attempting to push to origin..."

if git push origin "$BRANCH_NAME" 2>&1 | grep -q "Permission denied\|no access"; then
    echo ""
    echo "⚠️  PUSH FAILED: You do not have push access to the main repository."
    echo ""
    echo "📌 FORK WORKFLOW REQUIRED:"
    echo "   1. Fork the repo: https://github.com/medha0618nair/MSN-loan-agent"
    echo "   2. Add your fork as a remote:"
    echo "      git remote add fork https://github.com/${USERNAME}/MSN-loan-agent.git"
    echo "   3. Push to your fork:"
    echo "      git push fork ${BRANCH_NAME}"
    echo "   4. Open PR from your fork → main repo"
    echo "      GitHub will show 'Create Pull Request' button after push"
else
    echo "✓ Pushed to origin/${BRANCH_NAME}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ SUCCESS! Pull Request URL:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "https://github.com/medha0618nair/MSN-loan-agent/pull/new/${BRANCH_NAME}"
    echo ""
fi

# ============================================================================
# STEP 7: Print PR Checklist
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 PR CHECKLIST (Copy to PR description)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "## Merge Checklist"
echo ""
echo "- [ ] All agent folders present: intake, kyc, bank, credit-decision, face, payslip"
echo "- [ ] Each agent has README.md with setup and usage instructions"
echo "- [ ] Each agent has requirements.txt or dependencies listed"
echo "- [ ] Agent ports configured and documented (face:8000, payslip:8001, etc.)"
echo "- [ ] Tests pass: \`pytest <agent-name>/tests/\`"
echo "- [ ] Top-level README.md updated with project structure"
echo "- [ ] No merge conflicts with main branch"
echo "- [ ] Code review approved"
echo ""
echo "## Agent Status"
echo "- [ ] intake-agent: Ready"
echo "- [ ] kyc-agent: Ready"
echo "- [ ] bank-agent: Ready"
echo "- [ ] credit-decision-agent: Ready"
echo "- [ ] face-agent: Ready (Port 8000)"
echo "- [ ] payslip-agent: Ready (Port 8001)"
echo "- [ ] orchestrator-agent: Ready"
echo ""

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Merge script completed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
