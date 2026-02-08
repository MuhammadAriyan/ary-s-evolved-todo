#!/bin/bash
# Deploy all microservices to Kubernetes cluster
# Usage: ./deploy-microservices.sh [environment]

set -e

ENVIRONMENT=${1:-production}
NAMESPACE="todo-app"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELM_DIR="$(dirname "$SCRIPT_DIR")/helm"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi

    if ! command -v helm &> /dev/null; then
        log_error "helm not found. Please install Helm."
        exit 1
    fi

    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster."
        exit 1
    fi

    log_info "Prerequisites check passed."
}

# Create namespace if it doesn't exist
create_namespace() {
    log_info "Creating namespace: $NAMESPACE"
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    kubectl label namespace $NAMESPACE istio-injection=enabled --overwrite
}

# Deploy a microservice using Helm
deploy_service() {
    local service_name=$1
    local chart_path="$HELM_DIR/$service_name"

    log_info "Deploying $service_name..."

    if [ ! -d "$chart_path" ]; then
        log_error "Helm chart not found: $chart_path"
        return 1
    fi

    helm upgrade --install "$service_name" "$chart_path" \
        --namespace "$NAMESPACE" \
        --create-namespace \
        --wait \
        --timeout 5m \
        --set image.tag="${IMAGE_TAG:-latest}" \
        --set environment="$ENVIRONMENT"

    if [ $? -eq 0 ]; then
        log_info "$service_name deployed successfully."
    else
        log_error "Failed to deploy $service_name."
        return 1
    fi
}

# Wait for deployment to be ready
wait_for_deployment() {
    local deployment_name=$1
    log_info "Waiting for $deployment_name to be ready..."
    kubectl rollout status deployment/"$deployment_name" -n "$NAMESPACE" --timeout=5m
}

# Main deployment flow
main() {
    log_info "Starting microservices deployment to $ENVIRONMENT environment..."

    check_prerequisites
    create_namespace

    # Deploy microservices in order
    SERVICES=(
        "audit"
        "search-indexer"
        "dlq-handler"
        "recurring-task"
    )

    for service in "${SERVICES[@]}"; do
        deploy_service "$service"
        wait_for_deployment "$service"
    done

    log_info "All microservices deployed successfully!"
    log_info "Checking pod status..."
    kubectl get pods -n "$NAMESPACE"

    log_info "Checking services..."
    kubectl get svc -n "$NAMESPACE"
}

# Run main function
main
