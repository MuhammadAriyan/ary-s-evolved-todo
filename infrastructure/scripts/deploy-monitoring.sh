#!/bin/bash
# Deploy Prometheus and Grafana to Oracle OKE
# This script deploys monitoring stack to the cluster

set -e

echo "=== Deploying Prometheus and Grafana to Oracle OKE ==="
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

# Add Helm repositories
echo "📦 Adding Helm repositories..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Create monitoring namespace
echo "🔧 Creating monitoring namespace..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Deploy Prometheus
echo "🚀 Deploying Prometheus..."
helm upgrade --install prometheus prometheus-community/prometheus \
    --namespace monitoring \
    --values ../helm/prometheus/values.yaml \
    --wait --timeout=10m

echo "✅ Prometheus deployed successfully"
echo ""

# Wait for Prometheus to be ready
echo "⏳ Waiting for Prometheus to be ready..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/prometheus-server \
    --namespace=monitoring

echo "✅ Prometheus is ready"
echo ""

# Deploy Grafana
echo "🚀 Deploying Grafana..."
helm upgrade --install grafana grafana/grafana \
    --namespace monitoring \
    --values ../helm/grafana/values.yaml \
    --wait --timeout=10m

echo "✅ Grafana deployed successfully"
echo ""

# Wait for Grafana to be ready
echo "⏳ Waiting for Grafana to be ready..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/grafana \
    --namespace=monitoring

echo "✅ Grafana is ready"
echo ""

# Get Grafana admin password
echo "🔑 Grafana Admin Credentials:"
echo "Username: admin"
echo "Password: $(kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode)"
echo ""

# Show monitoring stack status
echo "📋 Monitoring Stack Status:"
kubectl get pods -n monitoring
echo ""
kubectl get services -n monitoring
echo ""
kubectl get ingress -n monitoring
echo ""

# Deploy alert rules
echo "🔧 Deploying Prometheus alert rules..."
kubectl apply -f ../monitoring/alerts.yaml

echo "✅ Alert rules deployed"
echo ""

# Deploy Grafana dashboards
echo "🔧 Deploying Grafana dashboards..."
for dashboard in ../monitoring/grafana-dashboards/*.json; do
    dashboard_name=$(basename "$dashboard" .json)
    echo "  - Deploying dashboard: $dashboard_name"
    kubectl create configmap "grafana-dashboard-$dashboard_name" \
        --from-file="$dashboard" \
        --namespace=monitoring \
        --dry-run=client -o yaml | kubectl apply -f -
    kubectl label configmap "grafana-dashboard-$dashboard_name" \
        grafana_dashboard=1 \
        --namespace=monitoring \
        --overwrite
done

echo "✅ Grafana dashboards deployed"
echo ""

echo "=== Monitoring Deployment Complete ==="
echo ""
echo "Access Prometheus:"
echo "  kubectl port-forward -n monitoring svc/prometheus-server 9090:80"
echo "  Then open: http://localhost:9090"
echo ""
echo "Access Grafana:"
echo "  kubectl port-forward -n monitoring svc/grafana 3000:80"
echo "  Then open: http://localhost:3000"
echo ""
echo "Or access via Ingress (if configured):"
echo "  Prometheus: https://prometheus.todo.example.com"
echo "  Grafana: https://grafana.todo.example.com"
