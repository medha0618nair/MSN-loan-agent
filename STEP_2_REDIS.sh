#!/bin/bash
# STEP 2: Start Redis (Terminal 1)

docker run -d -p 6379:6379 redis:7-alpine
echo "✅ Redis started"
docker ps | grep redis
