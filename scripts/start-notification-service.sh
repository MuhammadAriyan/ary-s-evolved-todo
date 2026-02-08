#!/bin/bash
# Start Notification Service with Dapr Sidecar
# T074: Start Notification Service with Dapr sidecar and verify Bindings subscription

set -e

echo "🚀 Starting Notification Service with Dapr..."

# Check if Dapr is installed
if ! command -v dapr &> /dev/null; then
    echo "❌ Dapr CLI not found. Please install Dapr first:"
    echo "   https://docs.dapr.io/getting-started/install-dapr-cli/"
    exit 1
fi

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set, using default from .env"
fi

if [ -z "$SENDGRID_API_KEY" ]; then
    echo "⚠️  SENDGRID_API_KEY not set - email notifications will be disabled"
fi

# Navigate to notification service directory
cd "$(dirname "$0")/../backend/microservices/notification"

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

echo "📦 Installing dependencies..."
source .venv/bin/activate
pip install -q -r requirements.txt

# Start the service with Dapr
echo "🎯 Starting Notification Service on port 8002..."
echo "📡 Dapr sidecar will run on HTTP port 3500, gRPC port 50001"
echo ""

dapr run \
    --app-id notification-service \
    --app-port 8002 \
    --dapr-http-port 3500 \
    --dapr-grpc-port 50001 \
    --components-path ../../../infrastructure/dapr \
    --log-level info \
    -- python main.py

echo ""
echo "✅ Notification Service stopped"
