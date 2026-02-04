#!/bin/bash
# Start Recurring Task Service with Dapr sidecar
# T119: Start Recurring Task Service with Dapr sidecar and verify Pub/Sub subscription

set -e

echo "Starting Recurring Task Service with Dapr..."

# Check if Dapr is installed
if ! command -v dapr &> /dev/null; then
    echo "Error: Dapr CLI is not installed. Please install Dapr first."
    echo "Visit: https://docs.dapr.io/getting-started/install-dapr-cli/"
    exit 1
fi

# Set environment variables
export BACKEND_API_URL="${BACKEND_API_URL:-http://localhost:8000}"
export DAPR_HTTP_PORT=3503
export DAPR_GRPC_PORT=50053

# Navigate to the recurring task service directory
cd "$(dirname "$0")/../backend/microservices/recurring_task"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start the service with Dapr
echo "Starting Recurring Task Service on port 8003..."
echo "Dapr HTTP port: $DAPR_HTTP_PORT"
echo "Dapr gRPC port: $DAPR_GRPC_PORT"

dapr run \
    --app-id recurring-task-service \
    --app-port 8003 \
    --dapr-http-port $DAPR_HTTP_PORT \
    --dapr-grpc-port $DAPR_GRPC_PORT \
    --components-path ../../../infrastructure/dapr \
    --log-level info \
    -- python main.py

echo "Recurring Task Service stopped."
