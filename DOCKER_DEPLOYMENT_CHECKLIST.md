# Docker Deployment Checklist

Use this checklist to ensure your Docker deployment is complete and ready for production use.

## ✅ Pre-Deployment Phase

### System Requirements
- [ ] Docker Desktop installed (version 4.0+)
- [ ] Docker Compose installed (version 2.0+)
- [ ] 8+ GB RAM available
- [ ] 10+ GB free disk space
- [ ] macOS 11+, Windows 10+, or recent Linux distribution

**Verify:**
```bash
docker --version      # Should show 20.10+
docker-compose --version  # Should show 2.0+
docker info           # Should show running daemon
```

### Project Files
- [ ] All 7 Dockerfiles present and valid
- [ ] docker-compose.yml exists (480+ lines)
- [ ] .env.docker file created
- [ ] orchestrator_agent/config_v2_docker.py exists
- [ ] All requirements.txt files present in agents
- [ ] Bank statement CSV file in place
- [ ] All Python packages listed in requirements

**Verify:**
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
find . -name "Dockerfile" | wc -l  # Should be 7
ls -la docker-compose.yml          # Should exist
ls -la .env.docker                 # Should exist
```

### Data Files
- [ ] Bank statement: `bank-statement/bank_transactions_ACC1001.csv`
- [ ] PAN image: `agents/kyc_agent/uploads/nithinofPAN.jpeg`
- [ ] Tesseract OCR installed on host: `tesseract --version`
- [ ] pytesseract package installed: `pip list | grep pytesseract`

**Verify:**
```bash
tesseract --version   # Should show Tesseract 5.5.1+
ls -la bank-statement/
ls -la agents/kyc_agent/uploads/
```

## 🏗️ Build Phase

### Image Building
- [ ] No port conflicts: `lsof -i :8001-8006,9000`
- [ ] Docker daemon running: `docker info`
- [ ] Sufficient disk space: `docker system df`

**Verify:**
```bash
# Should show no processes on these ports
lsof -i :8001 || echo "Port 8001 available"

# Should show available space
docker system df
```

### Build Images
```bash
# Clean previous builds (optional)
docker-compose down -v
docker system prune -a -f

# Build all images
docker-compose build --verbose
```

- [ ] All 7 images built successfully
- [ ] No build errors in output
- [ ] Total image size < 15GB

**Verify:**
```bash
docker images | grep agent | wc -l  # Should show 7
docker-compose config -q             # Should be valid
```

## 🚀 Deployment Phase

### Start Services
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
docker-compose up -d
```

- [ ] All services start without errors
- [ ] No permission denied errors
- [ ] No port already in use errors

**Verify:**
```bash
docker-compose ps | grep -i up  # All should show "Up"
```

### Wait for Health
```bash
sleep 60
docker-compose ps
```

- [ ] All 7 services showing "Up (healthy)" status
- [ ] No services in "restarting" state
- [ ] No services showing "(unhealthy)"

**Expected Output:**
```
STATUS: Up 45 seconds (healthy)
```

## 🏥 Health Verification Phase

### Individual Service Health
```bash
# Test each service
curl http://localhost:8001/health    # Intake
curl http://localhost:8002/health    # KYC
curl http://localhost:8003/health    # Face
curl http://localhost:8004/health    # Payslip
curl http://localhost:8005/health    # Bank
curl http://localhost:8006/health    # Credit
curl http://localhost:9000/health    # Orchestrator
```

- [ ] All 7 endpoints return HTTP 200
- [ ] All responses contain `"status": "ok"`
- [ ] Response time < 100ms for each

**Verify:**
```bash
for port in 8001 8002 8003 8004 8005 8006 9000; do
  curl -s http://localhost:$port/health | jq '.status'
done
# Should show: "ok" 7 times
```

### Network Connectivity
```bash
# From orchestrator to other services
docker-compose exec orchestrator curl http://intake:8000/health
docker-compose exec orchestrator curl http://kyc:8000/health
docker-compose exec orchestrator curl http://bank:8000/health
docker-compose exec orchestrator curl http://credit:8000/health
```

- [ ] All internal URLs accessible
- [ ] All return status 200
- [ ] DNS resolution working inside network

**Verify:**
```bash
docker-compose exec orchestrator nslookup intake
# Should resolve to 172.x.x.x
```

## 📊 Data Verification Phase

### Volume Mounting
```bash
# Check data directories
docker-compose exec intake ls -la /app/data/
docker-compose exec kyc ls -la /app/audit/
docker-compose exec bank ls -la /app/bank-statement/
```

- [ ] All directories exist and are accessible
- [ ] Data files are readable
- [ ] Write permissions verified

**Verify:**
```bash
docker-compose exec intake touch /app/data/test.txt
docker-compose exec intake rm /app/data/test.txt
# Should succeed
```

### Database Connectivity
- [ ] Intake can write to /app/data/conversations/
- [ ] KYC can read/write /app/audit/
- [ ] Bank can read CSV files
- [ ] All timestamps recorded correctly

**Verify:**
```bash
docker-compose exec intake cat /app/data/conversations/*/conversation.json | jq '.timestamp'
# Should show ISO timestamps
```

## 🧪 Integration Testing Phase

### API Integration Tests
```bash
# Test 1: Start conversation
CONV=$(curl -s -X POST http://localhost:8001/start \
  -H "Content-Type: application/json" -d '{}' | jq -r '.conversation_id')
echo "✓ Intake: $CONV"

# Test 2: Parse KYC
curl -s -X POST http://localhost:8002/kyc/parse \
  -H "Content-Type: application/json" \
  -d '{"application_id":"APP-001","evidence_id":"KYC-001","file_uri":"/app/uploads/nithinofPAN.jpeg"}' \
  | jq '.extracted_data.pan_number'
# Should show: "DIJPN7537R"

# Test 3: Parse Bank Statement
curl -s -X POST http://localhost:8005/bank/parse \
  -H "Content-Type: application/json" \
  -d '{"application_id":"APP-001","evidence_id":"BANK-001","file_uri":"/app/bank-statement/bank_transactions_ACC1001.csv"}' \
  | jq '.analysis.average_salary'
# Should show: 41851.72
```

- [ ] Intake conversation starts successfully
- [ ] KYC extracts correct PAN (DIJPN7537R)
- [ ] Bank analysis detects correct salary (₹41,851)
- [ ] All services respond with expected data

### End-to-End Flow Test
```bash
# Test orchestrator chain
curl -s -X POST http://localhost:9000/start \
  -H "Content-Type: application/json" \
  -d '{"applicant_name":"Test User"}' | jq '.orchestration_id'
```

- [ ] Orchestrator starts workflow
- [ ] Returns valid orchestration_id
- [ ] Can retrieve status

## 📈 Performance Validation Phase

### Response Time Benchmarks
```bash
# Measure response times
time curl http://localhost:8001/health
time curl http://localhost:8002/health
time curl http://localhost:8005/bank/parse -d '{...}'
```

- [ ] Health checks: < 50ms
- [ ] Document parsing: 1-3 seconds
- [ ] Credit scoring: < 1 second

### Resource Usage
```bash
docker stats --no-stream
```

- [ ] No service using > 1GB memory
- [ ] No service using > 50% CPU (idle)
- [ ] Network I/O < 10MB/s

**Expected:**
```
MEMORY USAGE: 200-400MB per service
```

## 📝 Logging and Monitoring Phase

### Log Verification
```bash
# Check logs have no errors
docker-compose logs --tail=100 | grep -i error | wc -l
# Should be 0 or minimal

# View info logs
docker-compose logs orchestrator | head -20
```

- [ ] No ERROR level logs
- [ ] No CRITICAL logs
- [ ] INFO logs show normal operation
- [ ] Timestamps are correct

### Health Check Logs
```bash
docker-compose logs | grep "health"
```

- [ ] Health checks running every 10 seconds
- [ ] All checks passing
- [ ] No timeout errors

## 🔐 Security Phase

### Network Isolation
```bash
# Verify bridge network
docker network inspect loan-agent-network | jq '.Containers'
```

- [ ] All 7 services on same network
- [ ] Services cannot access external networks by default
- [ ] Only exposed ports accessible from host

### Data Security
- [ ] No credentials in logs
- [ ] No API keys in environment
- [ ] Data stored only in volumes
- [ ] No data exposed in Docker logs

**Verify:**
```bash
docker-compose logs | grep -i "password\|token\|key" | wc -l
# Should be 0
```

## 📊 Documentation Phase

### Required Documentation
- [ ] `DOCKER_README.md` exists and is complete
- [ ] `DOCKER_SETUP_GUIDE.md` with detailed instructions
- [ ] `DOCKER_VERIFICATION.md` with troubleshooting
- [ ] `DOCKER_API_TESTS.md` with test examples
- [ ] `DOCKER_QUICK_REFERENCE.md` with command reference

### Configuration Documentation
- [ ] .env.docker documented
- [ ] All environment variables documented
- [ ] Volume mappings documented
- [ ] Port mappings documented

## 🚢 Production Readiness Phase

### Deployment Readiness
- [ ] All services passing health checks
- [ ] All data persisted correctly
- [ ] All APIs responding correctly
- [ ] Performance within acceptable limits
- [ ] Logging and monitoring enabled
- [ ] Documentation complete
- [ ] Team trained on deployment

### Scaling Readiness
- [ ] Can increase resource limits
- [ ] Can add service replicas
- [ ] Can add new services
- [ ] Can backup and restore data

**Verify:**
```bash
docker-compose up -d --scale bank=2  # Test scaling
docker-compose ps | grep bank        # Should see 2 instances
docker-compose down                  # Stop scaled version
docker-compose up -d                 # Return to normal
```

## 🆘 Rollback Phase

### Backup Current State
```bash
# Save current configuration
docker-compose config > docker-compose-backup.yml
cp .env.docker .env.docker.backup
docker volume inspect intake-data  # Note volume details

# Backup data
docker run --rm -v intake-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/intake-data-backup.tar.gz /data
```

- [ ] Current docker-compose.yml backed up
- [ ] Environment file backed up
- [ ] Data volumes backed up
- [ ] Backup verified and tested

### Rollback Procedure
```bash
# Restore backup
docker-compose down -v
docker-compose up -d --build
# OR
cp docker-compose-backup.yml docker-compose.yml
docker-compose up -d
```

- [ ] Can stop all services cleanly
- [ ] Can restore from backups
- [ ] Can rollback changes quickly
- [ ] Recovery time < 5 minutes

## 📋 Sign-Off Checklist

**Ready for Production:**
- [ ] All 7 services healthy and running
- [ ] All health checks passing
- [ ] All APIs tested and working
- [ ] All data persisting correctly
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Documentation complete
- [ ] Team trained
- [ ] Backup and recovery tested

**Ready for Testing:**
- [ ] All services accessible
- [ ] Can send test requests
- [ ] Can monitor in real-time
- [ ] Can view logs

**Ready for Shutdown:**
- [ ] Data backed up
- [ ] Logs archived
- [ ] Configuration saved
- [ ] Services stop cleanly

## 🎯 Quick Deployment Commands

```bash
# Full deployment from scratch
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
docker-compose down -v              # Clean slate
docker-compose build --no-cache     # Fresh build
docker-compose up -d                # Start all
sleep 60                            # Wait for startup
docker-compose ps                   # Verify status

# Verification
for port in 8001 8002 8003 8004 8005 8006 9000; do
  curl -s http://localhost:$port/health | jq '.status'
done

# All should show: "ok"
```

## ❌ Issues During Deployment

If any checks fail:

1. **Check logs**: `docker-compose logs <service>`
2. **Inspect service**: `docker-compose exec <service> bash`
3. **Review checklist**: Find the failed step
4. **Refer to**: `DOCKER_VERIFICATION.md` for solutions
5. **Escalate**: Contact system administrator if needed

---

**Deployment Date**: _______________

**Deployed By**: _______________

**Notes**: _____________________

---

**Version**: 1.0  
**Last Updated**: December 13, 2025  
**System**: Multi-Agent Loan Processing Platform
