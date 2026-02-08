#!/bin/bash
# Oracle OKE Cluster Configuration Script
# This script configures kubectl to connect to Oracle OKE cluster

set -e

echo "=== Oracle OKE Cluster Configuration ==="
echo ""

# Check if required tools are installed
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl is not installed. Please install kubectl first."; exit 1; }
command -v oci >/dev/null 2>&1 || { echo "❌ OCI CLI is not installed. Please install OCI CLI first."; exit 1; }

# Configuration variables
CLUSTER_NAME="${OKE_CLUSTER_NAME:-todo-oke-cluster}"
REGION="${OCI_REGION:-us-ashburn-1}"
COMPARTMENT_ID="${OCI_COMPARTMENT_ID}"

if [ -z "$COMPARTMENT_ID" ]; then
    echo "❌ OCI_COMPARTMENT_ID environment variable is not set"
    echo "Please set it to your Oracle Cloud compartment OCID"
    exit 1
fi

echo "Cluster Name: $CLUSTER_NAME"
echo "Region: $REGION"
echo "Compartment ID: $COMPARTMENT_ID"
echo ""

# Get cluster OCID
echo "📡 Fetching cluster information..."
CLUSTER_ID=$(oci ce cluster list \
    --compartment-id "$COMPARTMENT_ID" \
    --name "$CLUSTER_NAME" \
    --region "$REGION" \
    --query 'data[0].id' \
    --raw-output 2>/dev/null)

if [ -z "$CLUSTER_ID" ] || [ "$CLUSTER_ID" == "null" ]; then
    echo "❌ Cluster '$CLUSTER_NAME' not found in compartment"
    echo ""
    echo "Available clusters:"
    oci ce cluster list --compartment-id "$COMPARTMENT_ID" --region "$REGION" --query 'data[*].name' --output table
    exit 1
fi

echo "✅ Found cluster: $CLUSTER_ID"
echo ""

# Generate kubeconfig
echo "🔧 Generating kubeconfig..."
mkdir -p ~/.kube
oci ce cluster create-kubeconfig \
    --cluster-id "$CLUSTER_ID" \
    --file ~/.kube/config-oke \
    --region "$REGION" \
    --token-version 2.0.0 \
    --kube-endpoint PUBLIC_ENDPOINT

# Merge with existing kubeconfig
if [ -f ~/.kube/config ]; then
    echo "📝 Backing up existing kubeconfig..."
    cp ~/.kube/config ~/.kube/config.backup.$(date +%Y%m%d_%H%M%S)

    echo "🔀 Merging kubeconfig files..."
    KUBECONFIG=~/.kube/config:~/.kube/config-oke kubectl config view --flatten > ~/.kube/config.merged
    mv ~/.kube/config.merged ~/.kube/config
    rm ~/.kube/config-oke
else
    mv ~/.kube/config-oke ~/.kube/config
fi

# Set current context
CONTEXT_NAME="context-$(echo $CLUSTER_ID | cut -d. -f5)"
kubectl config use-context "$CONTEXT_NAME"

echo "✅ Kubeconfig configured successfully"
echo ""

# Verify connection
echo "🔍 Verifying cluster connection..."
if kubectl cluster-info >/dev/null 2>&1; then
    echo "✅ Successfully connected to cluster"
    echo ""
    kubectl cluster-info
    echo ""
    kubectl get nodes
else
    echo "❌ Failed to connect to cluster"
    exit 1
fi

echo ""
echo "=== Configuration Complete ==="
echo ""
echo "Current context: $(kubectl config current-context)"
echo ""
echo "To switch contexts later, use:"
echo "  kubectl config use-context $CONTEXT_NAME"
echo ""
echo "To view all contexts:"
echo "  kubectl config get-contexts"
