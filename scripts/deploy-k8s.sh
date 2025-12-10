#!/bin/bash

# MoneyMind Finance AI - Kubernetes Deployment Script
# This script deploys the entire MoneyMind infrastructure to Kubernetes

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="moneymind"
K8S_DIR="./k8s"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}MoneyMind Finance AI - K8s Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please install kubectl first."
    exit 1
fi
print_status "kubectl found"

if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster. Please configure kubectl."
    exit 1
fi
print_status "Connected to Kubernetes cluster"

# Check if k8s directory exists
if [ ! -d "$K8S_DIR" ]; then
    print_error "K8s directory not found: $K8S_DIR"
    exit 1
fi
print_status "K8s manifests directory found"

echo ""
echo "Starting deployment..."
echo ""

# Step 1: Create namespace
echo "1. Creating namespace..."
kubectl apply -f $K8S_DIR/00-namespace.yaml
print_status "Namespace created"
echo ""

# Step 2: Create ConfigMap
echo "2. Creating ConfigMap..."
kubectl apply -f $K8S_DIR/01-configmap.yaml
print_status "ConfigMap created"
echo ""

# Step 3: Create Secrets
echo "3. Creating Secrets..."
print_warning "Make sure you've updated the secrets in $K8S_DIR/02-secrets.yaml"
read -p "Have you updated the secrets? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Please update secrets before deploying"
    exit 1
fi
kubectl apply -f $K8S_DIR/02-secrets.yaml
print_status "Secrets created"
echo ""

# Step 4: Create PVCs
echo "4. Creating Persistent Volume Claims..."
kubectl apply -f $K8S_DIR/03-pvcs.yaml
print_status "PVCs created"
echo ""

# Step 5: Deploy databases
echo "5. Deploying databases..."

echo "   - PostgreSQL..."
kubectl apply -f $K8S_DIR/04-postgres.yaml
print_status "PostgreSQL deployed"

echo "   - Redis..."
kubectl apply -f $K8S_DIR/05-redis.yaml
print_status "Redis deployed"

echo "   - Qdrant..."
kubectl apply -f $K8S_DIR/06-qdrant.yaml
print_status "Qdrant deployed"

echo "   - Neo4j..."
kubectl apply -f $K8S_DIR/07-neo4j.yaml
print_status "Neo4j deployed"
echo ""

# Step 6: Wait for databases to be ready
echo "6. Waiting for databases to be ready..."
echo "   This may take a few minutes..."

kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s || print_warning "PostgreSQL timeout"
print_status "PostgreSQL ready"

kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s || print_warning "Redis timeout"
print_status "Redis ready"

kubectl wait --for=condition=ready pod -l app=qdrant -n $NAMESPACE --timeout=300s || print_warning "Qdrant timeout"
print_status "Qdrant ready"

kubectl wait --for=condition=ready pod -l app=neo4j -n $NAMESPACE --timeout=300s || print_warning "Neo4j timeout"
print_status "Neo4j ready"
echo ""

# Step 7: Deploy backend
echo "7. Deploying backend..."
print_warning "Make sure backend image is built and available"
kubectl apply -f $K8S_DIR/08-backend.yaml
print_status "Backend deployed"
echo ""

# Step 8: Deploy frontend
echo "8. Deploying frontend..."
print_warning "Make sure frontend image is built and available"
kubectl apply -f $K8S_DIR/09-frontend.yaml
print_status "Frontend deployed"
echo ""

# Step 9: Wait for applications
echo "9. Waiting for applications to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=300s || print_warning "Backend timeout"
print_status "Backend ready"

kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=300s || print_warning "Frontend timeout"
print_status "Frontend ready"
echo ""

# Step 10: Optional Ingress
echo "10. Ingress setup (optional)..."
read -p "Do you want to deploy Ingress? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Make sure to update domain names in $K8S_DIR/10-ingress.yaml"
    read -p "Have you updated the domain names? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl apply -f $K8S_DIR/10-ingress.yaml
        print_status "Ingress deployed"
    else
        print_warning "Skipping Ingress deployment"
    fi
else
    print_warning "Skipping Ingress deployment"
fi
echo ""

# Display deployment status
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo "Pods:"
kubectl get pods -n $NAMESPACE
echo ""

echo "Services:"
kubectl get svc -n $NAMESPACE
echo ""

echo "PVCs:"
kubectl get pvc -n $NAMESPACE
echo ""

# Get access information
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Access Information${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

FRONTEND_SERVICE=$(kubectl get svc frontend-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
if [ "$FRONTEND_SERVICE" != "pending" ] && [ -n "$FRONTEND_SERVICE" ]; then
    echo "Frontend URL: http://$FRONTEND_SERVICE"
else
    print_warning "Frontend LoadBalancer IP is pending. Use port-forward:"
    echo "  kubectl port-forward svc/frontend-service 3000:80 -n $NAMESPACE"
fi
echo ""

echo "To access backend API:"
echo "  kubectl port-forward svc/backend-service 8000:8000 -n $NAMESPACE"
echo ""

echo "To view logs:"
echo "  kubectl logs -f deployment/backend -n $NAMESPACE"
echo "  kubectl logs -f deployment/frontend -n $NAMESPACE"
echo ""

print_status "Deployment completed successfully!"
echo ""
