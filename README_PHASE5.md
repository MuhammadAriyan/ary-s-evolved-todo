# Phase V Event-Driven Cloud Deployment - README

## Overview

Ary's Evolved Todo has been transformed into a cloud-native, event-driven microservices application deployed on Oracle Kubernetes Engine (OKE). This phase implements real-time synchronization, precise time-based reminders, advanced recurring patterns, full-text search, audit trails, and collaborative features.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 15+)                      │
│  • Real-time WebSocket sync                                     │
│  • Optimistic UI updates                                        │
│  • Offline-first with sync queue                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend API (FastAPI)                       │
│  • Task CRUD operations                                         │
│  • Search with PostgreSQL full-text                             │
│  • JWT authentication (Better Auth)                             │
│  • Event publishing to Kafka                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Dapr Pub/Sub
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Redpanda (Kafka-compatible)                        │
│  Topics: task-events, task-updates, notification-events        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Event Streaming
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Event-Driven Microservices                   │
│  • WebSocket Sync Service (real-time updates)                  │
│  • Notification Service (time-based reminders)                 │
│  • Recurring Task Service (pattern generation)                 │
│  • Audit Service (complete audit trail)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Data Persistence
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PostgreSQL (Neon)  │  Redis (State Store)  │  Monitoring      │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Real-Time Synchronization (User Story 1)
- **WebSocket-based sync**: Task changes appear across all devices within 2 seconds
- **Optimistic UI updates**: Instant feedback with automatic rollback on errors
- **Connection resilience**: Auto-reconnect with missed event replay
- **Multi-device support**: Sync across unlimited devices per user

### 2. Precise Time-Based Reminders (User Story 2)
- **Exact-time delivery**: Notifications within 10 seconds of scheduled time
- **Multi-channel**: Email and in-app notifications
- **Timezone-aware**: Automatic timezone conversion
- **Idempotent delivery**: No duplicate notifications

### 3. Advanced Recurring Patterns (User Story 3)
- **Flexible patterns**: Daily, weekly, weekdays, monthly, custom cron
- **Automatic generation**: Next instance created on completion
- **Pattern validation**: Prevents invalid or excessive frequencies
- **Timezone support**: Respects user timezone settings

### 4. Intelligent Search (User Story 4)
- **Full-text search**: PostgreSQL tsvector with relevance ranking
- **Fuzzy matching**: Handles typos with pg_trgm extension
- **Advanced filters**: Status, priority, tags, date ranges
- **Fast performance**: <1 second for 10k+ tasks

### 5. Complete Audit Trail (User Story 5)
- **Event sourcing**: All operations logged via Kafka events
- **Before/after state**: Complete change history
- **Batch processing**: Efficient writes with 100-event batches
- **Export support**: JSON and CSV formats

### 6. Production Deployment (User Story 6)
- **Oracle OKE**: Kubernetes deployment on Oracle Cloud free tier
- **Dapr runtime**: Service mesh with Pub/Sub, State Store, Bindings
- **CI/CD pipelines**: Automated build, test, and deploy
- **Monitoring**: Prometheus + Grafana with custom dashboards

### 7. Reusable Intelligence (User Story 7)
- **Agents**: microservice-creator for scaffolding new services
- **Skills**: event-pattern, dapr-component, helm-chart, monitoring-setup
- **Blueprints**: event-driven-architecture, microservices-deployment, dapr-integration

## Technology Stack

### Frontend
- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS
- **State Management**: React hooks + WebSocket client
- **Authentication**: Better Auth (JWT)

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **ORM**: SQLModel
- **Database**: Neon PostgreSQL (serverless)
- **Cache/State**: Redis (managed)
- **Event Streaming**: Redpanda Cloud (Kafka-compatible)

### Infrastructure
- **Container Orchestration**: Kubernetes (Oracle OKE)
- **Service Mesh**: Dapr runtime
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions
- **Deployment**: Helm charts

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Node.js 18+
- Dapr CLI
- kubectl and Helm (for Kubernetes deployment)

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/your-org/evolved-todo.git
cd evolved-todo
```

2. **Start infrastructure services**
```bash
cd infrastructure
docker-compose -f docker-compose.dev.yml up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Redpanda (port 9092)
- Redpanda Console (port 8080)

3. **Set up backend**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed development data (optional)
python scripts/seed_dev_data.py

# Start backend API with Dapr
dapr run \
  --app-id backend-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ../infrastructure/dapr \
  -- uvicorn app.main:app --reload
```

4. **Start microservices**

In separate terminals:

```bash
# WebSocket Sync Service
cd backend/microservices/websocket_sync
dapr run \
  --app-id websocket-sync \
  --app-port 8001 \
  --components-path ../../../infrastructure/dapr \
  -- python main.py

# Notification Service
cd backend/microservices/notification
dapr run \
  --app-id notification-service \
  --app-port 8002 \
  --components-path ../../../infrastructure/dapr \
  -- python main.py

# Recurring Task Service
cd backend/microservices/recurring_task
dapr run \
  --app-id recurring-task-service \
  --app-port 8003 \
  --components-path ../../../infrastructure/dapr \
  -- python main.py

# Audit Service
cd backend/microservices/audit
dapr run \
  --app-id audit-service \
  --app-port 8004 \
  --components-path ../../../infrastructure/dapr \
  -- python main.py
```

5. **Set up frontend**
```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Start development server
npm run dev
```

6. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Redpanda Console: http://localhost:8080

## Project Structure

```
evolved-todo/
├── backend/
│   ├── app/                      # Main application
│   │   ├── api/                  # API endpoints
│   │   ├── models/               # SQLModel database models
│   │   ├── services/             # Business logic
│   │   └── middleware/           # JWT auth, etc.
│   ├── microservices/            # Event-driven services
│   │   ├── websocket_sync/       # Real-time sync
│   │   ├── notification/         # Reminders
│   │   ├── recurring_task/       # Recurring patterns
│   │   └── audit/                # Audit trail
│   ├── tests/                    # Unit and integration tests
│   └── requirements.txt
├── frontend/
│   ├── app/                      # Next.js App Router pages
│   ├── components/               # React components
│   ├── hooks/                    # Custom hooks
│   ├── lib/                      # Utilities
│   └── package.json
├── infrastructure/
│   ├── dapr/                     # Dapr components
│   ├── helm/                     # Helm charts
│   ├── monitoring/               # Prometheus/Grafana
│   ├── ci-cd/                    # GitHub Actions
│   └── docker-compose.dev.yml
├── .claude/                      # Reusable intelligence
│   ├── agents/                   # AI agents
│   ├── skills/                   # Code generation skills
│   └── blueprints/               # Architecture patterns
└── specs/                        # Feature specifications
    └── 011-event-driven-microservices/
```

## Testing

### Run Backend Tests
```bash
cd backend
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/contract/ -v
```

### Run Frontend Tests
```bash
cd frontend
npm test
npm run test:e2e  # Playwright E2E tests
```

### Load Testing
```bash
cd backend
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment guide.

### Quick Deploy to Oracle OKE

```bash
# Configure kubectl context
kubectl config use-context oracle-oke

# Create namespace
kubectl create namespace evolved-todo

# Create secrets
kubectl create secret generic database-secret \
  --from-literal=url="postgresql://..." \
  -n evolved-todo

# Deploy with Helm
helm upgrade --install backend-api \
  infrastructure/helm/backend \
  -n evolved-todo

helm upgrade --install frontend \
  infrastructure/helm/frontend \
  -n evolved-todo

# Deploy microservices
for service in websocket-sync notification recurring-task audit; do
  helm upgrade --install $service \
    infrastructure/helm/$service \
    -n evolved-todo
done
```

## Monitoring

See [MONITORING.md](./MONITORING.md) for observability guide.

### Access Monitoring Dashboards

```bash
# Port-forward Grafana
kubectl port-forward -n evolved-todo svc/grafana 3000:3000

# Access at http://localhost:3000
# Default credentials: admin/admin
```

### Key Metrics
- Request rate and latency (p50, p95, p99)
- Error rates by service
- WebSocket connection count
- Event processing throughput
- Database query performance

## Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)**: Production deployment guide
- **[MONITORING.md](./MONITORING.md)**: Observability and troubleshooting
- **[specs/011-event-driven-microservices/](./specs/011-event-driven-microservices/)**: Feature specifications
- **[.claude/](./claude/)**: Reusable intelligence (agents, skills, blueprints)

## Contributing

1. Create feature branch from `main`
2. Implement changes with tests
3. Run linters and tests locally
4. Create pull request
5. Wait for CI/CD checks to pass
6. Request code review

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/evolved-todo/issues
- Documentation: https://docs.evolved-todo.example.com
