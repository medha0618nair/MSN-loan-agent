═══════════════════════════════════════════════════════════════════════════════
                            PR CHECKLIST
                  Multi-Agent Merge for MSN Loan System
═══════════════════════════════════════════════════════════════════════════════

Copy and paste the section below into your GitHub Pull Request description.

───────────────────────────────────────────────────────────────────────────────

## 📋 Merge Checklist

### Agent Folders
- [ ] All 7 agent folders present in repo root:
  - [ ] intake-agent
  - [ ] kyc-agent
  - [ ] bank-agent
  - [ ] credit-decision-agent
  - [ ] face-agent
  - [ ] payslip-agent
  - [ ] orchestrator-agent

### Documentation
- [ ] Each agent has README.md with:
  - [ ] Setup instructions
  - [ ] Dependencies listed
  - [ ] Usage examples
  - [ ] API endpoints documented
- [ ] Top-level README.md includes:
  - [ ] Project structure overview
  - [ ] List of all agents
  - [ ] Quick start guide
  - [ ] Agent owner information (Nithin/Medha)

### Dependencies & Ports
- [ ] Each agent has requirements.txt or equivalent
- [ ] Agent ports confirmed and documented:
  - [ ] face-agent: Port 8000
  - [ ] payslip-agent: Port 8001
  - [ ] intake-agent: Port specified in README
  - [ ] kyc-agent: Port specified in README
  - [ ] bank-agent: Port specified in README
  - [ ] credit-decision-agent: Port specified in README
  - [ ] orchestrator-agent: Port 8010 (or specified)
- [ ] No port conflicts between agents

### Testing
- [ ] All tests pass:
  ```bash
  cd intake-agent && pytest tests/
  cd kyc-agent && pytest tests/
  cd bank-agent && pytest tests/
  cd credit-decision-agent && pytest tests/
  cd face-agent && pytest tests/
  cd payslip-agent && pytest tests/
  ```
- [ ] Each agent starts without errors
- [ ] Health check endpoints working

### Code Quality
- [ ] No merge conflicts with main branch
- [ ] Git history clean (squash commits if needed)
- [ ] No sensitive data in commits
- [ ] Dependencies versions pinned where appropriate

### Git Workflow
- [ ] Branch created from latest main
- [ ] Commit message clear and descriptive
- [ ] Pull request title follows format: "Add agents: intake, kyc, bank, etc."
- [ ] PR description includes which agents are added

### Integration
- [ ] Orchestrator can detect all agents
- [ ] Agent communication paths verified
- [ ] No hardcoded localhost paths (use config/env vars)
- [ ] API contract between agents documented

### Code Review
- [ ] At least one owner approved (Nithin/Medha)
- [ ] No outstanding review comments
- [ ] Ready for merge

───────────────────────────────────────────────────────────────────────────────

## 🚀 Merge Procedure

**For Repository Maintainer (after approval):**

1. Ensure all checkboxes are marked
2. Click "Merge pull request"
3. Choose "Squash and merge" or "Create a merge commit"
4. Delete the feature branch after merge
5. Notify contributors that merge is complete

**For Contributors without Push Access:**

If you see "Permission denied" when pushing:

1. **Fork the main repository:**
   - Go to https://github.com/medha0618nair/MSN-loan-agent
   - Click "Fork" (top right)

2. **Add your fork as a remote:**
   ```bash
   git remote add fork https://github.com/YOUR-USERNAME/MSN-loan-agent.git
   ```

3. **Push to your fork instead:**
   ```bash
   git push fork add-agents-YOUR-USERNAME
   ```

4. **Create Pull Request:**
   - GitHub will show "Compare & pull request" button on your fork
   - Or go to https://github.com/medha0618nair/MSN-loan-agent/pulls
   - Click "New Pull Request"
   - Select: main repo main ← your fork add-agents-YOUR-USERNAME

5. **Submit PR with checklist above**

───────────────────────────────────────────────────────────────────────────────

## 📞 Quick Reference

**Branch Naming Convention:**
```
add-agents-{username}
```

**Commit Message Format:**
```
Add agents: intake, kyc, bank, credit-decision, face, payslip by {username}
```

**PR Title Format:**
```
Add agents: intake, kyc, bank, credit-decision, face, payslip
```

**Required Files per Agent:**
```
{agent-name}/
├── main.py              (FastAPI entry point)
├── requirements.txt     (Python dependencies)
├── README.md           (Agent documentation)
└── tests/             (Test suite)
    └── test_*.py
```

───────────────────────────────────────────────────────────────────────────────

## ⚠️ Common Issues & Solutions

**Issue: "fatal: Permission denied (publickey)"**
- Solution: Use fork workflow (see above)

**Issue: "CONFLICT: Both branches modified README.md"**
- Solution: Pull latest, resolve conflicts, then push again
  ```bash
  git pull origin main
  # Fix conflicts in README.md
  git add README.md
  git commit -m "Resolve merge conflicts"
  git push origin add-agents-{username}
  ```

**Issue: "Port 8000 already in use"**
- Solution: Update port numbers in agent README or main.py
- Document new ports in top-level README

**Issue: Missing dependencies in requirements.txt**
- Solution: Run `pip freeze > requirements.txt` in each agent venv
- Remove dev-only packages (pytest, black, etc.)

───────────────────────────────────────────────────────────────────────────────

## 📚 Additional Resources

- **Git Workflow Guide:** https://git-scm.com/book/en/v2
- **GitHub PR Best Practices:** https://docs.github.com/en/pull-requests
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Pytest Guide:** https://docs.pytest.org/

═══════════════════════════════════════════════════════════════════════════════
