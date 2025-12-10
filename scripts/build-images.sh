#!/bin/bash

# MoneyMind Finance AI - Docker Build Script
# This script builds all Docker images for the project

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}MoneyMind Finance AI - Docker Build${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration
REGISTRY="${DOCKER_REGISTRY:-localhost}"
VERSION="${VERSION:-latest}"
BACKEND_IMAGE="$REGISTRY/moneymind-backend:$VERSION"
FRONTEND_IMAGE="$REGISTRY/moneymind-frontend:$VERSION"

echo "Building images with tag: $VERSION"
echo "Registry: $REGISTRY"
echo ""

# Build backend
echo "Building backend image..."
docker build -t $BACKEND_IMAGE ./backend
echo -e "${GREEN}✓${NC} Backend image built: $BACKEND_IMAGE"
echo ""

# Build frontend
echo "Building frontend image..."
docker build -t $FRONTEND_IMAGE ./frontend
echo -e "${GREEN}✓${NC} Frontend image built: $FRONTEND_IMAGE"
echo ""

# Optional: Push to registry
if [ "$REGISTRY" != "localhost" ]; then
    read -p "Push images to registry? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Pushing backend image..."
        docker push $BACKEND_IMAGE
        echo -e "${GREEN}✓${NC} Backend image pushed"
        
        echo "Pushing frontend image..."
        docker push $FRONTEND_IMAGE
        echo -e "${GREEN}✓${NC} Frontend image pushed"
    fi
fi

echo ""
echo -e "${GREEN}Build completed successfully!${NC}"
echo ""
echo "Images:"
echo "  - $BACKEND_IMAGE"
echo "  - $FRONTEND_IMAGE"
echo ""
