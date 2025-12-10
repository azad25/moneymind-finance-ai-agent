# MoneyMind Finance AI Agent - Quick Start Guide

## 🚀 Quick Start with Docker Compose

### 1. Prerequisites
- Docker Engine 24.0+
- Docker Compose 2.20+
- 8GB RAM minimum

### 2. Start the Application

```bash
# Navigate to project directory
cd /home/azad/Documents/moneymind-finance-ai-agent

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (user: neo4j, password: moneymind_neo4j_password_2024)

### 4. Stop the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (⚠️ WARNING: This deletes all data)
docker-compose down -v
```

---

## ☸️ Quick Start with Kubernetes

### 1. Prerequisites
- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured
- Docker for building images

### 2. Build Images

```bash
# Make script executable
chmod +x scripts/build-images.sh

# Build images
./scripts/build-images.sh
```

### 3. Deploy to Kubernetes

```bash
# Make script executable
chmod +x scripts/deploy-k8s.sh

# Deploy
./scripts/deploy-k8s.sh
```

### 4. Access the Application

```bash
# Get frontend service IP
kubectl get svc frontend-service -n moneymind

# Or use port-forward
kubectl port-forward svc/frontend-service 3000:80 -n moneymind
kubectl port-forward svc/backend-service 8000:8000 -n moneymind
```

Then access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

---

## 📝 Configuration

### Update Secrets (Important!)

Before deploying to production, update these files:

1. **Docker Compose**: Edit `docker-compose.yml`
   - Change all passwords
   - Add your API keys

2. **Kubernetes**: Edit `k8s/02-secrets.yaml`
   - Change all passwords
   - Add your API keys

### Required API Keys

- **ExchangeRate API**: Get from https://www.exchangerate-api.com/
- **AlphaVantage API**: Get from https://www.alphavantage.co/

---

## 🔍 Troubleshooting

### Services not starting?

```bash
# Docker Compose
docker-compose logs <service-name>

# Kubernetes
kubectl logs -f deployment/<service-name> -n moneymind
```

### Database connection errors?

```bash
# Check if databases are running
docker-compose ps
# or
kubectl get pods -n moneymind
```

### Out of memory?

Increase Docker memory limit in Docker Desktop settings (Resources > Memory)

---

## 📚 Full Documentation

For detailed documentation, see [INFRASTRUCTURE.md](./INFRASTRUCTURE.md)

---

## 🆘 Need Help?

1. Check logs for errors
2. Review [INFRASTRUCTURE.md](./INFRASTRUCTURE.md) troubleshooting section
3. Verify all prerequisites are met
