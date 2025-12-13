# Docker Setup Guide - Multi-Agent Loan System

## Overview

This guide will help you run the entire multi-agent loan processing system using Docker and Docker Compose.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Docker Network                              │
│              (loan-agent-network - bridge network)                  │
└─────────────────────────────────────────────────────────────────────┘
     │
     ├── Intake Agent (intake:8000)          → External: localhost:8001
     ├── KYC Agent (kyc:8000)                → External: localhost:8002
     ├── Face Agent (face:8000)              → External: localhost:8003
     ├── Payslip Agent (payslip:8000)        → External: localhost:8004
     ├── Bank Agent (bank:8000)              → External: localhost:8005
     ├── Credit Agent (credit:8000)          → External: localhost:8006
     └── Orchestrator (orchestrator:8000)    → External: localhost:9000
```

## Prerequisites

- Docker Desktop (or Docker + Docker Compose)
- 8+ GB RAM available
- ~10 GB disk space for images and data

## Files Generated

### 1. Updated Dockerfiles
Each agent has been updated with:
- Python 3.13 slim base image
- Proper port exposure (8000 internal)
- Health checks
- Volume mounts for data persistence

Files updated:
- `agents/intake_agent/Dockerfile`
- `agents/kyc_agent/Dockerfile`
- `agents/face-agent/Dockerfile`
- `agents/payslip-agent/Dockerfile`
- `agents/bank-agent/Dockerfile`
- `agents/credit-agent/Dockerfile`
- `orchestrator_agent/Dockerfile` (new)

### 2. Docker Compose Configuration
- `docker-compose.yml` - Main orchestration file

Features:
- All 7 services defined
- Bridge network for inter-service communication
- Health checks for each service
- Orchestrator depends_on all agents
- Volume mounts for data persistence
- Environment variables for service discovery

### 3. Configuration Files
- `.env.docker` - Environment variables for Docker
- `orchestrator_agent/config_v2_docker.py` - Docker-aware orchestrator config

## Quick Start

### Option 1: Full Build and Start (Recommended)

```bash
# Navigate to project root
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"

# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### Option 2: Build First, Then Start

```bash
# Build images only
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### Option 3: Start with Specific Services

```bash
# Start only intake and orchestrator (good for testing)
docker-compose up -d intake orchestrator

# Start all backend services (without orchestrator)
docker-compose up -d intake kyc face payslip bank credit

# Add orchestrator after others are healthy
docker-compose up -d orchestrator
```

## Service Communication

### Internal URLs (within Docker)
Services communicate using service names:

```
Intake:       http://intake:8000
KYC:          http://kyc:8000
Face:         http://face:8000
Payslip:      http://payslip:8000
Bank:         http://bank:8000
Credit:       http://credit:8000
Orchestrator: http://orchestrator:8000
```

### External URLs (from your machine)
```
Intake:       http://localhost:8001
KYC:          http://localhost:8002
Face:         http://localhost:8003
Payslip:      http://localhost:8004
Bank:         http://localhost:8005
Credit:       http://localhost:8006
Orchestrator: http://localhost:9000
```

## Testing the System

### 1. Check All Services Are Healthy

```bash
# Check Docker Compose status
docker-compose ps

# Expected output:
# NAME                COMMAND                SERVICE         STATUS              PORTS
# intake-agent        "uvicorn main_v2:..."  intake          Up 30s (healthy)    0.0.0.0:8001->8000/tcp
# kyc-agent           "uvicorn main:app..."  kyc             Up 30s (healthy)    0.0.0.0:8002->8000/tcp
# face-agent          "uvicorn main:app..."  face            Up 30s (healthy)    0.0.0.0:8003->8000/tcp
# payslip-agent       "uvicorn main:app..."  payslip         Up 30s (healthy)    0.0.0.0:8004->8000/tcp
# bank-agent          "uvicorn main:app..."  bank            Up 30s (healthy)    0.0.0.0:8005->8000/tcp
# credit-agent        "uvicorn main:app..."  credit          Up 30s (healthy)    0.0.0.0:8006->8000/tcp
# orchestrator-agent  "uvicorn main_v2:..."  orchestrator    Up 15s (healthy)    0.0.0.0:9000->8000/tcp
```

### 2. Test Individual Services

```bash
# Test Intake Agent
curl http://localhost:8001/health

# Test KYC Agent
curl http://localhost:8002/health

# Test Face Agent
curl http://localhost:8003/health

# Test Payslip Agent
curl http://localhost:8004/health

# Test Bank Agent
curl http://localhost:8005/health

# Test Credit Agent
curl http://localhost:8006/health

# Test Orchestrator
curl http://localhost:9000/health
```

### 3. Test Inter-Service Communication (Inside Docker)

```bash
# Check if services can reach each other from within the network
docker-compose exec intake curl http://kyc:8000/health
docker-compose exec orchestrator curl http://intake:8000/health
```

## Data Persistence

All data is persisted in volumes:

```
agents/intake_agent/data/           → /app/data
agents/kyc_agent/data/              → /app/data
agents/face-agent/data/             → /app/data
agents/payslip-agent/data/          → /app/data
agents/bank-agent/data/             → /app/data
agents/credit-agent/audit/          → /app/audit
agents/credit-agent/models/         → /app/models
orchestrator_agent/audit/           → /app/audit
orchestrator_agent/jobs/            → /app/jobs
bank-statement/                     → /app/bank-statement (read-only)
```

## Logs and Debugging

### View All Logs
```bash
# Follow all logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs -f intake
docker-compose logs -f orchestrator

# View last 100 lines
docker-compose logs --tail=100 intake

# View logs from specific time
docker-compose logs --since 2025-12-13T12:00:00
```

### Enter Service Shell
```bash
# Debug inside a container
docker-compose exec intake bash

# Run Python commands
docker-compose exec intake python -c "import sys; print(sys.version)"

# Check installed packages
docker-compose exec kyc pip list
```

### Check Container Resources
```bash
# View CPU and memory usage
docker stats

# Stop all services
docker-compose stop

# Remove all containers (keep images)
docker-compose rm

# Remove everything (containers + images + volumes)
docker-compose down -v
```

## Common Issues and Solutions

### Issue 1: "Cannot connect to orchestrator"

**Problem**: Orchestrator can't reach other agents

**Solution**: Ensure all agents are healthy before orchestrator starts
```bash
# Check orchestrator logs
docker-compose logs orchestrator

# Restart orchestrator
docker-compose restart orchestrator
```

### Issue 2: "Port already in use"

**Problem**: Port 8001-8006 or 9000 already in use

**Solution**: Either stop the conflicting service or modify docker-compose.yml
```bash
# Find what's using the port (e.g., 8001)
lsof -i :8001

# Stop existing services
docker-compose down

# Or modify ports in docker-compose.yml
```

### Issue 3: "Out of memory"

**Problem**: Docker runs out of memory

**Solution**: Increase Docker desktop memory or reduce services
```bash
# Check Docker resource limits (Mac)
docker info | grep "Memory\|Swap"

# Reduce to essential services only
docker-compose up intake orchestrator credit
```

### Issue 4: "Bank statement not accessible"

**Problem**: Bank agent can't access CSV file

**Solution**: Ensure path is mounted correctly
```bash
# Check mounted volumes
docker-compose exec bank ls -la /app/bank-statement/

# If missing, verify source path exists
ls -la "bank-statement/"
```

## Performance Optimization

### 1. Multi-Stage Builds (Future Enhancement)

Smaller images using multi-stage builds:
```dockerfile
FROM python:3.13-slim AS builder
# ... build dependencies ...

FROM python:3.13-slim
COPY --from=builder /opt/venv /opt/venv
# ... minimal runtime ...
```

### 2. Resource Limits

Set limits in docker-compose.yml:
```yaml
services:
  intake:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 3. Caching Strategy

Docker automatically caches layers:
- Dockerfiles are optimized to cache requirements
- Minimize layer changes to speed up rebuilds

## Updating Services

### Update a Single Service

```bash
# Rebuild and restart one service
docker-compose up --build -d intake

# Or without rebuild (use existing image)
docker-compose restart intake
```

### Update All Services

```bash
# Rebuild all and restart
docker-compose up --build -d

# Or without rebuild
docker-compose restart
```

## Production Deployment

For production, consider:

1. **Use Docker registries** (Docker Hub, ECR, GCR)
   ```bash
   docker tag intake-agent:latest myregistry/intake-agent:v1.0
   docker push myregistry/intake-agent:v1.0
   ```

2. **Use Kubernetes** for orchestration
   ```bash
   # Deploy to K8s cluster
   kubectl apply -f k8s-manifests/
   ```

3. **Enable logging drivers**
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

4. **Use secrets management**
   ```bash
   docker secret create db_password db_password.txt
   ```

5. **Implement CI/CD**
   - Build on push
   - Test in staging
   - Deploy to production

## Complete Example Workflow

```bash
# 1. Navigate to project
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"

# 2. Copy environment file
cp .env.docker .env

# 3. Build all images (first time only)
docker-compose build

# 4. Start all services
docker-compose up -d

# 5. Wait for services to be healthy (30-60 seconds)
sleep 60

# 6. Check status
docker-compose ps

# 7. Test the system
curl http://localhost:8001/health

# 8. View logs
docker-compose logs -f

# 9. Make API calls
# See API examples below

# 10. Stop when done
docker-compose down

# 11. Clean up (optional)
docker-compose down -v  # Removes volumes too
```

## API Examples

### Start Intake Conversation (External)

```bash
curl -X POST http://localhost:8001/start \
  -H "Content-Type: application/json" \
  -d '{}' \
  | python -m json.tool
```

### Process Bank Statement (Internal Docker)

```bash
docker-compose exec bank curl -X POST http://bank:8000/bank/parse \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-001",
    "evidence_id": "BANK-001",
    "file_uri": "/app/bank-statement/bank_transactions_ACC1001.csv"
  }' \
  | python -m json.tool
```

## Monitoring and Observability

### Basic Monitoring

```bash
# Watch resource usage
watch -n 1 'docker stats --no-stream'

# Monitor logs in real-time
docker-compose logs -f --timestamps

# Check container health
docker-compose ps
```

### Prometheus Integration (Future)

Add monitoring service:
```yaml
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"
```

## Cleanup and Maintenance

```bash
# Stop all services
docker-compose stop

# Remove all containers
docker-compose rm -f

# Remove images
docker-compose down --rmi all

# Remove volumes (data loss!)
docker-compose down -v

# Prune unused resources
docker system prune -a

# Check Docker disk usage
docker system df
```

## Support and Documentation

- Docker documentation: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- FastAPI in Docker: https://fastapi.tiangolo.com/deployment/docker/

---

**Generated**: December 13, 2025
**System**: Multi-Agent Loan Processing Platform
