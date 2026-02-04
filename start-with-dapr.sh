#!/bin/bash
# Start Backend and Frontend with Dapr (Mandatory)
#
# Prerequisites:
# 1. Install Dapr CLI (requires sudo):
#    wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | sudo /bin/bash
# 2. Initialize Dapr:
#    dapr init
# 3. Verify Dapr is running:
#    dapr --version

set -e

echo "=== Starting Ary's Evolved Todo with Dapr ==="
echo ""

# Check if Dapr CLI is installed
if ! command -v dapr &> /dev/null; then
    echo "❌ ERROR: Dapr CLI is not installed!"
    echo ""
    echo "To install Dapr CLI, run:"
    echo "  wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | sudo /bin/bash"
    echo ""
    echo "Then initialize Dapr:"
    echo "  dapr init"
    echo ""
    exit 1
fi

# Check if Dapr is initialized
if ! dapr --version &> /dev/null; then
    echo "❌ ERROR: Dapr is not initialized!"
    echo ""
    echo "To initialize Dapr, run:"
    echo "  dapr init"
    echo ""
    exit 1
fi

echo "✅ Dapr CLI is installed and initialized"
echo ""

# Start infrastructure services
echo "Starting infrastructure services..."
cd "$(dirname "$0")"
docker-compose -f infrastructure/docker-compose.yml up -d

echo "Waiting for services to be healthy..."
sleep 10

# Start backend with Dapr
echo ""
echo "Starting backend with Dapr sidecar..."
cd backend
source venv/bin/activate

dapr run \
  --app-id backend-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --components-path ../infrastructure/dapr \
  --log-level info \
  -- uvicorn app.main:app --host 0.0.0.0 --port 8000 &

BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Start frontend
echo ""
echo "Starting frontend..."
cd ../frontend
npm run dev &

FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

echo ""
echo "=== Services Started ==="
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "Backend Health: http://localhost:8000/health"
echo "Dapr Dashboard: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; docker-compose -f infrastructure/docker-compose.yml down; exit 0" INT TERM

wait
