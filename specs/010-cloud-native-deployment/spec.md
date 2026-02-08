# Feature Specification: Phase V - Advanced Cloud Deployment

**Feature ID**: 010-cloud-native-deployment
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-01-30
**Author**: Principal System Architect

---

## Executive Summary

Phase V transforms the Ary's Evolutioned Todo application into a production-ready, event-driven, cloud-native system with Kafka message streaming, Dapr distributed runtime, and deployment to both local Minikube and cloud Kubernetes clusters. This phase implements advanced task management features (recurring tasks, reminders, priorities, tags, search/filter/sort) and establishes a zero-friction CI/CD pipeline for continuous delivery.

**Success Criteria**: A horizontally scalable, fault-tolerant, event-driven system deployed to cloud Kubernetes with automated CI/CD, comprehensive monitoring, and reusable intelligence artifacts (agents, skills, blueprints).

---

## 1. Context & Motivation

### 1.1 Current State (Phase IV Complete)

**Achievements**:
- ✅ Local Kubernetes deployment on Minikube with AI-generated Helm charts
- ✅ AI chatbot with multi-agent architecture (OpenAI Agents SDK + MCP)
- ✅ Full-stack web app (Next.js 15 + FastAPI + Neon PostgreSQL)
- ✅ Production deployment (Vercel + HuggingFace Spaces)
- ✅ Authentication (Better Auth with JWT/JWKS)
- ✅ Reusable intelligence: enhanced skills, custom agents
- ✅ Multi-language support (English + Urdu) with voice input

**Limitations**:
- Synchronous request-response architecture (no event streaming)
- No distributed state management
- Manual deployment processes
- Limited observability and monitoring
- No auto-scaling or fault tolerance mechanisms
- Missing advanced features (reminders, recurring task execution)

### 1.2 Business Drivers

1. **Scalability**: Handle 10,000+ concurrent users with horizontal scaling
2. **Reliability**: 99.9% uptime with fault tolerance and self-healing
3. **Real-time Sync**: Multi-client task updates via event streaming
4. **Audit Trail**: Complete event log for compliance and debugging
5. **Developer Velocity**: Zero-friction feature delivery via CI/CD
6. **Cost Efficiency**: Cloud-native architecture with resource optimization

### 1.3 User Impact

**End Users**:
- Real-time task synchronization across devices
- Reliable reminder notifications (no missed due dates)
- Advanced task organization (priorities, tags, search)
- Automatic recurring task creation
- Faster response times with async processing

**Developers**:
- Reusable blueprints for cloud-native deployment
- Automated testing and deployment
- Clear event-driven patterns
- Comprehensive monitoring and debugging tools

---

## 2. Requirements

### 2.1 Functional Requirements

#### FR-001: Event-Driven Architecture
**Priority**: P0 (Critical)
**Description**: Implement Kafka-based event streaming for all task operations.

**Acceptance Criteria**:
- [ ] Kafka topics created: `task-events`, `reminders`, `task-updates`
- [ ] All CRUD operations publish events to `task-events`
- [ ] Event schema includes: event_id, event_type, timestamp, user_id, task_id, payload
- [ ] Events are immutable and append-only
- [ ] Dead letter queue for failed event processing

**Event Types**:
- `task.created`, `task.updated`, `task.completed`, `task.deleted`
- `task.uncompleted`, `task.priority_changed`, `task.tag_added`, `task.tag_removed`
- `reminder.scheduled`, `reminder.triggered`, `reminder.dismissed`
- `recurring.generated`, `recurring.skipped`

#### FR-002: Dapr Integration
**Priority**: P0 (Critical)
**Description**: Use Dapr for all distributed system concerns.

**Acceptance Criteria**:
- [ ] Dapr installed on Minikube and cloud Kubernetes
- [ ] Pub/Sub component configured for Kafka abstraction
- [ ] State Store component for conversation and task state
- [ ] Service Invocation for frontend ↔ backend communication
- [ ] Jobs API for exact-time reminder scheduling (NO polling)
- [ ] Secrets component for credential management
- [ ] Application code uses only Dapr HTTP/gRPC APIs (no direct Kafka client)

**Dapr Components**:
```yaml
# pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-pubsub
spec:
  type: pubsub.kafka

# statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-statestore
spec:
  type: state.postgresql
```

#### FR-003: Advanced Task Features
**Priority**: P0 (Critical)
**Description**: Implement all advanced task management capabilities.

**3.1 Recurring Tasks**:
- [ ] Cron expression support (daily, weekly, monthly, custom)
- [ ] Automatic task generation via Recurring Task Service
- [ ] Skip/pause recurring schedules
- [ ] Next occurrence calculation and display
- [ ] Event: `recurring.generated` published to `task-events`

**3.2 Due Dates & Reminders**:
- [ ] ISO 8601 datetime support with timezone
- [ ] Reminder scheduling via Dapr Jobs API (exact-time, no polling)
- [ ] Notification Service consumes `reminders` topic
- [ ] Multiple reminder types: email, push, in-app
- [ ] Snooze functionality (5min, 15min, 1hr, custom)
- [ ] Event: `reminder.triggered` published to `reminders` topic

**3.3 Priorities**:
- [ ] Priority levels: Low (1), Medium (2), High (3), Urgent (4)
- [ ] Priority-based sorting in list views
- [ ] Visual indicators (colors, icons)
- [ ] Filter by priority in search
- [ ] Event: `task.priority_changed` published to `task-events`

**3.4 Tags**:
- [ ] Multi-tag support per task (PostgreSQL array column)
- [ ] Tag autocomplete in UI
- [ ] Tag-based filtering and grouping
- [ ] Tag cloud visualization
- [ ] GIN index on tags column for fast search
- [ ] Event: `task.tag_added`, `task.tag_removed` published to `task-events`

**3.5 Search, Filter, Sort**:
- [ ] Full-text search on title and description (PostgreSQL `tsvector`)
- [ ] Filter by: status, priority, tags, due date range, created date
- [ ] Sort by: created_at, updated_at, due_date, priority, title
- [ ] Saved search queries
- [ ] Search results highlighting

#### FR-004: Event Consumers
**Priority**: P0 (Critical)
**Description**: Implement microservices that consume Kafka events.

**4.1 Recurring Task Service**:
- [ ] Consumes `task-events` topic (filter: `recurring.generated`)
- [ ] Generates new task instances based on cron schedule
- [ ] Publishes `task.created` events for generated tasks
- [ ] Handles timezone conversions
- [ ] Idempotent processing (deduplicate events)

**4.2 Notification Service**:
- [ ] Consumes `reminders` topic
- [ ] Sends notifications via multiple channels (email, push, in-app)
- [ ] Retry logic with exponential backoff
- [ ] Notification delivery tracking
- [ ] User notification preferences

**4.3 Audit Service**:
- [ ] Consumes all topics (`task-events`, `reminders`, `task-updates`)
- [ ] Stores complete event log in separate audit database
- [ ] Provides audit trail API for compliance
- [ ] Event replay capability for debugging
- [ ] Retention policy (90 days default)

**4.4 WebSocket Sync Service**:
- [ ] Consumes `task-updates` topic
- [ ] Broadcasts real-time updates to connected clients via WebSocket
- [ ] Client subscription management (per-user filtering)
- [ ] Reconnection handling with event replay
- [ ] Optimistic UI updates with server reconciliation

#### FR-005: Local Deployment (Minikube)
**Priority**: P0 (Critical)
**Description**: Deploy complete system to Minikube with Dapr and Kafka.

**Acceptance Criteria**:
- [ ] Minikube cluster with sufficient resources (8GB RAM, 4 CPUs)
- [ ] Dapr installed via `dapr init -k`
- [ ] Kafka deployed via Strimzi operator or Helm chart
- [ ] All services deployed with Helm charts
- [ ] Ingress configured for external access
- [ ] Health checks (liveness + readiness) for all services
- [ ] Resource limits and requests defined
- [ ] Persistent volumes for Kafka and PostgreSQL

**Services**:
- Frontend (2 replicas)
- Backend API (2 replicas)
- Recurring Task Service (1 replica)
- Notification Service (1 replica)
- Audit Service (1 replica)
- WebSocket Sync Service (2 replicas)
- Kafka (3 brokers)
- PostgreSQL (1 instance, external Neon or local)

#### FR-006: Cloud Deployment
**Priority**: P0 (Critical)
**Description**: Deploy to production cloud Kubernetes cluster.

**Acceptance Criteria**:
- [ ] Cloud provider selected: Oracle OKE (always-free) OR DigitalOcean Kubernetes OR GKE/AKS
- [ ] Kubernetes cluster created with kubectl configured
- [ ] Dapr installed with production configuration
- [ ] Kafka deployed via Redpanda Cloud OR Confluent Cloud OR Strimzi
- [ ] Helm charts deployed from Phase IV (AI-generated)
- [ ] TLS/SSL certificates configured (Let's Encrypt)
- [ ] DNS configured for custom domain
- [ ] Monitoring enabled (Prometheus + Grafana)
- [ ] Logging enabled (Loki or cloud-native solution)
- [ ] Auto-scaling configured (HPA for CPU/memory)
- [ ] Backup and disaster recovery plan

**Cloud Provider Recommendations**:
1. **Oracle OKE** (Recommended): Always-free tier, 2 VMs, 24GB RAM total
2. **DigitalOcean Kubernetes**: $12/month for 2 nodes, simple setup
3. **GKE/AKS**: Enterprise features, higher cost

**Kafka Options**:
1. **Redpanda Cloud**: Kafka-compatible, free tier available, simpler than Kafka
2. **Confluent Cloud**: Managed Kafka, free tier, excellent tooling
3. **Strimzi**: Self-hosted Kafka on Kubernetes, full control, more complex

#### FR-007: CI/CD Pipeline
**Priority**: P0 (Critical)
**Description**: Automated build, test, and deployment pipeline.

**Acceptance Criteria**:
- [ ] GitHub Actions workflow configured
- [ ] Triggered on: push to main, pull request, manual dispatch
- [ ] Pipeline stages:
  1. **Build**: Docker images for all services
  2. **Test**: Unit tests, integration tests, E2E tests
  3. **Scan**: Security scanning (Trivy), linting, code quality
  4. **Deploy**: Helm upgrade to Kubernetes cluster
  5. **Verify**: Health checks, smoke tests
- [ ] Rollback mechanism on failure
- [ ] Deployment strategies: Rolling update (default), Canary (optional), Blue-Green (optional)
- [ ] Environment-specific configurations (dev, staging, prod)
- [ ] Secrets management via GitHub Secrets + Dapr Secrets
- [ ] Deployment notifications (Slack, email)

**Pipeline Flow**:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    - Build Docker images
    - Push to registry (GHCR or Docker Hub)

  test:
    - Run unit tests (pytest, jest)
    - Run integration tests
    - Generate coverage report

  scan:
    - Trivy security scan
    - ESLint + Pylint
    - Dependency audit

  deploy:
    - Helm upgrade --install
    - Wait for rollout
    - Run smoke tests

  verify:
    - Health check endpoints
    - E2E test suite
    - Performance baseline
```

#### FR-008: Monitoring & Observability
**Priority**: P1 (High)
**Description**: Comprehensive monitoring, logging, and tracing.

**Acceptance Criteria**:
- [ ] Prometheus for metrics collection
- [ ] Grafana dashboards for visualization
- [ ] Loki for log aggregation (or cloud-native alternative)
- [ ] Jaeger for distributed tracing (optional)
- [ ] Custom metrics: task operations/sec, event processing latency, queue depth
- [ ] Alerts configured: high error rate, pod restarts, resource exhaustion
- [ ] SLO/SLI tracking: 99.9% uptime, p95 latency < 200ms
- [ ] Dapr metrics and tracing enabled

**Key Metrics**:
- Request rate, error rate, latency (RED method)
- Kafka consumer lag
- Event processing throughput
- Database connection pool utilization
- Pod CPU/memory usage

### 2.2 Non-Functional Requirements

#### NFR-001: Performance
- **Latency**: p95 < 200ms for API requests, p99 < 500ms
- **Throughput**: 1000 requests/sec per backend replica
- **Event Processing**: < 1 second from event publish to consumer processing
- **Database**: Query response time < 50ms for indexed queries

#### NFR-002: Scalability
- **Horizontal Scaling**: Auto-scale from 2 to 10 replicas based on CPU (70% threshold)
- **Concurrent Users**: Support 10,000+ concurrent WebSocket connections
- **Event Volume**: Handle 100,000 events/hour
- **Database**: Connection pooling (max 20 connections per replica)

#### NFR-003: Reliability
- **Uptime**: 99.9% availability (43 minutes downtime/month)
- **Fault Tolerance**: Survive single pod failure without service disruption
- **Data Durability**: Kafka replication factor 3, PostgreSQL backups every 6 hours
- **Graceful Degradation**: Continue operation if non-critical services fail

#### NFR-004: Security
- **Authentication**: JWT-based auth with JWKS validation (existing)
- **Authorization**: User-scoped data access (filter by user_id)
- **Secrets**: Managed via Dapr Secrets + Kubernetes Secrets
- **Network**: TLS for all external traffic, mTLS for service-to-service (Dapr)
- **Compliance**: GDPR-compliant audit logs, data retention policies

#### NFR-005: Maintainability
- **Code Coverage**: 80%+ for backend, 70%+ for frontend
- **Documentation**: API docs (OpenAPI), architecture diagrams, runbooks
- **Logging**: Structured JSON logs with correlation IDs
- **Deployment**: Zero-downtime rolling updates

---

## 3. Technical Architecture

### 3.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Cloud Kubernetes                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   Frontend   │◄────►│  Ingress     │◄────►│   Backend    │  │
│  │  (Next.js)   │      │  Controller  │      │   (FastAPI)  │  │
│  │  2 replicas  │      └──────────────┘      │  2 replicas  │  │
│  └──────────────┘                            └──────┬───────┘  │
│         │                                            │           │
│         │                                            │           │
│         ▼                                            ▼           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Dapr Sidecar                           │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐         │  │
│  │  │  Pub/Sub   │  │   State    │  │  Service   │         │  │
│  │  │  (Kafka)   │  │   Store    │  │ Invocation │         │  │
│  │  └────────────┘  └────────────┘  └────────────┘         │  │
│  │  ┌────────────┐  ┌────────────┐                          │  │
│  │  │  Jobs API  │  │  Secrets   │                          │  │
│  │  └────────────┘  └────────────┘                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Kafka Cluster                          │  │
│  │  Topics: task-events, reminders, task-updates            │  │
│  │  3 brokers, replication factor 3                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐   │
│  │  Recurring  │      │Notification │      │   Audit     │   │
│  │   Task      │      │  Service    │      │  Service    │   │
│  │  Service    │      │  1 replica  │      │  1 replica  │   │
│  │  1 replica  │      └─────────────┘      └─────────────┘   │
│  └─────────────┘                                               │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              PostgreSQL (Neon or Self-Hosted)             │  │
│  │  Tables: users, tasks, conversations, audit_events       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 Monitoring Stack                          │  │
│  │  Prometheus + Grafana + Loki                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Event Flow

**Task Creation Flow**:
```
1. User creates task via UI
2. Frontend → Backend API (POST /api/v1/tasks)
3. Backend saves to PostgreSQL
4. Backend publishes event to Dapr Pub/Sub
5. Dapr publishes to Kafka topic: task-events
6. Consumers receive event:
   - Audit Service: Logs event
   - WebSocket Sync Service: Broadcasts to connected clients
   - Recurring Task Service: Schedules next occurrence (if recurring)
7. Frontend receives WebSocket update, refreshes UI
```

**Reminder Flow**:
```
1. Task with due_date created
2. Backend schedules reminder via Dapr Jobs API
3. At reminder time, Dapr triggers job
4. Backend publishes event to Kafka topic: reminders
5. Notification Service consumes event
6. Notification Service sends notification (email/push/in-app)
7. User receives reminder
```

### 3.3 Database Schema Updates

**New Columns for `tasks` table**:
```sql
ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 2;
ALTER TABLE tasks ADD COLUMN tags TEXT[] DEFAULT '{}';
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN reminder_time TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN recurrence_rule TEXT; -- Cron expression
ALTER TABLE tasks ADD COLUMN next_occurrence TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN search_vector tsvector;

CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector);
```

**New Table: `audit_events`**:
```sql
CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    user_id UUID NOT NULL,
    task_id UUID,
    payload JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_events_user_id ON audit_events(user_id);
CREATE INDEX idx_audit_events_task_id ON audit_events(task_id);
CREATE INDEX idx_audit_events_timestamp ON audit_events(timestamp);
```

### 3.4 Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Message Broker** | Kafka (Redpanda Cloud) | Industry standard, high throughput, durable |
| **Distributed Runtime** | Dapr | Abstracts infrastructure, portable, polyglot |
| **Orchestration** | Kubernetes (OKE/DO/GKE) | Cloud-native, auto-scaling, self-healing |
| **CI/CD** | GitHub Actions | Native GitHub integration, free for public repos |
| **Monitoring** | Prometheus + Grafana | CNCF standard, rich ecosystem |
| **Logging** | Loki | Lightweight, integrates with Grafana |
| **Secrets** | Dapr Secrets + K8s Secrets | Secure, encrypted, auditable |
| **State Store** | PostgreSQL (via Dapr) | Reuse existing database, ACID guarantees |

---

## 4. Reusable Intelligence (+200 Bonus Points)

### 4.1 Claude Code Subagents

**New Agents** (in `.claude/agents/`):

1. **kafka-engineer** (kafka-engineer.agent.md):
   - Responsibilities: Kafka topic design, consumer implementation, event schema
   - Tools: Read, Grep, Glob, Bash, Edit, Write
   - Triggers: Kafka setup, event-driven architecture, consumer debugging

2. **dapr-engineer** (dapr-engineer.agent.md):
   - Responsibilities: Dapr component configuration, sidecar integration, Jobs API
   - Tools: Read, Grep, Glob, Bash, Edit, Write
   - Triggers: Dapr setup, pub/sub, state management, service invocation

3. **cloud-deployment-engineer** (cloud-deployment-engineer.agent.md):
   - Responsibilities: Cloud Kubernetes setup, Helm deployment, DNS/TLS config
   - Tools: All tools
   - Triggers: Cloud deployment, cluster setup, production configuration

4. **cicd-engineer** (cicd-engineer.agent.md):
   - Responsibilities: GitHub Actions workflows, deployment automation, rollback
   - Tools: Read, Grep, Glob, Bash, Edit, Write
   - Triggers: CI/CD setup, pipeline debugging, deployment automation

5. **monitoring-engineer** (monitoring-engineer.agent.md):
   - Responsibilities: Prometheus setup, Grafana dashboards, alerting rules
   - Tools: Read, Grep, Glob, Bash, Edit, Write
   - Triggers: Monitoring setup, dashboard creation, alert configuration

### 4.2 Agent Skills

**New Skills** (install via `npx skills add`):

1. **event-driven-architecture**:
   - Kafka topic design patterns
   - Event schema best practices
   - Consumer group management
   - Dead letter queue handling

2. **dapr-integration**:
   - Dapr component configuration
   - Pub/Sub patterns
   - State management strategies
   - Jobs API scheduling

3. **cloud-kubernetes-deployment**:
   - Cloud provider setup (OKE, DO, GKE, AKS)
   - Helm chart deployment
   - Ingress and TLS configuration
   - Auto-scaling setup

4. **cicd-automation**:
   - GitHub Actions workflow templates
   - Multi-stage pipeline design
   - Deployment strategies (rolling, canary, blue-green)
   - Rollback procedures

5. **observability-stack**:
   - Prometheus metrics design
   - Grafana dashboard templates
   - Loki log aggregation
   - Alert rule configuration

### 4.3 Cloud-Native Blueprints

**Blueprints** (in `blueprints/`):

1. **event-driven-microservices** (blueprints/event-driven-microservices/):
   - Kafka + Dapr integration template
   - Consumer service boilerplate
   - Event schema definitions
   - Testing strategies

2. **kubernetes-production-deployment** (blueprints/kubernetes-production-deployment/):
   - Helm chart structure
   - Dapr component manifests
   - Ingress + TLS configuration
   - Monitoring stack setup

3. **github-actions-cicd** (blueprints/github-actions-cicd/):
   - Multi-stage pipeline template
   - Docker build and push
   - Helm deployment workflow
   - Rollback automation

---

## 5. Success Metrics

### 5.1 Technical Metrics

- [ ] **Event Processing Latency**: p95 < 1 second
- [ ] **API Response Time**: p95 < 200ms
- [ ] **System Uptime**: 99.9% over 30 days
- [ ] **Auto-Scaling**: Scales from 2 to 10 replicas under load
- [ ] **CI/CD Pipeline**: < 10 minutes from commit to production
- [ ] **Test Coverage**: Backend 80%+, Frontend 70%+

### 5.2 Feature Completeness

- [ ] All FR-001 to FR-008 acceptance criteria met
- [ ] All NFR-001 to NFR-005 requirements satisfied
- [ ] Reusable intelligence artifacts created (5 agents, 5 skills, 3 blueprints)
- [ ] Documentation complete (README, architecture diagrams, runbooks)

### 5.3 Deliverables

- [ ] Public GitHub repository with all code
- [ ] `/specs/010-cloud-native-deployment/` folder with spec, plan, tasks
- [ ] Updated CLAUDE.md and README.md
- [ ] Deployment URLs (Minikube + Cloud)
- [ ] ≤90 second demo video showing:
  - Advanced features (recurring, reminders, priorities, tags, search)
  - Real-time sync across multiple clients
  - Event-driven architecture in action
  - CI/CD pipeline execution
  - Agentic workflow (agents creating agents, skills in action)

---

## 6. Constraints & Assumptions

### 6.1 Constraints

- **Budget**: Use free tiers where possible (Oracle OKE, Redpanda Cloud, Neon PostgreSQL)
- **Timeline**: Phase V completion within project deadline
- **Technology**: Must use Kafka + Dapr (non-negotiable per requirements)
- **Compatibility**: Must maintain backward compatibility with Phase IV Helm charts

### 6.2 Assumptions

- Phase IV is fully functional and validated
- Minikube has sufficient resources (8GB RAM, 4 CPUs)
- Cloud provider account is available and configured
- GitHub repository has Actions enabled
- Domain name is available for cloud deployment (optional)

### 6.3 Out of Scope

- Multi-region deployment
- Advanced Kafka features (Kafka Streams, ksqlDB)
- Machine learning for task recommendations
- Mobile app development
- Advanced authentication (SSO, SAML)

---

## 7. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Kafka complexity | High | Medium | Use Redpanda Cloud (simpler), Dapr abstraction |
| Cloud cost overrun | Medium | Low | Use free tiers, set budget alerts, monitor usage |
| CI/CD pipeline failures | Medium | Medium | Comprehensive testing, rollback automation |
| Event ordering issues | High | Low | Use Kafka partitioning by user_id, idempotent consumers |
| Dapr learning curve | Medium | Medium | Follow official docs, use blueprints, leverage skills |
| Performance degradation | High | Low | Load testing, auto-scaling, caching strategies |

---

## 8. Dependencies

### 8.1 External Dependencies

- **Cloud Provider**: Oracle OKE / DigitalOcean / GKE / AKS account
- **Kafka**: Redpanda Cloud / Confluent Cloud account
- **Domain**: Optional custom domain for production
- **GitHub**: Repository with Actions enabled

### 8.2 Internal Dependencies

- Phase IV completion and validation
- Existing Helm charts from Phase IV
- Database schema migration scripts
- Authentication system (Better Auth)

---

## 9. Acceptance Criteria Summary

**Phase V is complete when**:

1. ✅ Event-driven architecture implemented with Kafka + Dapr
2. ✅ All advanced features working (recurring, reminders, priorities, tags, search)
3. ✅ Deployed to Minikube with full Dapr stack
4. ✅ Deployed to cloud Kubernetes with monitoring
5. ✅ CI/CD pipeline automated via GitHub Actions
6. ✅ Reusable intelligence created (5 agents, 5 skills, 3 blueprints)
7. ✅ All tests passing (unit, integration, E2E)
8. ✅ Documentation complete and demo video recorded
9. ✅ System meets all NFRs (performance, scalability, reliability)
10. ✅ Production-ready validation confirmed

---

## 10. Next Steps

1. **Validate Phase IV**: Run comprehensive tests, verify Helm charts
2. **Create Plan**: Detailed architecture and implementation plan (plan.md)
3. **Generate Tasks**: Testable tasks with acceptance criteria (tasks.md)
4. **Implement**: Execute via Agentic Dev Stack (subagents + skills)
5. **Test**: Comprehensive testing at each milestone
6. **Deploy**: Minikube → Cloud with CI/CD
7. **Validate**: Production readiness checklist
8. **Document**: Final documentation and demo video

---

**Specification Status**: Ready for Planning Phase
**Next Artifact**: `plan.md` - Architecture & Implementation Plan
