# Oracle Cloud Infrastructure (OCI) Deployment Guide - Phase 5

Complete guide for deploying the event-driven microservices Todo application to Oracle Cloud Infrastructure with Kubernetes (OKE).

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [OCI Setup](#oci-setup)
3. [OKE Cluster Creation](#oke-cluster-creation)
4. [Database Setup (Autonomous Database)](#database-setup)
5. [Container Registry](#container-registry)
6. [Dapr Installation](#dapr-installation)
7. [Application Deployment](#application-deployment)
8. [Monitoring Setup](#monitoring-setup)
9. [Production Checklist](#production-checklist)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
```bash
# Install OCI CLI
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

### OCI Account Requirements
- Active OCI account with credits or subscription
- Compartment with appropriate permissions
- VCN (Virtual Cloud Network) configured
- IAM policies for OKE and container registry

---

## OCI Setup

### 1. Configure OCI CLI
```bash
# Run OCI CLI configuration
oci setup config

# Test configuration
oci iam region list
```

### 2. Set Environment Variables
```bash
export OCI_COMPARTMENT_ID="ocid1.compartment.oc1..xxx"
export OCI_REGION="us-ashburn-1"
export OCI_TENANCY_ID="ocid1.tenancy.oc1..xxx"
export OCI_USER_ID="ocid1.user.oc1..xxx"
```

### 3. Create Compartment (Optional)
```bash
oci iam compartment create \
  --compartment-id $OCI_TENANCY_ID \
  --name "todo-app-prod" \
  --description "Production environment for Todo App"
```

---

## OKE Cluster Creation

### Option 1: Quick Create (Recommended for Testing)
```bash
# Create OKE cluster with default settings
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region $OCI_REGION \
  --token-version 2.0.0
```

### Option 2: Custom Create (Production)
```bash
# Create VCN first
oci network vcn create \
  --compartment-id $OCI_COMPARTMENT_ID \
  --cidr-block "10.0.0.0/16" \
  --display-name "todo-app-vcn"

# Create OKE cluster
oci ce cluster create \
  --compartment-id $OCI_COMPARTMENT_ID \
  --name "todo-app-cluster" \
  --kubernetes-version "v1.28.2" \
  --vcn-id <vcn-ocid> \
  --service-lb-subnet-ids '["<subnet-ocid>"]'
```

### Configure kubectl
```bash
# Download kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <cluster-ocid> \
  --file $HOME/.kube/config \
  --region $OCI_REGION \
  --token-version 2.0.0 \
  --kube-endpoint PUBLIC_ENDPOINT

# Verify connection
kubectl get nodes
kubectl cluster-info
```

---

## Database Setup

### Option 1: Autonomous Database (Recommended)
```bash
# Create Autonomous Database
oci db autonomous-database create \
  --compartment-id $OCI_COMPARTMENT_ID \
  --db-name "tododb" \
  --display-name "Todo App Database" \
  --admin-password "<strong-password>" \
  --cpu-core-count 1 \
  --data-storage-size-in-tbs 1 \
  --db-workload "OLTP"

# Download wallet
oci db autonomous-database generate-wallet \
  --autonomous-database-id <adb-ocid> \
  --file wallet.zip \
  --password "<wallet-password>"

# Extract wallet
unzip wallet.zip -d wallet/
```

### Create Kubernetes Secret for Database
```bash
# Create secret from wallet
kubectl create secret generic adb-wallet \
  --from-file=wallet/ \
  --namespace=default

# Create database URL secret
kubectl create secret generic database-credentials \
  --from-literal=DATABASE_URL="postgresql://admin:<password>@<adb-host>:1522/tododb?sslmode=require" \
  --namespace=default
```

### Option 2: PostgreSQL on Compute Instance
```bash
# Create compute instance
oci compute instance launch \
  --compartment-id $OCI_COMPARTMENT_ID \
  --availability-domain "<AD-name>" \
  --shape "VM.Standard.E4.Flex" \
  --shape-config '{"ocpus":1,"memoryInGBs":8}' \
  --image-id <ubuntu-image-ocid> \
  --subnet-id <subnet-ocid> \
  --display-name "postgres-server"

# SSH and install PostgreSQL
ssh ubuntu@<instance-ip>
sudo apt update && sudo apt install -y postgresql-14
```

---

## Container Registry

### 1. Create OCIR Repository
```bash
# Login to OCIR
docker login <region-key>.ocir.io -u '<tenancy-namespace>/<username>' -p '<auth-token>'

# Example for Ashburn region
docker login iad.ocir.io -u 'mytenancy/oracleidentitycloudservice/user@example.com' -p '<auth-token>'
```

### 2. Build and Push Images
```bash
# Set registry variables
export OCIR_REGION="iad"
export OCIR_TENANCY="mytenancy"
export OCIR_REPO="todo-app"

# Build backend
cd backend
docker build -t ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/backend:latest .
docker push ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/backend:latest

# Build frontend
cd ../frontend
docker build -t ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/frontend:latest .
docker push ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/frontend:latest

# Build microservices
cd ../backend/microservices

# Audit service
docker build -t ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/audit:latest -f audit/Dockerfile .
docker push ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/audit:latest

# Notification service
docker build -t ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/notification:latest -f notification/Dockerfile .
docker push ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/notification:latest

# Recurring task service
docker build -t ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/recurring-task:latest -f recurring_task/Dockerfile .
docker push ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/recurring-task:latest

# WebSocket sync service
docker build -t ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/websocket-sync:latest -f websocket_sync/Dockerfile .
docker push ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/websocket-sync:latest
```

### 3. Create Image Pull Secret
```bash
kubectl create secret docker-registry ocir-secret \
  --docker-server=${OCIR_REGION}.ocir.io \
  --docker-username="${OCIR_TENANCY}/oracleidentitycloudservice/<username>" \
  --docker-password="<auth-token>" \
  --docker-email="<email>" \
  --namespace=default
```

---

## Dapr Installation

### 1. Install Dapr on OKE
```bash
# Initialize Dapr
dapr init -k

# Verify installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
# dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m   2024-02-04 10:00:00
# dapr-sentry            dapr-system  True     Running  1         1.12.0   1m   2024-02-04 10:00:00
# dapr-operator          dapr-system  True     Running  1         1.12.0   1m   2024-02-04 10:00:00
# dapr-placement         dapr-system  True     Running  1         1.12.0   1m   2024-02-04 10:00:00
```

### 2. Install Redis (State Store)
```bash
# Add Bitnami Helm repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Redis
helm install redis bitnami/redis \
  --set auth.enabled=true \
  --set auth.password="<redis-password>" \
  --set master.persistence.enabled=true \
  --set master.persistence.size=10Gi \
  --namespace=default
```

### 3. Install Kafka (Pub/Sub)
```bash
# Install Strimzi Kafka operator
kubectl create namespace kafka
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Create Kafka cluster
cat <<EOF | kubectl apply -f -
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
    storage:
      type: jbod
      volumes:
      - id: 0
        type: persistent-claim
        size: 100Gi
        deleteClaim: false
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 10Gi
      deleteClaim: false
  entityOperator:
    topicOperator: {}
    userOperator: {}
EOF

# Wait for Kafka to be ready
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka
```

### 4. Deploy Dapr Components
```bash
# Apply Dapr components
kubectl apply -f infrastructure/dapr/statestore-redis.yaml
kubectl apply -f infrastructure/dapr/pubsub-kafka.yaml
kubectl apply -f infrastructure/dapr/config.yaml

# Verify components
kubectl get components
```

---

## Application Deployment

### 1. Create Namespace
```bash
kubectl create namespace todo-app
kubectl label namespace todo-app dapr.io/enabled=true
```

### 2. Create Secrets
```bash
# Database credentials
kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_URL="<database-url>" \
  --from-literal=JWT_SECRET_KEY="<jwt-secret>" \
  --from-literal=BETTER_AUTH_SECRET="<auth-secret>" \
  --from-literal=SENDGRID_API_KEY="<sendgrid-key>" \
  --namespace=todo-app

# Frontend secrets
kubectl create secret generic frontend-secrets \
  --from-literal=NEXT_PUBLIC_API_URL="https://api.yourdomain.com" \
  --from-literal=BETTER_AUTH_URL="https://yourdomain.com" \
  --namespace=todo-app
```

### 3. Update Helm Values
```bash
# Edit infrastructure/helm/backend/values.yaml
cat > infrastructure/helm/backend/values-prod.yaml <<EOF
replicaCount: 3

image:
  repository: ${OCIR_REGION}.ocir.io/${OCIR_TENANCY}/${OCIR_REPO}/backend
  tag: latest
  pullPolicy: Always

imagePullSecrets:
  - name: ocir-secret

service:
  type: ClusterIP
  port: 8000

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: api-tls
      hosts:
        - api.yourdomain.com

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

dapr:
  enabled: true
  appId: backend
  appPort: 8000
  config: dapr-config

env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: backend-secrets
        key: DATABASE_URL
  - name: JWT_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: backend-secrets
        key: JWT_SECRET_KEY
  - name: REDIS_HOST
    value: redis-master
  - name: KAFKA_BOOTSTRAP_SERVERS
    value: todo-kafka-kafka-bootstrap.kafka:9092
EOF
```

### 4. Deploy with Helm
```bash
# Deploy backend
helm upgrade --install backend \
  ./infrastructure/helm/backend \
  --values ./infrastructure/helm/backend/values-prod.yaml \
  --namespace=todo-app

# Deploy frontend
helm upgrade --install frontend \
  ./infrastructure/helm/frontend \
  --values ./infrastructure/helm/frontend/values-prod.yaml \
  --namespace=todo-app

# Deploy microservices
helm upgrade --install notification \
  ./infrastructure/helm/notification \
  --namespace=todo-app

helm upgrade --install websocket-sync \
  ./infrastructure/helm/websocket-sync \
  --namespace=todo-app

# Verify deployments
kubectl get pods -n todo-app
kubectl get services -n todo-app
```

### 5. Run Database Migrations
```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pods -n todo-app -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -it $BACKEND_POD -n todo-app -- alembic upgrade head

# Verify tables
kubectl exec -it $BACKEND_POD -n todo-app -- python -c "
from app.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print('Tables:', inspector.get_table_names())
"
```

---

## Monitoring Setup

### 1. Install Prometheus and Grafana
```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace=monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# Verify installation
kubectl get pods -n monitoring
```

### 2. Configure Service Monitors
```bash
# Apply service monitors for application
kubectl apply -f infrastructure/monitoring/service-monitors.yaml -n todo-app

# Verify service monitors
kubectl get servicemonitors -n todo-app
```

### 3. Import Grafana Dashboards
```bash
# Get Grafana admin password
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Access Grafana at http://localhost:3000
# Import dashboards from infrastructure/monitoring/grafana-dashboards/
```

### 4. Configure Alerts
```bash
# Apply alert rules
kubectl apply -f infrastructure/monitoring/alerts.yaml -n monitoring

# Verify alerts
kubectl get prometheusrules -n monitoring
```

---

## Production Checklist

### Security
- [ ] Enable network policies
- [ ] Configure pod security policies
- [ ] Set up RBAC roles and bindings
- [ ] Enable secrets encryption at rest
- [ ] Configure TLS for all services
- [ ] Set up Web Application Firewall (WAF)
- [ ] Enable audit logging
- [ ] Configure security scanning for images

### High Availability
- [ ] Deploy across multiple availability domains
- [ ] Configure pod disruption budgets
- [ ] Set up horizontal pod autoscaling
- [ ] Configure health checks and readiness probes
- [ ] Set up load balancer with health checks
- [ ] Configure backup and disaster recovery

### Performance
- [ ] Configure resource limits and requests
- [ ] Enable caching (Redis)
- [ ] Configure CDN for static assets
- [ ] Optimize database queries and indexes
- [ ] Enable connection pooling
- [ ] Configure rate limiting

### Monitoring
- [ ] Set up Prometheus metrics collection
- [ ] Configure Grafana dashboards
- [ ] Set up alerting rules
- [ ] Configure log aggregation
- [ ] Enable distributed tracing
- [ ] Set up uptime monitoring

### Compliance
- [ ] Enable audit logging
- [ ] Configure data retention policies
- [ ] Set up backup schedules
- [ ] Document incident response procedures
- [ ] Configure compliance scanning

---

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting
```bash
# Check pod status
kubectl get pods -n todo-app

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app

# Common causes:
# - Image pull errors (check OCIR credentials)
# - Resource limits (check node capacity)
# - Configuration errors (check secrets and configmaps)
```

#### 2. Dapr Sidecar Issues
```bash
# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n todo-app

# Verify Dapr components
kubectl get components -n todo-app

# Check Dapr configuration
kubectl get configuration -n todo-app

# Restart pod to reinject sidecar
kubectl delete pod <pod-name> -n todo-app
```

#### 3. Database Connection Errors
```bash
# Test database connectivity from pod
kubectl exec -it <backend-pod> -n todo-app -- bash
psql $DATABASE_URL

# Check database secret
kubectl get secret backend-secrets -n todo-app -o yaml

# Verify network policies allow database access
kubectl get networkpolicies -n todo-app
```

#### 4. Ingress Not Working
```bash
# Check ingress status
kubectl get ingress -n todo-app

# Describe ingress for events
kubectl describe ingress <ingress-name> -n todo-app

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Verify DNS records point to load balancer
nslookup api.yourdomain.com
```

#### 5. Event Delivery Failures
```bash
# Check Kafka topics
kubectl exec -it todo-kafka-kafka-0 -n kafka -- bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Check consumer lag
kubectl exec -it todo-kafka-kafka-0 -n kafka -- bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --all-groups

# Check Dapr pub/sub component
kubectl get component pubsub-kafka -n todo-app -o yaml

# Check microservice logs
kubectl logs -l app=notification -n todo-app
```

### Performance Optimization

#### 1. Database Query Optimization
```bash
# Enable query logging
kubectl exec -it <backend-pod> -n todo-app -- bash
export LOG_LEVEL=DEBUG

# Analyze slow queries
kubectl logs <backend-pod> -n todo-app | grep "slow query"

# Check database indexes
kubectl exec -it <backend-pod> -n todo-app -- python -c "
from app.database import engine
result = engine.execute('SELECT * FROM pg_indexes WHERE schemaname = \'public\'')
for row in result:
    print(row)
"
```

#### 2. Resource Tuning
```bash
# Check resource usage
kubectl top pods -n todo-app
kubectl top nodes

# Adjust resource limits
kubectl edit deployment backend -n todo-app

# Configure HPA thresholds
kubectl edit hpa backend -n todo-app
```

#### 3. Caching Configuration
```bash
# Check Redis connection
kubectl exec -it redis-master-0 -- redis-cli ping

# Monitor cache hit rate
kubectl exec -it redis-master-0 -- redis-cli info stats | grep hit_rate

# Clear cache if needed
kubectl exec -it redis-master-0 -- redis-cli FLUSHALL
```

---

## Cost Optimization

### 1. Right-Size Resources
```bash
# Analyze resource usage over time
kubectl top pods -n todo-app --containers

# Adjust resource requests/limits based on actual usage
# Reduce over-provisioned resources
```

### 2. Use Spot Instances
```bash
# Create node pool with preemptible instances
oci ce node-pool create \
  --cluster-id <cluster-ocid> \
  --name "spot-pool" \
  --node-shape "VM.Standard.E4.Flex" \
  --node-shape-config '{"ocpus":2,"memoryInGBs":16}' \
  --size 3 \
  --placement-configs '[{"availabilityDomain":"<AD>","subnetId":"<subnet-ocid>"}]' \
  --node-source-details '{"sourceType":"IMAGE","imageId":"<image-ocid>","bootVolumeSizeInGBs":50}' \
  --is-pv-encryption-in-transit-enabled true
```

### 3. Optimize Storage
```bash
# Use block volumes with lower performance tiers for non-critical data
# Enable compression for logs and backups
# Set up lifecycle policies for old data
```

### 4. Monitor Costs
```bash
# Use OCI Cost Analysis
oci usage-api usage-summary list-usage-carbon-emissions \
  --tenant-id $OCI_TENANCY_ID \
  --time-usage-started "2024-01-01T00:00:00Z" \
  --time-usage-ended "2024-02-01T00:00:00Z"
```

---

## Backup and Disaster Recovery

### 1. Database Backups
```bash
# Autonomous Database automatic backups (enabled by default)
# Manual backup
oci db autonomous-database create-backup \
  --autonomous-database-id <adb-ocid> \
  --display-name "manual-backup-$(date +%Y%m%d)"

# Restore from backup
oci db autonomous-database restore \
  --autonomous-database-id <adb-ocid> \
  --timestamp "2024-02-04T10:00:00Z"
```

### 2. Application State Backup
```bash
# Backup Redis state
kubectl exec -it redis-master-0 -- redis-cli BGSAVE

# Copy RDB file
kubectl cp redis-master-0:/data/dump.rdb ./backup/redis-$(date +%Y%m%d).rdb

# Backup Kafka topics
kubectl exec -it todo-kafka-kafka-0 -n kafka -- bin/kafka-mirror-maker.sh \
  --consumer.config /tmp/consumer.properties \
  --producer.config /tmp/producer.properties \
  --whitelist ".*"
```

### 3. Kubernetes Resources Backup
```bash
# Install Velero
helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts
helm install velero vmware-tanzu/velero \
  --namespace velero \
  --create-namespace \
  --set configuration.provider=aws \
  --set configuration.backupStorageLocation.bucket=<oci-bucket> \
  --set configuration.backupStorageLocation.config.region=$OCI_REGION

# Create backup
velero backup create todo-app-backup --include-namespaces todo-app

# Restore from backup
velero restore create --from-backup todo-app-backup
```

---

## Next Steps

1. **Set up CI/CD Pipeline**: Configure GitHub Actions or OCI DevOps for automated deployments
2. **Enable Auto-Scaling**: Configure cluster autoscaler for dynamic node scaling
3. **Implement Blue-Green Deployment**: Set up traffic splitting for zero-downtime deployments
4. **Configure Multi-Region**: Deploy to multiple OCI regions for global availability
5. **Set up Disaster Recovery**: Implement cross-region replication and failover

---

## Support and Resources

- **OCI Documentation**: https://docs.oracle.com/en-us/iaas/Content/home.htm
- **OKE Documentation**: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm
- **Dapr Documentation**: https://docs.dapr.io/
- **Kubernetes Documentation**: https://kubernetes.io/docs/

---

## Appendix

### A. OCI CLI Commands Reference
```bash
# List compartments
oci iam compartment list --all

# List OKE clusters
oci ce cluster list --compartment-id $OCI_COMPARTMENT_ID

# List compute instances
oci compute instance list --compartment-id $OCI_COMPARTMENT_ID

# List autonomous databases
oci db autonomous-database list --compartment-id $OCI_COMPARTMENT_ID
```

### B. Useful kubectl Commands
```bash
# Get all resources in namespace
kubectl get all -n todo-app

# Watch pod status
kubectl get pods -n todo-app -w

# Get events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Execute command in pod
kubectl exec -it <pod-name> -n todo-app -- bash

# Port forward service
kubectl port-forward svc/backend 8000:8000 -n todo-app
```

### C. Helm Commands Reference
```bash
# List releases
helm list -n todo-app

# Get release values
helm get values backend -n todo-app

# Rollback release
helm rollback backend 1 -n todo-app

# Uninstall release
helm uninstall backend -n todo-app
```
