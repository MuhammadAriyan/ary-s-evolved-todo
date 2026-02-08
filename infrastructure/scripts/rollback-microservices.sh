#!/bin/bash
# Rollback microservices deployment
# Usage: ./rollback-microservices.sh <service-name> [revision]

set -e

SERVICE_NAME=$1
REVISION=${2:-0}  # 0 means previous revision
NAMESPACE="todo-app"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Validate input
if [ -z "$SERVICE_NAME" ]; then
    log_error "Usage: $0 <service-name> [revision]"
    log_info "Available services: audit, search-indexer, dlq-handler, recurring-task"
    exit 1
fi

# Check if service exists
check_service() {
    log_info "Checking if service $SERVICE_NAME exists..."
    if ! helm list -n "$NAMESPACE" | grep -q "$SERVICE_NAME"; then
        log_error "Service $SERVICE_NAME not found in namespace $NAMESPACE"
        exit 1
    fi
}

# Show release history
show_history() {
    log_info "Release history for $SERVICE_NAME:"
    helm history "$SERVICE_NAME" -n "$NAMESPACE"
}

# Perform rollback
rollback_service() {
    log_warn "Rolling back $SERVICE_NAME to revision $REVISION..."

    if [ "$REVISION" -eq 0 ]; then
        helm rollback "$SERVICE_NAME" -n "$NAMESPACE" --wait --timeout 5m
    else
        helm rollback "$SERVICE_NAME" "$REVISION" -n "$NAMESPACE" --wait --timeout 5m
    fi

    if [ $? -eq 0 ]; then
        log_info "Rollback completed successfully."
    else
        log_error "Rollback failed!"
        exit 1
    fi
}

# Verify rollback
verify_rollback() {
    log_info "Verifying rollback..."
    kubectl rollout status deployment/"$SERVICE_NAME" -n "$NAMESPACE" --timeout=5m

    log_info "Current pod status:"
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name="$SERVICE_NAME"
}

# Main execution
main() {
    log_info "Starting rollback process for $SERVICE_NAME..."

    check_service
    show_history

    # Ask for confirmation
    read -p "Do you want to proceed with rollback? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_warn "Rollback cancelled."
        exit 0
    fi

    rollback_service
    verify_rollback

    log_info "Rollback completed successfully!"
}

main
