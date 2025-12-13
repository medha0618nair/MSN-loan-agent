# Docker Quick Reference - Common Commands

## System Information

```bash
# Check Docker version
docker --version
docker-compose --version

# Check Docker daemon status
docker info

# Check system resource usage
docker system df
docker stats
```

## Project Setup

```bash
# Navigate to project
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"

# Verify Docker Compose file
docker-compose config

# Validate syntax
docker-compose config > /dev/null && echo "✓ Valid" || echo "✗ Invalid"
```

## Building

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build intake

# Build without cache (force rebuild)
docker-compose build --no-cache

# Build and show build logs
docker-compose build --verbose
```

## Starting Services

```bash
# Start all services in background
docker-compose up -d

# Start all services and watch logs
docker-compose up

# Start specific services
docker-compose up -d intake orchestrator

# Start with build (rebuild if changed)
docker-compose up -d --build

# Start with pull (update images first)
docker-compose up -d --pull always

# Scale a service to multiple instances
docker-compose up -d --scale bank=2
```

## Monitoring

```bash
# Show all containers
docker-compose ps

# Show containers with full details
docker-compose ps -a

# Watch containers update in real-time
watch -n 1 'docker-compose ps'

# Monitor resource usage
docker stats

# Live monitoring
docker stats --no-stream

# Show process inside container
docker-compose top intake
```

## Logs

```bash
# View all logs
docker-compose logs

# View logs for specific service
docker-compose logs intake

# Follow logs in real-time (all services)
docker-compose logs -f

# Follow logs for specific service
docker-compose logs -f intake

# Last 50 lines
docker-compose logs --tail=50

# Last 100 lines with timestamps
docker-compose logs -f --timestamps --tail=100

# Logs since specific time
docker-compose logs --since 10m  # Last 10 minutes
docker-compose logs --since 2025-12-13T12:00:00

# Filter logs by service
docker-compose logs bank | grep "ERROR"

# Stream logs to file
docker-compose logs -f > docker-logs.txt
```

## Debugging

```bash
# Open shell in container
docker-compose exec intake bash

# Open shell with root
docker-compose exec -u root intake bash

# Run Python in container
docker-compose exec intake python -c "print('Hello')"

# Run command in container
docker-compose exec intake ls -la /app/

# Check environment variables
docker-compose exec intake env

# Check installed packages
docker-compose exec intake pip list

# Check Python version
docker-compose exec intake python --version

# Check system info inside container
docker-compose exec intake uname -a

# Network connectivity test
docker-compose exec orchestrator curl http://intake:8000/health

# DNS resolution test
docker-compose exec orchestrator nslookup intake

# IP address inside container
docker-compose exec intake hostname -I

# Check network interfaces
docker-compose exec intake ip addr
```

## Testing Endpoints

```bash
# Test health endpoint
curl http://localhost:8001/health

# Test with verbose output
curl -v http://localhost:8001/health

# Test with pretty-printed JSON
curl http://localhost:8001/health | jq '.'

# Test with custom headers
curl -H "Content-Type: application/json" \
     http://localhost:8001/health

# Test POST request
curl -X POST http://localhost:8001/start \
     -H "Content-Type: application/json" \
     -d '{}'

# Save response to file
curl http://localhost:8001/health > response.json

# Show response headers only
curl -I http://localhost:8001/health

# Test with timeout
curl --max-time 5 http://localhost:8001/health

# Test all services quickly
for port in 8001 8002 8003 8004 8005 8006 9000; do
  echo "Port $port: $(curl -s http://localhost:$port/health | jq '.status' 2>/dev/null || echo 'FAILED')"
done
```

## Stopping and Removing

```bash
# Stop all services (keep containers)
docker-compose stop

# Stop specific service
docker-compose stop intake

# Stop all with timeout
docker-compose stop -t 30

# Pause services (freeze containers)
docker-compose pause

# Unpause services
docker-compose unpause

# Remove stopped containers
docker-compose rm

# Remove stopped containers without prompt
docker-compose rm -f

# Remove containers and volumes
docker-compose rm -v

# Remove everything (containers, images, volumes)
docker-compose down

# Complete cleanup
docker-compose down -v --rmi all
```

## Restarting

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart intake

# Restart with timeout
docker-compose restart -t 60

# Stop and start all services
docker-compose down && docker-compose up -d

# Restart with rebuild
docker-compose down && docker-compose up -d --build
```

## Data Management

```bash
# List all volumes
docker volume ls

# Show volume details
docker volume inspect <volume_name>

# Check volume size
docker system df -v

# Backup volume
docker volume inspect <volume_name> | grep Mountpoint
# Then tar the mountpoint directory

# Clean up unused volumes
docker volume prune

# Remove specific volume
docker volume rm <volume_name>

# Remove all unused volumes
docker volume prune -f
```

## Network Management

```bash
# List networks
docker network ls

# Show network details
docker network inspect loan-agent-network

# Show containers on network
docker network inspect loan-agent-network | jq '.Containers'

# Create custom network (if needed)
docker network create my-network

# Connect container to network
docker network connect my-network <container_id>

# Disconnect container from network
docker network disconnect my-network <container_id>

# Remove network
docker network rm my-network

# Prune unused networks
docker network prune
```

## Images

```bash
# List all images
docker images

# Show image details
docker inspect <image_id>

# Tag image
docker tag <image> <new_name>:<tag>

# Remove image
docker rmi <image_id>

# Remove unused images
docker image prune

# Remove all images
docker image prune -a

# Save image to file
docker save intake-agent > intake-agent.tar

# Load image from file
docker load < intake-agent.tar

# Push to registry (if configured)
docker push <registry>/<image>:<tag>

# Pull from registry
docker pull <registry>/<image>:<tag>
```

## Service Management

```bash
# Show service versions
docker-compose version

# Validate compose file
docker-compose config

# Show compose environment
docker-compose config -q

# List services defined
docker-compose config --services

# Show dependency order
docker-compose config | grep -A 5 "depends_on"

# Execute in running service
docker-compose exec intake bash -c "command"

# Execute as different user
docker-compose exec -u root intake bash

# Execute with environment variable
docker-compose exec -e VAR=value intake env

# Port info
docker-compose port intake 8000  # Show mapped port
```

## Health Checks

```bash
# Check service health
docker-compose ps | grep healthy

# Follow container exit codes
docker-compose logs --no-log-prefix

# Manual health check
curl -f http://localhost:8001/health || echo "Unhealthy"

# Health check with details
docker-compose exec intake curl -v http://intake:8000/health

# Wait for service to be healthy
for i in {1..30}; do
  if curl -s http://localhost:8001/health > /dev/null; then
    echo "Service is healthy"
    break
  fi
  echo "Waiting... ($i/30)"
  sleep 1
done
```

## Useful Combinations

### Complete System Check

```bash
#!/bin/bash
echo "=== System Check ==="
echo "Docker: $(docker --version)"
echo "Compose: $(docker-compose --version)"
echo ""
echo "Services:"
docker-compose ps
echo ""
echo "Health:"
for port in 8001 8002 8003 8004 8005 8006 9000; do
  curl -s http://localhost:$port/health | jq '.status' 2>/dev/null && echo "Port $port: OK" || echo "Port $port: FAILED"
done
```

### Restart Failed Services

```bash
#!/bin/bash
echo "Checking for unhealthy services..."
docker-compose ps | grep -v healthy | while read line; do
  SERVICE=$(echo $line | awk '{print $1}')
  echo "Restarting $SERVICE..."
  docker-compose restart $SERVICE
done
```

### View Recent Errors

```bash
docker-compose logs | grep -i "error\|exception\|failed" | tail -20
```

### Monitor Single Service

```bash
# Watch one service logs with filtering
docker-compose logs -f intake | grep -E "ERROR|WARNING"
```

### System Cleanup

```bash
#!/bin/bash
echo "Cleaning up Docker..."
docker system prune -f         # Remove unused containers/images/networks
docker volume prune -f         # Remove unused volumes
docker network prune -f        # Remove unused networks
docker image prune -a -f       # Remove dangling images
echo "Cleanup complete"
```

## Emergency Commands

```bash
# Kill all containers (hard stop)
docker kill $(docker ps -q)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)

# Stop Docker daemon (not recommended)
# On Mac: use Docker Desktop menu → Quit

# Reset Docker completely (CAUTION: Destroys all data)
# On Mac: Docker Desktop → Preferences → Reset → Reset to factory defaults
```

## Performance Tuning

```bash
# Check resource limits per service
for container in $(docker-compose ps -q); do
  echo "Container: $(docker ps --no-trunc | grep $container | awk '{print $NF}')"
  docker stats --no-stream --format "table {{.MemUsage}}" $container
done

# Monitor continuously
watch -n 1 'docker stats --no-stream'

# Limit memory for a service (in docker-compose.yml)
# deploy:
#   resources:
#     limits:
#       memory: 1G
```

## Backup and Restore

```bash
# Backup all volumes
docker run --rm \
  -v loan-agent-network:/volume \
  -v $PWD:/backup \
  alpine tar czf /backup/backup.tar.gz /volume

# Restore from backup
docker run --rm \
  -v loan-agent-network:/volume \
  -v $PWD:/backup \
  alpine tar xzf /backup/backup.tar.gz -C /

# Backup database
docker-compose exec kyc mysqldump -u user -p database > backup.sql

# Backup Docker Compose state
docker-compose config > compose-backup.yml
```

## Shortcuts for Common Tasks

```bash
# Start everything
alias docker-start="cd /Users/apple/Desktop/codered\ final/MSN-loan-agent && docker-compose up -d"

# Stop everything
alias docker-stop="docker-compose down"

# View all logs
alias docker-logs="docker-compose logs -f"

# Quick status
alias docker-status="docker-compose ps"

# Full reset
alias docker-reset="docker-compose down -v && docker-compose up -d --build"
```

Add to `~/.zshrc`:
```bash
# Save the aliases above to ~/.zshrc
source ~/.zshrc
```

## Key Files Reference

```bash
# Main files location
PROJECT_DIR="/Users/apple/Desktop/codered final/MSN-loan-agent"

# Configuration
docker-compose.yml              # Main orchestration file
.env.docker                     # Environment variables
orchestrator_agent/config_v2_docker.py  # Docker config

# Dockerfiles
agents/*/Dockerfile             # Each agent's Dockerfile
orchestrator_agent/Dockerfile   # Orchestrator Dockerfile

# Data locations
agents/*/data/                  # Stored data
agents/*/audit/                 # Audit logs
bank-statement/                 # Bank data
```

## Troubleshooting Quick Fixes

| Problem | Command |
|---------|---------|
| Service won't start | `docker-compose logs <service>` |
| Port already in use | `lsof -i :<port>` |
| Out of memory | `docker stats` → increase Docker RAM |
| Network issues | `docker network inspect loan-agent-network` |
| Slow performance | `docker system df` → free space |
| Container keeps crashing | `docker-compose up <service>` → watch output |

---

**Quick Start:**
```bash
cd "/Users/apple/Desktop/codered final/MSN-loan-agent"
docker-compose up -d
docker-compose ps
curl http://localhost:8001/health
```

**Debugging:**
```bash
docker-compose logs -f              # See what's happening
docker-compose exec intake bash     # Debug inside container
curl http://localhost:8001/health   # Test endpoint
```

**Cleanup:**
```bash
docker-compose down                 # Stop and remove
docker-compose down -v              # Stop and remove volumes (data loss)
```
