#!/bin/bash
# Deploy Dapr Runtime to Oracle OKE
# This script deploys Dapr runtime with custom components

set -e

echo "=== Deploying Dapr Runtime to Oracle OKE ==="
echo ""

# Check if kubectl is configured
if ! kubectl cluster-info >/dev/null 2>&1; then
    echo "❌ kubectl is not configured or cluster is not accessible"
    echo "Please run ./configure-oke.sh first"
    exit 1
fi

# Check if Helm is installed
command -v helm >/dev/null 2>&1 || { echo "❌ Helm is not installed. Please install Helm first."; exit 1; }

echo "✅ Prerequisites check passed"
echo ""

# Add Dapr Helm repository
echo "📦 Adding Dapr Helm repository..."
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

# Create dapr-system namespace
echo "🔧 Creating dapr-system namespace..."
kubectl create namespace dapr-system --dry-run=client -o yaml | kubectl apply -f -

# Install Dapr runtime
echo "🚀 Installing Dapr runtime..."
helm upgrade --install dapr dapr/dapr \
    --namespace dapr-system \
    --set global.ha.enabled=true \
    --set global.ha.replicaCount=3 \
    --set global.mtls.enabled=true \
    --set global.prometheus.enabled=true \
    --set global.prometheus.port=9090 \
    --wait --timeout=10m

echo "✅ Dapr runtime installed successfully"
echo ""

# Wait for Dapr components to be ready
echo "⏳ Waiting for Dapr components to be ready..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/dapr-operator \
    deployment/dapr-sentry \
    deployment/dapr-sidecar-injector \
    deployment/dapr-placement-server \
    --namespace=dapr-system

echo "✅ All Dapr components are ready"
echo ""

# Deploy custom Dapr components
echo "🔧 Deploying custom Dapr components..."

# Create default namespace if it doesn't exist
kubectl create namespace default --dry-run=client -o yaml | kubectl apply -f -

# Deploy Pub/Sub component
echo "  - Deploying Pub/Sub component (Redpanda)..."
kubectl apply -f ../dapr/pubsub-redpanda.yaml

# Deploy State Store component
echo "  - Deploying State Store component (Redis)..."
kubectl apply -f ../dapr/statestore-redis.yaml

# Deploy Bindings component
echo "  - Deploying Bindings component (Cron)..."
kubectl apply -f ../dapr/bindings-cron-prod.yaml

# Deploy Configuration
echo "  - Deploying Dapr configuration..."
kubectl apply -f ../dapr/config.yaml

echo "✅ Custom Dapr components deployed successfully"
echo ""

# Verify Dapr installation
echo "🔍 Verifying Dapr installation..."
dapr_version=$(kubectl get deployment dapr-operator -n dapr-system -o jsonpath='{.spec.template.spec.containers[0].image}' | cut -d: -f2)
echo "Dapr version: $dapr_version"
echo ""

# List Dapr components
echo "📋 Dapr components:"
kubectl get components -n default
echo ""

# Show Dapr system pods
echo "📋 Dapr system pods:"
kubectl get pods -n dapr-system
echo ""

echo "=== Dapr Deployment Complete ==="
echo ""
echo "To verify Dapr is working:"
echo "  kubectl get pods -n dapr-system"
echo "  kubectl get components -n default"
echo ""
echo "To check Dapr logs:"
echo "  kubectl logs -l app=dapr-operator -n dapr-system"
