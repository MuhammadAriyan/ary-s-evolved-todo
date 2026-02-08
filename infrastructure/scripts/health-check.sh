#!/bin/bash
# Health check script for all microservices
# Usage: ./health-check.sh [namespace]

set -e

NAMESPACE=${1:-todo-app}

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Check if namespace exists
check_namespace() {
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_error "Namespace $NAMESPACE does not exist."
        exit 1
    fi
}

# Check deployment status
check_deployments() {
    log_header "Checking Deployments"

    DEPLOYMENTS=$(kubectl get deployments -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

    if [ -z "$DEPLOYMENTS" ]; then
        log_warn "No deployments found in namespace $NAMESPACE"
        return
    fi

    for deployment in $DEPLOYMENTS; do
        READY=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')
        DESIRED=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')

        if [ "$READY" == "$DESIRED" ]; then
            log_info "✓ $deployment: $READY/$DESIRED replicas ready"
        else
            log_error "✗ $deployment: $READY/$DESIRED replicas ready"
        fi
    done
}

# Check pod status
check_pods() {
    log_header "Checking Pods"

    kubectl get pods -n "$NAMESPACE" -o wide

    echo ""
    FAILED_PODS=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running,status.phase!=Succeeded -o jsonpath='{.items[*].metadata.name}')

    if [ -n "$FAILED_PODS" ]; then
        log_error "Failed pods detected: $FAILED_PODS"
        for pod in $FAILED_PODS; do
            log_error "Logs for $pod:"
            kubectl logs "$pod" -n "$NAMESPACE" --tail=20
        done
    else
        log_info "All pods are running successfully."
    fi
}

# Check services
check_services() {
    log_header "Checking Services"
    kubectl get svc -n "$NAMESPACE"
}

# Check HPA status
check_hpa() {
    log_header "Checking Horizontal Pod Autoscalers"

    HPAS=$(kubectl get hpa -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

    if [ -z "$HPAS" ]; then
        log_warn "No HPAs found in namespace $NAMESPACE"
        return
    fi

    kubectl get hpa -n "$NAMESPACE"
}

# Check resource usage
check_resources() {
    log_header "Checking Resource Usage"

    log_info "CPU and Memory usage by pod:"
    kubectl top pods -n "$NAMESPACE" 2>/dev/null || log_warn "Metrics server not available"
}

# Check Dapr sidecars
check_dapr() {
    log_header "Checking Dapr Sidecars"

    PODS=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}')

    for pod in $PODS; do
        DAPR_SIDECAR=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.spec.containers[?(@.name=="daprd")].name}')

        if [ -n "$DAPR_SIDECAR" ]; then
            log_info "✓ $pod has Dapr sidecar"
        else
            log_warn "✗ $pod missing Dapr sidecar"
        fi
    done
}

# Check endpoints health
check_endpoints() {
    log_header "Checking Service Endpoints"

    SERVICES=("audit" "search-indexer" "dlq-handler" "recurring-task")

    for service in "${SERVICES[@]}"; do
        ENDPOINT=$(kubectl get svc "$service" -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}' 2>/dev/null)
        PORT=$(kubectl get svc "$service" -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].port}' 2>/dev/null)

        if [ -n "$ENDPOINT" ] && [ -n "$PORT" ]; then
            log_info "Testing $service at $ENDPOINT:$PORT/health"

            # Create a test pod to check endpoint
            kubectl run health-check-temp --image=curlimages/curl:latest --rm -i --restart=Never -n "$NAMESPACE" -- \
                curl -s -o /dev/null -w "%{http_code}" "http://$ENDPOINT:$PORT/health" 2>/dev/null || log_warn "Could not reach $service endpoint"
        else
            log_warn "Service $service not found"
        fi
    done
}

# Generate health report
generate_report() {
    log_header "Health Check Summary"

    TOTAL_PODS=$(kubectl get pods -n "$NAMESPACE" --no-headers | wc -l)
    RUNNING_PODS=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase=Running --no-headers | wc -l)
    FAILED_PODS=$(kubectl get pods -n "$NAMESPACE" --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers | wc -l)

    echo "Total Pods: $TOTAL_PODS"
    echo "Running Pods: $RUNNING_PODS"
    echo "Failed Pods: $FAILED_PODS"

    if [ "$FAILED_PODS" -eq 0 ]; then
        log_info "✓ All systems operational"
        return 0
    else
        log_error "✗ System health check failed"
        return 1
    fi
}

# Main execution
main() {
    log_info "Starting health check for namespace: $NAMESPACE"

    check_namespace
    check_deployments
    check_pods
    check_services
    check_hpa
    check_resources
    check_dapr
    check_endpoints
    generate_report
}

main
