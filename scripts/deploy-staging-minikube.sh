#!/bin/bash
# Deploy staging environment to local Minikube cluster
# Usage: ./scripts/deploy-staging-minikube.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Staging Deployment - Minikube        ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/10] Checking prerequisites...${NC}"

# Check Docker
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Docker daemon is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check Minikube
if ! command -v minikube &> /dev/null; then
    echo -e "${RED}ERROR: Minikube is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Minikube is installed${NC}"

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}ERROR: kubectl is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ kubectl is installed${NC}"

# Check Helm
if ! command -v helm &> /dev/null; then
    echo -e "${RED}ERROR: Helm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Helm is installed${NC}"
echo ""

# Step 2: Start Minikube cluster
echo -e "${YELLOW}[2/10] Starting Minikube cluster...${NC}"
if minikube status > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Minikube is already running${NC}"
else
    echo "Starting Minikube with 8GB RAM and 4 CPUs..."
    minikube start --driver=docker --memory=8192 --cpus=4 --kubernetes-version=v1.28.0
    echo -e "${GREEN}✓ Minikube started${NC}"
fi
echo ""

# Step 3: Enable addons
echo -e "${YELLOW}[3/10] Enabling Minikube addons...${NC}"
minikube addons enable ingress
minikube addons enable metrics-server
echo -e "${GREEN}✓ Addons enabled${NC}"
echo ""

# Step 4: Create staging namespace
echo -e "${YELLOW}[4/10] Creating staging namespace...${NC}"
kubectl create namespace staging --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

# Step 5: Build Docker images in Minikube
echo -e "${YELLOW}[5/10] Building Docker images...${NC}"
echo "Setting Docker environment to Minikube..."
eval $(minikube docker-env)

# Build backend image
echo "Building backend image..."
docker build -t todo-backend-api:latest -f "$PROJECT_ROOT/backend/Dockerfile" "$PROJECT_ROOT/backend"

# Build frontend image
echo "Building frontend image..."
docker build -t todo-frontend:latest -f "$PROJECT_ROOT/frontend/Dockerfile" "$PROJECT_ROOT/frontend"

# Build microservices
echo "Building websocket-sync image..."
docker build -t todo-websocket-sync:latest -f "$PROJECT_ROOT/backend/microservices/websocket_sync/Dockerfile" "$PROJECT_ROOT/backend/microservices/websocket_sync"

echo "Building notification service image..."
docker build -t todo-notification:latest -f "$PROJECT_ROOT/backend/microservices/notification/Dockerfile" "$PROJECT_ROOT/backend/microservices/notification"

echo "Building recurring-task service image..."
docker build -t todo-recurring-task:latest -f "$PROJECT_ROOT/backend/microservices/recurring_task/Dockerfile" "$PROJECT_ROOT/backend/microservices/recurring_task"

echo -e "${GREEN}✓ Images built${NC}"
echo ""

# Step 6: Create secrets
echo -e "${YELLOW}[6/10] Creating Kubernetes secrets...${NC}"

# Generate random secrets for staging
BETTER_AUTH_SECRET=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)

kubectl create secret generic backend-secrets \
    --namespace=staging \
    --from-literal=database-url="postgresql://postgres:postgres@postgres:5432/todo_staging" \
    --from-literal=redis-url="redis://redis:6379/0" \
    --from-literal=kafka-brokers="redpanda:9092" \
    --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
    --from-literal=openai-api-key="sk-test-key" \
    --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ Secrets created${NC}"
echo ""

# Step 7: Deploy infrastructure (PostgreSQL, Redis, Redpanda)
echo -e "${YELLOW}[7/10] Deploying infrastructure services...${NC}"

# Deploy PostgreSQL
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: staging
spec:
  ports:
  - port: 5432
  selector:
    app: postgres
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: staging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        env:
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          value: postgres
        - name: POSTGRES_DB
          value: todo_staging
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        emptyDir: {}
EOF

# Deploy Redis
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: staging
spec:
  ports:
  - port: 6379
  selector:
    app: redis
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: staging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
EOF

# Deploy Redpanda
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: redpanda
  namespace: staging
spec:
  ports:
  - port: 9092
    name: kafka
  selector:
    app: redpanda
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redpanda
  namespace: staging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redpanda
  template:
    metadata:
      labels:
        app: redpanda
    spec:
      containers:
      - name: redpanda
        image: docker.redpanda.com/redpandadata/redpanda:v23.3.3
        command:
        - redpanda
        - start
        - --kafka-addr
        - internal://0.0.0.0:9092
        - --advertise-kafka-addr
        - internal://redpanda:9092
        - --mode
        - dev-container
        - --smp
        - "1"
        ports:
        - containerPort: 9092
EOF

echo "Waiting for infrastructure services to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/postgres -n staging
kubectl wait --for=condition=available --timeout=120s deployment/redis -n staging
kubectl wait --for=condition=available --timeout=120s deployment/redpanda -n staging

echo -e "${GREEN}✓ Infrastructure deployed${NC}"
echo ""

# Step 8: Install Dapr
echo -e "${YELLOW}[8/10] Installing Dapr runtime...${NC}"
if ! helm list -n dapr-system | grep -q dapr; then
    helm repo add dapr https://dapr.github.io/helm-charts/ || true
    helm repo update
    helm upgrade --install dapr dapr/dapr \
        --version=1.12 \
        --namespace dapr-system \
        --create-namespace \
        --wait
    echo -e "${GREEN}✓ Dapr installed${NC}"
else
    echo -e "${GREEN}✓ Dapr already installed${NC}"
fi
echo ""

# Step 9: Deploy Dapr components
echo -e "${YELLOW}[9/10] Deploying Dapr components...${NC}"
kubectl apply -f "$PROJECT_ROOT/infrastructure/dapr/" -n staging
echo -e "${GREEN}✓ Dapr components deployed${NC}"
echo ""

# Step 10: Deploy application services using Helm
echo -e "${YELLOW}[10/10] Deploying application services...${NC}"

# Deploy backend
helm upgrade --install backend-api "$PROJECT_ROOT/infrastructure/helm/backend" \
    --namespace=staging \
    --set image.repository=todo-backend-api \
    --set image.tag=latest \
    --set image.pullPolicy=Never \
    --set ingress.enabled=false \
    --wait

# Deploy frontend
helm upgrade --install frontend "$PROJECT_ROOT/infrastructure/helm/frontend" \
    --namespace=staging \
    --set image.repository=todo-frontend \
    --set image.tag=latest \
    --set image.pullPolicy=Never \
    --set ingress.enabled=false \
    --wait

# Deploy websocket-sync
helm upgrade --install websocket-sync "$PROJECT_ROOT/infrastructure/helm/websocket-sync" \
    --namespace=staging \
    --set image.repository=todo-websocket-sync \
    --set image.tag=latest \
    --set image.pullPolicy=Never \
    --wait

# Deploy notification service
helm upgrade --install notification "$PROJECT_ROOT/infrastructure/helm/notification" \
    --namespace=staging \
    --set image.repository=todo-notification \
    --set image.tag=latest \
    --set image.pullPolicy=Never \
    --wait

echo -e "${GREEN}✓ Application services deployed${NC}"
echo ""

# Display summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Minikube Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Cluster Information:"
echo "  Minikube IP:       $(minikube ip)"
echo "  Kubernetes:        $(kubectl version --short 2>/dev/null | grep Server | cut -d' ' -f3)"
echo ""
echo "Access Services:"
echo "  List services:     minikube service list -n staging"
echo "  Frontend:          minikube service frontend -n staging"
echo "  Backend API:       minikube service backend-api -n staging"
echo ""
echo "Useful Commands:"
echo "  View pods:         kubectl get pods -n staging"
echo "  View logs:         kubectl logs -f deployment/backend-api -n staging"
echo "  Port forward:      kubectl port-forward -n staging svc/backend-api 8000:8000"
echo "  Dashboard:         minikube dashboard"
echo ""
echo "Stop Minikube:"
echo "  minikube stop"
echo ""
echo "Delete Cluster:"
echo "  minikube delete"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
