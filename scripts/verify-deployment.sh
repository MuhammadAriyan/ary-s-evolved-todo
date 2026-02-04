#!/bin/bash
# Verify staging deployment
# Usage: ./scripts/verify-deployment.sh [local|minikube]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Deployment type (local or minikube)
DEPLOYMENT_TYPE="${1:-local}"

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Deployment Verification              ${NC}"
echo -e "${BLUE}  Type: $DEPLOYMENT_TYPE                ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Track test results
PASSED=0
FAILED=0
WARNINGS=0

# Function to check service
check_service() {
    local service_name=$1
    local check_command=$2
    local expected_output=$3

    echo -n "  $service_name: "

    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ Not running${NC}"
        ((FAILED++))
        return 1
    fi
}

# Function to check HTTP endpoint
check_http() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}

    echo -n "  $service_name: "

    if command -v curl &> /dev/null; then
        status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

        if [ "$status_code" = "$expected_status" ]; then
            echo -e "${GREEN}✓ Responding ($status_code)${NC}"
            ((PASSED++))
            return 0
        else
            echo -e "${RED}✗ Failed ($status_code)${NC}"
            ((FAILED++))
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ curl not available${NC}"
        ((WARNINGS++))
        return 1
    fi
}

# Verify based on deployment type
if [ "$DEPLOYMENT_TYPE" = "local" ]; then
    echo -e "${YELLOW}Verifying Docker Compose deployment...${NC}"
    echo ""

    # Check Docker is running
    echo -e "${BLUE}[1/5] Docker Status${NC}"
    if ! docker ps > /dev/null 2>&1; then
        echo -e "${RED}ERROR: Docker daemon is not running${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is running${NC}"
    echo ""

    # Check infrastructure containers
    echo -e "${BLUE}[2/5] Infrastructure Services${NC}"
    check_service "PostgreSQL" "docker ps | grep -q todo-postgres"
    check_service "Redis" "docker ps | grep -q todo-redis"
    check_service "Redpanda" "docker ps | grep -q todo-redpanda"
    check_service "Dapr Placement" "docker ps | grep -q todo-dapr-placement"
    echo ""

    # Check container health
    echo -e "${BLUE}[3/5] Service Health${NC}"
    check_service "PostgreSQL Health" "docker exec todo-postgres pg_isready -U postgres"
    check_service "Redis Health" "docker exec todo-redis redis-cli ping | grep -q PONG"
    echo ""

    # Check HTTP endpoints (if services are running)
    echo -e "${BLUE}[4/5] HTTP Endpoints${NC}"
    check_http "Backend API Health" "http://localhost:8000/health" || echo "  Note: Start backend with: cd backend && uvicorn app.main:app --reload --port 8000"
    check_http "Frontend" "http://localhost:3000" || echo "  Note: Start frontend with: cd frontend && npm run dev"
    check_http "Redpanda Console" "http://localhost:8080" || true
    echo ""

    # Check ports
    echo -e "${BLUE}[5/5] Port Availability${NC}"
    echo -n "  PostgreSQL (5432): "
    if nc -z localhost 5432 2>/dev/null || (echo > /dev/tcp/localhost/5432) 2>/dev/null; then
        echo -e "${GREEN}✓ Open${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Closed${NC}"
        ((FAILED++))
    fi

    echo -n "  Redis (6379): "
    if nc -z localhost 6379 2>/dev/null || (echo > /dev/tcp/localhost/6379) 2>/dev/null; then
        echo -e "${GREEN}✓ Open${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Closed${NC}"
        ((FAILED++))
    fi

    echo -n "  Redpanda (19092): "
    if nc -z localhost 19092 2>/dev/null || (echo > /dev/tcp/localhost/19092) 2>/dev/null; then
        echo -e "${GREEN}✓ Open${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Closed${NC}"
        ((FAILED++))
    fi
    echo ""

    # Display logs command
    echo -e "${YELLOW}View Logs:${NC}"
    echo "  docker compose -f infrastructure/docker-compose.dev.yml logs -f"
    echo ""

elif [ "$DEPLOYMENT_TYPE" = "minikube" ]; then
    echo -e "${YELLOW}Verifying Minikube deployment...${NC}"
    echo ""

    # Check Minikube is running
    echo -e "${BLUE}[1/6] Minikube Status${NC}"
    if ! minikube status > /dev/null 2>&1; then
        echo -e "${RED}ERROR: Minikube is not running${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Minikube is running${NC}"
    echo ""

    # Check namespace
    echo -e "${BLUE}[2/6] Namespace${NC}"
    if kubectl get namespace staging > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Staging namespace exists${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ Staging namespace not found${NC}"
        ((FAILED++))
    fi
    echo ""

    # Check infrastructure pods
    echo -e "${BLUE}[3/6] Infrastructure Pods${NC}"
    kubectl get pods -n staging -l app=postgres -o jsonpath='{.items[0].status.phase}' 2>/dev/null | grep -q "Running" && \
        echo -e "  PostgreSQL: ${GREEN}✓ Running${NC}" && ((PASSED++)) || \
        (echo -e "  PostgreSQL: ${RED}✗ Not running${NC}" && ((FAILED++)))

    kubectl get pods -n staging -l app=redis -o jsonpath='{.items[0].status.phase}' 2>/dev/null | grep -q "Running" && \
        echo -e "  Redis: ${GREEN}✓ Running${NC}" && ((PASSED++)) || \
        (echo -e "  Redis: ${RED}✗ Not running${NC}" && ((FAILED++)))

    kubectl get pods -n staging -l app=redpanda -o jsonpath='{.items[0].status.phase}' 2>/dev/null | grep -q "Running" && \
        echo -e "  Redpanda: ${GREEN}✓ Running${NC}" && ((PASSED++)) || \
        (echo -e "  Redpanda: ${RED}✗ Not running${NC}" && ((FAILED++)))
    echo ""

    # Check application pods
    echo -e "${BLUE}[4/6] Application Pods${NC}"
    kubectl get pods -n staging -l app.kubernetes.io/name=backend-api -o jsonpath='{.items[0].status.phase}' 2>/dev/null | grep -q "Running" && \
        echo -e "  Backend API: ${GREEN}✓ Running${NC}" && ((PASSED++)) || \
        (echo -e "  Backend API: ${RED}✗ Not running${NC}" && ((FAILED++)))

    kubectl get pods -n staging -l app.kubernetes.io/name=frontend -o jsonpath='{.items[0].status.phase}' 2>/dev/null | grep -q "Running" && \
        echo -e "  Frontend: ${GREEN}✓ Running${NC}" && ((PASSED++)) || \
        (echo -e "  Frontend: ${RED}✗ Not running${NC}" && ((FAILED++)))

    kubectl get pods -n staging -l app.kubernetes.io/name=websocket-sync -o jsonpath='{.items[0].status.phase}' 2>/dev/null | grep -q "Running" && \
        echo -e "  WebSocket Sync: ${GREEN}✓ Running${NC}" && ((PASSED++)) || \
        (echo -e "  WebSocket Sync: ${RED}✗ Not running${NC}" && ((FAILED++)))

    kubectl get pods -n staging -l app.kubernetes.io/name=notification -o jsonpath='{.items[0].status.phase}' 2>/dev/null | grep -q "Running" && \
        echo -e "  Notification: ${GREEN}✓ Running${NC}" && ((PASSED++)) || \
        (echo -e "  Notification: ${RED}✗ Not running${NC}" && ((FAILED++)))
    echo ""

    # Check Dapr
    echo -e "${BLUE}[5/6] Dapr Runtime${NC}"
    if kubectl get namespace dapr-system > /dev/null 2>&1; then
        echo -e "  Dapr Namespace: ${GREEN}✓ Exists${NC}"
        ((PASSED++))

        dapr_pods=$(kubectl get pods -n dapr-system --no-headers 2>/dev/null | wc -l)
        if [ "$dapr_pods" -gt 0 ]; then
            echo -e "  Dapr Pods: ${GREEN}✓ $dapr_pods running${NC}"
            ((PASSED++))
        else
            echo -e "  Dapr Pods: ${RED}✗ None running${NC}"
            ((FAILED++))
        fi
    else
        echo -e "  Dapr: ${RED}✗ Not installed${NC}"
        ((FAILED++))
    fi
    echo ""

    # Check services
    echo -e "${BLUE}[6/6] Services${NC}"
    kubectl get svc -n staging backend-api > /dev/null 2>&1 && \
        echo -e "  Backend API Service: ${GREEN}✓ Exists${NC}" && ((PASSED++)) || \
        (echo -e "  Backend API Service: ${RED}✗ Not found${NC}" && ((FAILED++)))

    kubectl get svc -n staging frontend > /dev/null 2>&1 && \
        echo -e "  Frontend Service: ${GREEN}✓ Exists${NC}" && ((PASSED++)) || \
        (echo -e "  Frontend Service: ${RED}✗ Not found${NC}" && ((FAILED++)))
    echo ""

    # Display access commands
    echo -e "${YELLOW}Access Services:${NC}"
    echo "  minikube service list -n staging"
    echo "  minikube service frontend -n staging"
    echo "  minikube service backend-api -n staging"
    echo ""
    echo -e "${YELLOW}View Logs:${NC}"
    echo "  kubectl logs -f deployment/backend-api -n staging"
    echo "  kubectl logs -f deployment/frontend -n staging"
    echo ""
    echo -e "${YELLOW}Port Forward:${NC}"
    echo "  kubectl port-forward -n staging svc/backend-api 8000:8000"
    echo "  kubectl port-forward -n staging svc/frontend 3000:3000"
    echo ""

else
    echo -e "${RED}ERROR: Invalid deployment type: $DEPLOYMENT_TYPE${NC}"
    echo "Usage: $0 [local|minikube]"
    exit 1
fi

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Verification Summary                 ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "  ${GREEN}Passed:   $PASSED${NC}"
echo -e "  ${RED}Failed:   $FAILED${NC}"
echo -e "  ${YELLOW}Warnings: $WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next Steps:"
    if [ "$DEPLOYMENT_TYPE" = "local" ]; then
        echo "  1. Start backend:  cd backend && uvicorn app.main:app --reload --port 8000"
        echo "  2. Start frontend: cd frontend && npm run dev"
        echo "  3. Open browser:   http://localhost:3000"
    else
        echo "  1. Access services: minikube service list -n staging"
        echo "  2. Open dashboard:  minikube dashboard"
        echo "  3. Test endpoints:  kubectl port-forward -n staging svc/backend-api 8000:8000"
    fi
    exit 0
else
    echo -e "${RED}✗ Some checks failed${NC}"
    echo ""
    echo "Troubleshooting:"
    if [ "$DEPLOYMENT_TYPE" = "local" ]; then
        echo "  1. Check Docker:   docker ps"
        echo "  2. View logs:      docker compose -f infrastructure/docker-compose.dev.yml logs"
        echo "  3. Restart:        docker compose -f infrastructure/docker-compose.dev.yml restart"
    else
        echo "  1. Check pods:     kubectl get pods -n staging"
        echo "  2. Describe pod:   kubectl describe pod <pod-name> -n staging"
        echo "  3. View logs:      kubectl logs <pod-name> -n staging"
    fi
    exit 1
fi
