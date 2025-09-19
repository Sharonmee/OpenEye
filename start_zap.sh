#!/bin/bash

# Script to start OWASP ZAP in Docker for OpenEye integration

echo "Starting OWASP ZAP in Docker..."

# Stop any existing ZAP container
docker stop zap-container 2>/dev/null || true
docker rm zap-container 2>/dev/null || true

# Start ZAP in daemon mode with API enabled
docker run -d \
  --name zap-container \
  -p 8080:8080 \
  -p 8090:8090 \
  -i owasp/zap2docker-stable:latest \
  zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true

echo "ZAP is starting up..."
echo "Waiting for ZAP to be ready..."

# Wait for ZAP to be ready
for i in {1..30}; do
  if curl -s http://localhost:8080/JSON/core/view/version/ > /dev/null 2>&1; then
    echo "ZAP is ready!"
    echo "API available at: http://localhost:8080"
    echo "Web UI available at: http://localhost:8090"
    break
  fi
  echo "Waiting... ($i/30)"
  sleep 2
done

echo ""
echo "ZAP Docker container is running!"
echo "To stop ZAP: docker stop zap-container"
echo "To view logs: docker logs zap-container"
echo ""
echo "You can now start your Django application and begin scanning!"
