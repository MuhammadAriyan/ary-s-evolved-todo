#!/bin/bash
# Deploy staging environment locally using Docker Compose
# Usage: ./scripts/deploy-staging-local.sh

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
echo -e "${BLUE}  Staging Deployment - Docker Compose  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Check Docker is running
echo -e "${YELLOW}[1/8] Checking Docker daemon...${NC}"
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Docker daemon is not running${NC}"
    echo ""
    echo "Please start Docker:"
    echo "  - Docker Desktop: Launch from applications menu"
    echo "  - Docker Engine: sudo systemctl start docker"
    echo ""
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Step 2: Check Docker Compose
echo -e "${YELLOW}[2/8] Checking Docker Compose...${NC}"
if ! docker compose version > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose is available${NC}"
echo ""

# Step 3: Create .env file if not exists
echo -e "${YELLOW}[3/8] Setting up environment variables...${NC}"
if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
    echo "Creating backend/.env from .env.example..."
    cp "$PROJECT_ROOT/backend/.env.example" "$PROJECT_ROOT/backend/.env"
    echo -e "${GREEN}✓ Created backend/.env${NC}"
else
    echo -e "${GREEN}✓ backend/.env already exists${NC}"
fi

if [ ! -f "$PROJECT_ROOT/frontend/.env.local" ]; then
    if [ -f "$PROJECT_ROOT/frontend/.env.example" ]; then
        echo "Creating frontend/.env.local from .env.example..."
        cp "$PROJECT_ROOT/frontend/.env.example" "$PROJECT_ROOT/frontend/.env.local"
        echo -e "${GREEN}✓ Created frontend/.env.local${NC}"
    else
        echo -e "${YELLOW}⚠ frontend/.env.example not found, skipping${NC}"
    fi
else
    echo -e "${GREEN}✓ frontend/.env.local already exists${NC}"
fi
echo ""

# Step 4: Stop any existing containers
echo -e "${YELLOW}[4/8] Stopping existing containers...${NC}"
cd "$PROJECT_ROOT/infrastructure"
docker compose -f docker-compose.dev.yml down > /dev/null 2>&1 || true
echo -e "${GREEN}✓ Cleaned up existing containers${NC}"
echo ""

# Step 5: Pull latest images
echo -e "${YELLOW}[5/8] Pulling Docker images...${NC}"
docker compose -f docker-compose.dev.yml pull --quiet
echo -e "${GREEN}✓ Images pulled${NC}"
echo ""

# Step 6: Start infrastructure services
echo -e "${YELLOW}[6/8] Starting infrastructure services...${NC}"
echo "  - PostgreSQL (database)"
echo "  - Redis (state store)"
echo "  - Redpanda (event streaming)"
echo "  - Dapr Placement Service"
echo ""
docker compose -f docker-compose.dev.yml up -d postgres redis redpanda dapr-placement

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 5

# Check PostgreSQL
echo -n "  PostgreSQL: "
for i in {1..30}; do
    if docker exec todo-postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Timeout${NC}"
        exit 1
    fi
    sleep 1
done

# Check Redis
echo -n "  Redis: "
for i in {1..30}; do
    if docker exec todo-redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Timeout${NC}"
        exit 1
    fi
    sleep 1
done

# Check Redpanda
echo -n "  Redpanda: "
for i in {1..60}; do
    if docker exec todo-redpanda rpk cluster health 2>/dev/null | grep -q "Healthy.*true"; then
        echo -e "${GREEN}✓ Ready${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}✗ Timeout (may still be starting)${NC}"
    fi
    sleep 2
done

echo -e "${GREEN}✓ Infrastructure services started${NC}"
echo ""

# Step 7: Build and start application services
echo -e "${YELLOW}[7/8] Building and starting application services...${NC}"
echo "This may take a few minutes on first run..."
echo ""

# Note: We're only starting infrastructure for now
# Application services would need proper Dockerfiles in the right locations
echo -e "${YELLOW}Note: Application services (backend, frontend, microservices) need to be started separately${NC}"
echo "You can start them with:"
echo "  Backend: cd backend && uvicorn app.main:app --reload --port 8000"
echo "  Frontend: cd frontend && npm run dev"
echo ""

# Step 8: Display access information
echo -e "${YELLOW}[8/8] Deployment Summary${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Staging Environment Ready!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Infrastructure Services:"
echo "  PostgreSQL:        localhost:5432"
echo "  Redis:             localhost:6379"
echo "  Redpanda (Kafka):  localhost:19092"
echo "  Redpanda Console:  http://localhost:8080"
echo "  Dapr Placement:    localhost:50006"
echo ""
echo "Application Services (start manually):"
echo "  Backend API:       http://localhost:8000"
echo "  API Docs:          http://localhost:8000/docs"
echo "  Frontend:          http://localhost:3000"
echo ""
echo "Useful Commands:"
echo "  View logs:         docker compose -f infrastructure/docker-compose.dev.yml logs -f"
echo "  Stop services:     docker compose -f infrastructure/docker-compose.dev.yml down"
echo "  Restart service:   docker compose -f infrastructure/docker-compose.dev.yml restart <service>"
echo ""
echo "Next Steps:"
echo "  1. Start backend:  cd backend && uvicorn app.main:app --reload --port 8000"
echo "  2. Start frontend: cd frontend && npm run dev"
echo "  3. Verify:         ./scripts/verify-deployment.sh local"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
