# Phase V: Event-Driven Architecture Documentation

## System Overview

Ary's Evolved Todo has been transformed into a cloud-native, event-driven task management system with real-time synchronization, precise time-based reminders, and comprehensive audit trails.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Frontend (Next.js 15)                         │
│                         http://localhost:3000                           │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │ Task Manager │  │ Search UI    │  │ Reminders    │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐             │
│  │         WebSocket Client (Auto-Reconnect)            │             │
│  └──────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Backend API (FastAPI)                            │
│                       http://localhost:8000                             │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │ Task CRUD    │  │ Search API   │  │ Auth (JWT)   │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐             │
│  │         EventPublisher (Dapr Pub/Sub)                │             │
│  └──────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Event Streaming (Redpanda/Kafka)                     │
│                                                                         │
│  Topics: task-events, task-updates, reminder-events, audit-events      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────┬───────────┼───────────┬───────────────┐
        │               │           │           │               │
        ▼               ▼           ▼           ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  WebSocket   │ │ Notification │ │  Recurring   │ │    Audit     │
│    Sync      │ │   Service    │ │    Task      │ │   Service    │
│   :8001      │ │    :8002     │ │   Service    │ │    :8004     │
│              │ │              │ │    :8003     │ │              │
│ • Real-time  │ │ • Reminders  │ │ • Cron       │ │ • Change     │
│   updates    │ │ • Multi-     │ │   patterns   │ │   history    │
│ • WebSocket  │ │   channel    │ │ • Task       │ │ • Audit      │
│   broadcast  │ │   notify     │ │   generator  │ │   logs       │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │               │           │           │
        └───────────────┴───────────┴───────────┴───────────────┐
                                    │                           │
                                    ▼                           ▼
                    ┌───────────────────────────┐   ┌──────────────────┐
                    │  PostgreSQL (Neon)        │   │  Redis (State)   │
                    │  • Tasks                  │   │  • WebSocket     │
                    │  • Audit logs             │   │    connections   │
                    │  • Reminders              │   │  • Sessions      │
                    │  • Users (Better Auth)    │   │  • Idempotency   │
                    └───────────────────────────┘   └──────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth (JWT)
- **State Management**: TanStack React Query
- **Real-time**: WebSocket client with auto-reconnect
- **UI Components**: Radix UI + shadcn/ui

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.12+
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Authentication**: JWT verification middleware
- **API Documentation**: OpenAPI/Swagger

### Infrastructure
- **Database**: PostgreSQL (Neon serverless)
- **State Store**: Redis (managed)
- **Event Streaming**: Redpanda (Kafka-compatible)
- **Runtime**: Dapr (Distributed Application Runtime)
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes (Oracle OKE)

### Microservices
1. **WebSocket Sync Service** (Python + FastAPI)
   - Real-time task synchronization
   - Connection management via Redis
   - Event consumption from Kafka

2. **Notification Service** (Python + FastAPI)
   - Time-based reminder scheduling
   - Multi-channel notifications (email, in-app, push)
   - Timezone conversion

3. **Recurring Task Service** (Python + FastAPI)
   - Cron pattern parsing
   - Task instance generation
   - Schedule management

4. **Audit Service** (Python + FastAPI)
   - Change history tracking
   - Batch log writing
   - Event consumption

## Event Flow

### Task Creation Flow

```
1. User creates task in Frontend
   ↓
2. Frontend → POST /api/v1/tasks → Backend API
   ↓
3. Backend saves task to PostgreSQL
   ↓
4. Backend publishes event to Kafka (task-events topic)
   ↓
5. Event consumed by:
   - WebSocket Sync Service → broadcasts to connected clients
   - Audit Service → logs change to audit_log table
   ↓
6. Frontend receives WebSocket message
   ↓
7. UI updates in real-time (all connected devices)
```

### Reminder Flow

```
1. User schedules reminder in Frontend
   ↓
2. Frontend → POST /api/v1/reminders → Backend API
   ↓
3. Backend saves reminder to scheduled_reminders table
   ↓
4. Notification Service checks for due reminders every minute
   ↓
5. When reminder time arrives:
   - Notification Service sends notification
   - Publishes event to Kafka (reminder-events topic)
   - Marks reminder as sent (idempotency check)
   ↓
6. Frontend receives notification via WebSocket
   ↓
7. User sees in-app notification
```

## Database Schema

### Core Tables

**tasks**
- id (PK)
- user_id (indexed)
- title, description
- completed (indexed)
- priority
- tags (array)
- due_date (indexed)
- search_vector (tsvector, GIN indexed)
- recurring_pattern (JSONB)
- parent_task_id (FK to tasks)
- group_id
- created_at, updated_at

**audit_log**
- id (PK)
- user_id (indexed)
- entity_type, entity_id
- action (create, update, delete)
- before_state (JSONB)
- after_state (JSONB)
- created_at (indexed)

**scheduled_reminders**
- id (PK)
- task_id (FK to tasks)
- user_id (indexed)
- reminder_time (indexed)
- channel (email, in_app, push)
- sent (boolean)
- created_at

### Collaboration Tables (Phase V Extended)

**friend_connections**
- id (PK)
- user_id, friend_id
- status (pending, accepted, blocked)
- created_at

**collaboration_groups**
- id (PK)
- name, description
- owner_id
- created_at

**group_memberships**
- id (PK)
- group_id (FK)
- user_id
- role (owner, admin, member)
- permissions (JSONB)
- joined_at

## Dapr Components

### Pub/Sub (Redpanda)

**pubsub-redpanda.yaml**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-redpanda
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:19092"
  - name: consumerGroup
    value: "todo-app"
```

### State Store (Redis)

**statestore-redis.yaml**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redis-statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "localhost:6379"
  - name: redisPassword
    value: ""
```

## API Endpoints

### Tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List tasks
- `GET /api/v1/tasks/{id}` - Get task
- `PATCH /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

### Search
- `GET /api/v1/search?query={text}` - Full-text search
- `GET /api/v1/search?query={text}&status=pending` - Search with filters

### Reminders
- `POST /api/v1/tasks/{id}/reminders` - Schedule reminder
- `GET /api/v1/tasks/{id}/reminders` - List reminders
- `DELETE /api/v1/reminders/{id}` - Cancel reminder

### Audit
- `GET /api/v1/audit?entity_id={id}` - Get audit logs
- `GET /api/v1/audit?user_id={id}` - Get user audit logs

### Health & Metrics
- `GET /health` - Health check (all services)
- `GET /metrics` - Prometheus metrics (all services)

## Performance Targets

- **Real-time sync**: <2 seconds end-to-end
- **Reminder delivery**: <10 seconds of scheduled time
- **Search response**: <1 second for 10k+ tasks
- **Event processing**: <100ms p95 latency
- **API response**: <200ms p95

## Security

### Authentication
- JWT tokens via Better Auth
- Token expiry: 7 days
- Session expiry: 7 days
- Cookie cache: 5 minutes

### Authorization
- User isolation: All queries filter by user_id
- JWT verification middleware on all protected endpoints
- No cross-user data access

### Data Protection
- SQL injection prevention via SQLModel parameterization
- Input validation on all endpoints
- CORS configured for trusted origins
- Rate limiting on public endpoints

## Monitoring

### Health Checks
All services expose `/health` endpoint:
```json
{
  "status": "healthy",
  "service": "service-name",
  "timestamp": "2026-02-04T00:00:00",
  "checks": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "dapr": {"status": "healthy"}
  }
}
```

### Metrics
All services expose `/metrics` endpoint with:
- Request count
- Response times
- Error rates
- Custom metrics (connections, events processed, etc.)

## Deployment

### Local Development
```bash
# Start all services
/dev

# Or manually:
cd infrastructure && docker compose -f docker-compose.dev.yml up -d
cd backend && dapr run --app-id backend-api --app-port 8000 ...
cd frontend && npm run dev
```

### Production (Kubernetes)
```bash
# Deploy with Helm
helm install todo-app ./infrastructure/helm/todo-app

# Or with kubectl
kubectl apply -f infrastructure/k8s/
```

## Troubleshooting

### WebSocket Connection Issues
- Check BETTER_AUTH_URL matches frontend port (3000)
- Verify JWT token is valid
- Check CORS configuration includes frontend origin

### Event Not Flowing
- Verify Kafka topics exist: `docker exec todo-redpanda rpk topic list`
- Check Dapr components are loaded: `dapr components -k`
- Verify microservices are subscribed to topics

### Database Connection Errors
- Check DATABASE_URL environment variable
- Verify PostgreSQL is running: `docker ps | grep postgres`
- Run migrations: `alembic upgrade head`

## Next Steps

1. **Test the system** - Follow manual testing guide
2. **Deploy to production** - Set up Oracle OKE cluster
3. **Add monitoring** - Configure Prometheus + Grafana
4. **Write tests** - Integration and load testing
5. **Document APIs** - Complete OpenAPI specification

## Resources

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- WebSocket Sync: http://localhost:8001/health
- Notification: http://localhost:8002/health
- Recurring Tasks: http://localhost:8003/health
- Audit Service: http://localhost:8004/health

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/evolved-todo/issues
- Documentation: /docs
- Architecture: /ARCHITECTURE.md
