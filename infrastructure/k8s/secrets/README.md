# Kubernetes Secrets Configuration

This directory contains Kubernetes Secret manifests for the Todo application.

## Important Security Notes

⚠️ **NEVER commit actual secrets to version control!**

The files in this directory are templates. Before deploying:

1. Copy each template file
2. Replace placeholder values with actual credentials
3. Apply secrets using `kubectl apply -f <secret-file>.yaml`
4. Delete the files with actual credentials from your local machine

## Secrets Management Best Practices

### For Development
- Use `.env` files locally (already in `.gitignore`)
- Use Dapr secrets component with local file store

### For Production
- Use Oracle Cloud Vault or Kubernetes Secrets
- Enable encryption at rest for Kubernetes Secrets
- Use RBAC to restrict access to secrets
- Rotate secrets regularly

## Required Secrets

### backend-secrets.yaml
Contains all backend service credentials:
- `database-url`: Neon PostgreSQL connection string
- `redis-url`: Redis connection string
- `kafka-brokers`: Redpanda Cloud broker addresses
- `kafka-username`: Kafka authentication username
- `kafka-password`: Kafka authentication password
- `better-auth-secret`: JWT signing secret
- `openai-api-key`: OpenAI API key for chat features
- `sendgrid-api-key`: SendGrid API key for email notifications
- `oke-kubeconfig`: Oracle OKE cluster kubeconfig

## Applying Secrets

```bash
# Create namespace if it doesn't exist
kubectl create namespace default

# Apply secrets
kubectl apply -f backend-secrets.yaml

# Verify secrets are created
kubectl get secrets -n default

# View secret keys (not values)
kubectl describe secret backend-secrets -n default
```

## Using Secrets in Helm Charts

Secrets are referenced in Helm chart values using `secretKeyRef`:

```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: backend-secrets
        key: database-url
```

## Rotating Secrets

```bash
# Update secret
kubectl create secret generic backend-secrets \
  --from-literal=database-url="new-value" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart deployments to pick up new secrets
kubectl rollout restart deployment/backend-api
kubectl rollout restart deployment/websocket-sync
kubectl rollout restart deployment/notification
```

## GitHub Secrets for CI/CD

Configure these secrets in GitHub repository settings:

- `OKE_KUBECONFIG`: Base64-encoded kubeconfig for Oracle OKE
- `GHCR_TOKEN`: GitHub Container Registry token
- `DATABASE_URL`: Production database URL
- `REDIS_URL`: Production Redis URL
- `KAFKA_BROKERS`: Production Kafka brokers
- `KAFKA_USERNAME`: Production Kafka username
- `KAFKA_PASSWORD`: Production Kafka password
- `BETTER_AUTH_SECRET`: Production auth secret
- `OPENAI_API_KEY`: Production OpenAI key
- `SENDGRID_API_KEY`: Production SendGrid key
