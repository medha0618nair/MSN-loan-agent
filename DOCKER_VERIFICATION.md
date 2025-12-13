# Docker Verification Checklist

## Pre-Deployment Checklist ✓

### System Requirements
- [ ] Docker Desktop installed and running
- [ ] Docker version 20.10+: `docker --version`
- [ ] Docker Compose version 2.0+: `docker-compose --version`
- [ ] 8GB+ RAM available
- [ ] 10GB+ disk space available

### Project Setup
- [ ] Project directory: `/Users/apple/Desktop/codered final/MSN-loan-agent`
- [ ] All 7 Dockerfiles present:
  - [ ] `agents/intake_agent/Dockerfile`
  - [ ] `agents/kyc_agent/Dockerfile`
  - [ ] `agents/face-agent/Dockerfile`
  - [ ] `agents/payslip-agent/Dockerfile`
  - [ ] `agents/bank-agent/Dockerfile`
  - [ ] `agents/credit-agent/Dockerfile`
  - [ ] `orchestrator_agent/Dockerfile`
- [ ] docker-compose.yml exists and configured
- [ ] .env.docker exists with service URLs
- [ ] orchestrator_agent/config_v2_docker.py exists

### Data Files
- [ ] Bank statement CSV exists: `bank-statement/bank_transactions_ACC1001.csv`
- [ ] PAN image exists: `agents/kyc_agent/uploads/nithinofPAN.jpeg`
- [ ] Tesseract OCR installed: `tesseract --version`
- [ ] pytesseract installed: Check with `pip list | grep pytesseract`

## Deployment Checklist ✓

### Pre-Start Verification

```bash
# 1. Check Docker daemon is running
docker info

# 2. Check if ports are available
lsof -i :8001,8002,8003,8004,8005,8006,9000 || echo "✓ All ports available"

# 3. Verify all agent directories exist
ls -d agents/*/

# 4. Check requirements.txt in each agent
find agents/*/requirements.txt orchestrator_agent/requirements.txt

# 5. Verify docker-compose.yml syntax
docker-compose config > /dev/null && echo "✓ docker-compose.yml valid"
```

### Start Services

```bash
# 1. Navigate to project
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"

# 2. Build images
docker-compose build

# 3. Start services
docker-compose up -d

# 4. Wait for services to start (60 seconds)
sleep 60

# 5. Check all services are healthy
docker-compose ps
```

### Post-Start Verification

```bash
# 1. Check all services are running
docker-compose ps | grep -i healthy

# 2. Test individual health endpoints
curl http://localhost:8001/health  # Intake
curl http://localhost:8002/health  # KYC
curl http://localhost:8003/health  # Face
curl http://localhost:8004/health  # Payslip
curl http://localhost:8005/health  # Bank
curl http://localhost:8006/health  # Credit
curl http://localhost:9000/health  # Orchestrator

# 3. Check inter-service communication
docker-compose exec orchestrator curl http://intake:8000/health

# 4. View logs
docker-compose logs --tail=50
```

## Service Health Status

### Expected Status After Startup

| Service | Port | Status | Command |
|---------|------|--------|---------|
| Intake | 8001 | Healthy | `curl http://localhost:8001/health` |
| KYC | 8002 | Healthy | `curl http://localhost:8002/health` |
| Face | 8003 | Healthy | `curl http://localhost:8003/health` |
| Payslip | 8004 | Healthy | `curl http://localhost:8004/health` |
| Bank | 8005 | Healthy | `curl http://localhost:8005/health` |
| Credit | 8006 | Healthy | `curl http://localhost:8006/health` |
| Orchestrator | 9000 | Healthy | `curl http://localhost:9000/health` |

### Status Meanings

- **Up (healthy)** ✓ - Service running and responsive
- **Up (unhealthy)** ⚠️ - Service running but not responding to health checks
- **Restarting** 🔄 - Service crashed and Docker is restarting
- **Exited** ❌ - Service stopped (check logs)

## Troubleshooting Command Reference

### Check Service Status
```bash
# Show all containers
docker-compose ps

# Show only problematic containers
docker-compose ps | grep -v healthy

# Get container IDs
docker ps -f label=com.docker.compose.project=msnloanagent
```

### View Logs
```bash
# All services, last 50 lines
docker-compose logs --tail=50

# Specific service
docker-compose logs -f intake

# Follow new logs in real-time
docker-compose logs -f

# Filter by time
docker-compose logs --since 2025-12-13T12:00:00
```

### Debug Inside Container
```bash
# Open shell in container
docker-compose exec intake bash

# Run Python code
docker-compose exec intake python -c "import sys; print(sys.version)"

# Check environment variables
docker-compose exec intake env | grep -E "INTAKE|KYC|BANK"

# List files
docker-compose exec intake ls -la /app/

# Check installed packages
docker-compose exec intake pip list
```

### Network Debugging
```bash
# Check network connectivity from container
docker-compose exec orchestrator curl http://intake:8000/health

# Check DNS resolution
docker-compose exec orchestrator nslookup intake

# List all networks
docker network ls

# Inspect loan-agent-network
docker network inspect loan-agent-network

# Check container IP addresses
docker-compose exec intake hostname -I
```

### Performance Debugging
```bash
# Monitor resource usage (real-time)
docker stats

# Check memory usage per service
docker stats --no-stream

# List all volumes
docker volume ls

# Check volume size
docker system df

# Inspect logs for errors
docker-compose logs | grep -i error
```

### Clean Start (Nuclear Option)
```bash
# Stop all services
docker-compose down

# Remove all containers
docker-compose rm -f

# Rebuild images
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

## Common Issues Reference

### Issue: "Cannot connect to Docker daemon"
**Cause**: Docker Desktop not running
**Fix**: Open Docker Desktop application

### Issue: "Port 8001 already in use"
**Cause**: Another service using the port
**Fix**: 
```bash
lsof -i :8001
kill -9 <PID>
```

### Issue: "Service unhealthy"
**Cause**: Service crash or health check failure
**Fix**:
```bash
docker-compose logs intake
docker-compose restart intake
```

### Issue: "Cannot resolve service name"
**Cause**: Network issue or service not running
**Fix**:
```bash
docker-compose ps  # Check all services up
docker network inspect loan-agent-network  # Check network
```

### Issue: "Out of memory"
**Cause**: Docker resource limits too low
**Fix**: Increase Docker Desktop memory limit or reduce services

### Issue: "File not found in container"
**Cause**: Volume mount path incorrect
**Fix**:
```bash
docker-compose exec bank ls -la /app/bank-statement/
# Check if files exist in host
ls -la bank-statement/
```

## Performance Tuning

### Check Current Resource Usage
```bash
# Real-time resource monitoring
docker stats

# Memory limit per service
docker inspect <container_id> | grep -A 10 "Memory"

# CPU shares
docker inspect <container_id> | grep -A 5 "CpuShares"
```

### Optimize for Your System

**Low Memory (4GB):**
- Start only essential services: `docker-compose up intake orchestrator credit`
- Monitor memory: `docker stats`

**High Memory (16GB+):**
- All services can run: `docker-compose up -d`
- Add monitoring service: Prometheus + Grafana

## Rollback and Recovery

### Rollback to Previous Version
```bash
# List available images
docker images | grep agent

# Stop current services
docker-compose down

# Modify docker-compose.yml to use older image tag
# Then restart
docker-compose up -d
```

### Recover Data After Crash
```bash
# Check volumes
docker volume ls

# Mount volume to inspect data
docker volume inspect <volume_name>

# Backup volume data
docker run --rm -v <volume_name>:/data -v $(pwd):/backup alpine tar czf /backup/volume-backup.tar.gz /data
```

### Complete System Restore
```bash
# Backup current state
docker-compose down -v

# Restore from backup
tar xzf system-backup.tar.gz
docker-compose up -d
```

## Monitoring in Production

### Enable Advanced Logging
```yaml
# In docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Health Check Frequency
Current health check every 10s with 3 failures = 30s timeout

### Prometheus Metrics (Optional)
```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

## Validation Tests

### Quick System Test
```bash
# 1. Start system
docker-compose up -d

# 2. Wait for startup
sleep 60

# 3. Run validation
docker-compose ps | grep healthy | wc -l
# Should show 7 healthy services

# 4. Test orchestrator
curl -X POST http://localhost:9000/start \
  -H "Content-Type: application/json" \
  -d '{}'
```

### End-to-End Test
```bash
# 1. Start conversation at intake
CONVERSATION_ID=$(curl -s -X POST http://localhost:8001/start \
  -H "Content-Type: application/json" -d '{}' | jq -r '.conversation_id')

echo "Started conversation: $CONVERSATION_ID"

# 2. Check conversation was stored
docker-compose exec intake \
  cat /app/data/conversations/$CONVERSATION_ID/conversation.json

# 3. View orchestrator processing
docker-compose logs -f orchestrator
```

---

**Quick Start Commands:**

```bash
# Start everything
cd "/Users/apple/Desktop/codered final/MSN-loan-agent" && docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Stop and clean up
docker-compose down -v
```

**Success Indicators:**
- ✓ All 7 containers showing "Up (healthy)"
- ✓ All health endpoints responding
- ✓ Orchestrator can reach all services
- ✓ Data being written to volumes
