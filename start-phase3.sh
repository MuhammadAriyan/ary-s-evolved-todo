#!/bin/bash
# Phase 3 Quick Start Script
# Starts all services required for real-time task synchronization

set -e

echo "🚀 Starting Phase 3: Real-Time Task Synchronization"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose found${NC}"

# Check Dapr CLI
if ! command -v dapr &> /dev/null; then
    echo -e "${RED}❌ Dapr CLI not found. Please install Dapr CLI first.${NC}"
    echo "   Install: https://docs.dapr.io/getting-started/install-dapr-cli/"
    exit 1
fi
echo -e "${GREEN}✅ Dapr CLI found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3 first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

echo ""
echo "🐳 Starting infrastructure services..."
cd infrastructure
docker-compose -f docker-compose.dev.yml up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose -f docker-compose.dev.yml ps

echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo ""
echo "1. Start Backend API with Dapr:"
echo "   cd backend"
echo "   dapr run --app-id backend-api --app-port 8000 --dapr-http-port 3500 --dapr-grpc-port 50001 --components-path ../infrastructure/dapr -- uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "2. Start WebSocket Sync Service with Dapr (in new terminal):"
echo "   cd backend/microservices/websocket_sync"
echo "   dapr run --app-id websocket-sync --app-port 8001 --dapr-http-port 3501 --dapr-grpc-port 50002 --components-path ../../../infrastructure/dapr -- uvicorn main:app --host 0.0.0.0 --port 8001 --reload"
echo ""
echo "3. Start Frontend (in new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open browser and test:"
echo "   http://localhost:3000"
echo ""
echo -e "${GREEN}✅ Infrastructure services started successfully!${NC}"
echo ""
echo "📊 Service URLs:"
echo "   - Redpanda Console: http://localhost:8080"
echo "   - Backend API: http://localhost:8000"
echo "   - WebSocket Service: http://localhost:8001"
echo "   - Frontend: http://localhost:3000"
echo ""
echo "📖 For detailed testing instructions, see PHASE3_TESTING_GUIDE.md"
