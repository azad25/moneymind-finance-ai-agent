#!/bin/bash
set -e

echo "Starting Docker daemon..."
dockerd-entrypoint.sh &

echo "Waiting for Docker to be ready..."
until docker info > /dev/null 2>&1; do
    sleep 1
done
echo "Docker is ready!"

# Try to pull sandboxes, but continue even if it fails
echo "Initializing sandbox-mcp..."
sandbox-mcp --pull --force || echo "Failed to pull sandboxes, will use local config"

# Try to build sandboxes, but continue even if it fails
echo "Building sandbox images..."
sandbox-mcp --build || echo "Failed to build sandboxes, HTTP wrapper will still run"

echo "Starting HTTP wrapper..."
exec python3 /app/http_wrapper.py
