# Feature Specification: Phase V Event-Driven Cloud Deployment

**Feature Branch**: `011-event-driven-microservices`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "Phase V Cloud Deployment: Transform into event-driven, cloud-native system with Kafka + Dapr event streaming, advanced features (exact-time reminders via Dapr Jobs API, cron expressions, full-text search), microservices (Recurring Task Service, Notification Service, Audit Service, WebSocket Sync Service), cloud deployment (Oracle OKE or DigitalOcean Kubernetes), CI/CD pipeline (GitHub Actions), monitoring (Prometheus + Grafana + Loki), and reusable intelligence (5 agents, 5 skills, 3 blueprints)"

## Clarifications

### Session 2026-01-31

- Q: What is the scope of shared task collaboration mentioned in User Story 1? → A: Full collaborative editing with friend system, groups with admin permissions, messaging, task assignments, comments, and mentions. Each user has unique ID, can add friends, join groups, and collaborate on tasks with permission-based access control managed by group admins.
- Q: How granular should group permission management be? → A: Capability-based permissions where admins can toggle individual permissions (add tasks, edit tasks, delete tasks, comment, assign) per member.
- Q: What is the task ownership model within groups? → A: Group owns all tasks displayed to the group. Only the group owner (original creator) can manage permissions and the collaborator list. Group owner can promote any member to admin status. Admins have full control over all group tasks and can assign full access (add, edit, delete) to specific members.
- Q: Which authentication mechanism should be implemented for "basic authentication"? → A: JWT token-based authentication with Better Auth (already used in project)
- Q: Which cloud platform and event streaming service should be used? → A: Oracle OKE (Oracle Kubernetes Engine) with Oracle Cloud free tier + Redpanda Cloud for Kafka-compatible event streaming. Use full Dapr capabilities (Pub/Sub, State, Bindings/cron, Secrets, Service Invocation). CI/CD via GitHub Actions. Keep existing Neon PostgreSQL database.
- Q: Which full-text search implementation should be used? → A: PostgreSQL full-text search with tsvector columns and GIN indexes (built into Neon)
- Q: Which backend should be used for Dapr state store? → A: Redis - separate managed Redis instance for low-latency state operations (WebSocket connections, sessions, rate limiting, distributed locks). PostgreSQL/Neon remains the primary database for persistent application data.
- Q: Which monitoring stack deployment approach should be used? → A: Lightweight in-cluster monitoring with Prometheus + Grafana only. Defer Loki for log aggregation or use Oracle Cloud Logging to conserve resources on Oracle Cloud free tier.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real-Time Task Synchronization Across Devices (Priority: P1)

Users need their task changes to appear instantly across all their devices and browser tabs without manual refresh. When a user creates, updates, or completes a task on one device, all other active sessions should reflect the change immediately through event-driven updates.

**Why this priority**: This is the foundational capability that justifies the event-driven architecture. Without real-time sync, the system remains a traditional request-response application. This delivers immediate user value and validates the core architectural transformation.

**Independent Test**: Can be fully tested by opening the application in two browser tabs, creating a task in one tab, and verifying it appears in the other tab within 2 seconds without refresh. Delivers immediate value by eliminating the frustration of stale data.

**Acceptance Scenarios**:

1. **Given** a user has the application open in two browser tabs, **When** they create a new task in tab 1, **Then** the task appears in tab 2 within 2 seconds without manual refresh
2. **Given** a user marks a task complete on their mobile device, **When** they switch to their desktop browser, **Then** the task shows as completed within 2 seconds
3. **Given** multiple users collaborating on shared tasks, **When** one user updates a task, **Then** all other users see the update within 2 seconds
4. **Given** a user's connection is temporarily lost, **When** the connection is restored, **Then** all missed updates are synchronized automatically

---

### User Story 2 - Precise Time-Based Task Reminders (Priority: P1)

Users need to receive notifications at exact specified times for their tasks, not just at midnight polling intervals. When a user sets a task reminder for 2:30 PM, they should receive the notification at exactly 2:30 PM, not hours later.

**Why this priority**: This addresses a critical limitation of the current APScheduler polling system (midnight-only execution). Time-sensitive reminders are essential for productivity applications and represent a key user pain point with the current system.

**Independent Test**: Can be fully tested by creating a task with a reminder set for 5 minutes in the future, then verifying the notification arrives within 10 seconds of the scheduled time. Delivers immediate value by making the reminder system actually useful for time-sensitive tasks.

**Acceptance Scenarios**:

1. **Given** a user creates a task with a reminder for 2:30 PM, **When** the system time reaches 2:30 PM, **Then** the user receives a notification within 10 seconds
2. **Given** a user sets a reminder for "every weekday at 9:00 AM", **When** 9:00 AM arrives on a weekday, **Then** the user receives the notification within 10 seconds
3. **Given** a user sets multiple reminders for different tasks, **When** reminder times arrive, **Then** each notification is delivered at its exact scheduled time
4. **Given** a user's device is offline when a reminder is scheduled, **When** the device comes back online, **Then** the user receives a notification about missed reminders

---

### User Story 3 - Advanced Recurring Task Patterns (Priority: P2)

Users need to create recurring tasks with complex schedules beyond simple daily/weekly/monthly patterns. Examples include "every weekday at 9 AM", "first Monday of each month", "every 3 days", or custom cron expressions for power users.

**Why this priority**: This builds on the core event-driven infrastructure (P1) to provide advanced scheduling capabilities. While not essential for MVP, it significantly enhances the value proposition for power users and differentiates the product.

**Independent Test**: Can be fully tested by creating a task with the pattern "every weekday at 9 AM", advancing the system clock through a week, and verifying the task recurs Monday-Friday but not Saturday-Sunday. Delivers value by supporting real-world work patterns.

**Acceptance Scenarios**:

1. **Given** a user creates a recurring task with pattern "every weekday at 9 AM", **When** the schedule executes over a week, **Then** new task instances are created Monday through Friday at 9 AM, but not on weekends
2. **Given** a user creates a task with pattern "first Monday of each month", **When** the first Monday arrives, **Then** a new task instance is created
3. **Given** a power user enters a custom cron expression "0 */4 * * *" (every 4 hours), **When** the schedule executes, **Then** new task instances are created every 4 hours
4. **Given** a user modifies a recurring task pattern, **When** the change is saved, **Then** future instances follow the new pattern while past instances remain unchanged

---

### User Story 4 - Intelligent Task Search (Priority: P2)

Users need to quickly find tasks using natural language search across task titles, descriptions, tags, and notes. When a user searches for "meeting with client", the system should find all tasks containing those words, even with typos or partial matches.

**Why this priority**: As users accumulate hundreds of tasks, finding specific items becomes critical. Full-text search transforms the application from a simple list manager into a powerful knowledge base. This builds on the core infrastructure but isn't required for basic functionality.

**Independent Test**: Can be fully tested by creating 50 tasks with various content, searching for "client meeting", and verifying all relevant tasks appear in ranked order within 1 second. Delivers value by making large task lists manageable.

**Acceptance Scenarios**:

1. **Given** a user has 100+ tasks in the system, **When** they search for "client meeting", **Then** all tasks containing those words appear in ranked order within 1 second
2. **Given** a user searches with a typo like "meetng", **When** the search executes, **Then** the system suggests "meeting" and shows relevant results
3. **Given** a user searches for a tag like "#urgent", **When** the search executes, **Then** all tasks tagged with "urgent" appear
4. **Given** a user searches for partial text like "proj", **When** the search executes, **Then** tasks containing "project", "projection", etc. appear

---

### User Story 5 - Complete Activity Audit Trail (Priority: P2)

Users and administrators need to see a complete history of all task changes, including who made changes, when, and what was modified. This supports accountability, debugging, and compliance requirements.

**Why this priority**: Audit trails are essential for team collaboration and compliance but don't affect core task management functionality. This leverages the event-driven architecture to capture all changes automatically.

**Independent Test**: Can be fully tested by creating a task, modifying it 5 times, then viewing the audit log to verify all changes are recorded with timestamps and user information. Delivers value for team accountability and debugging.

**Acceptance Scenarios**:

1. **Given** a user creates and modifies a task multiple times, **When** they view the task's audit log, **Then** all changes are listed with timestamps, user names, and specific fields modified
2. **Given** an administrator needs to investigate a deleted task, **When** they search the audit log, **Then** they can see who deleted it, when, and the task's final state
3. **Given** a team collaborates on shared tasks, **When** conflicts arise, **Then** the audit log shows the complete sequence of changes to resolve disputes
4. **Given** a compliance audit is requested, **When** the administrator exports audit logs, **Then** all task operations for the specified time period are included

---

### User Story 6 - Production-Ready Cloud Deployment (Priority: P1)

The system must be deployable to production cloud infrastructure with automated CI/CD, monitoring, and operational readiness. When code is pushed to the main branch, it should automatically build, test, scan for security issues, and deploy to the cloud environment.

**Why this priority**: This is essential for moving from local development to production use. Without reliable deployment and monitoring, the system cannot serve real users. This is foundational infrastructure that enables all other features to reach users.

**Independent Test**: Can be fully tested by pushing a code change to the main branch, then verifying it automatically deploys to the cloud environment within 10 minutes with all health checks passing. Delivers value by enabling continuous delivery and reducing deployment risk.

**Acceptance Scenarios**:

1. **Given** a developer pushes code to the main branch, **When** the CI/CD pipeline executes, **Then** the code is built, tested, scanned, and deployed to production within 10 minutes
2. **Given** the application is running in production, **When** an administrator views the monitoring dashboard, **Then** they see real-time metrics for all services (CPU, memory, request rates, error rates)
3. **Given** a service experiences errors, **When** the error rate exceeds thresholds, **Then** alerts are sent to the operations team within 1 minute
4. **Given** a deployment fails health checks, **When** the failure is detected, **Then** the deployment is automatically rolled back to the previous stable version

---

### User Story 7 - Reusable Development Intelligence (Priority: P3)

Development teams need reusable agents, skills, and blueprints to accelerate future development and maintain consistency. When a new developer joins or a new feature is needed, they should have access to proven patterns and automated workflows.

**Why this priority**: This is an investment in long-term development velocity and quality. While not directly user-facing, it significantly reduces the cost and risk of future enhancements. This is lower priority because it doesn't affect end-user functionality.

**Independent Test**: Can be fully tested by using the provided agents to perform common tasks (e.g., "deploy a new microservice") and verifying the agent completes the task following established patterns. Delivers value by reducing development time for future features.

**Acceptance Scenarios**:

1. **Given** a developer needs to add a new microservice, **When** they invoke the microservice-creator agent, **Then** the agent generates a complete service template with Dockerfile, Helm charts, and CI/CD configuration
2. **Given** a developer needs to troubleshoot a production issue, **When** they invoke the debugger agent, **Then** the agent analyzes logs, traces, and metrics to identify the root cause
3. **Given** a new team member joins, **When** they review the blueprints documentation, **Then** they understand the system architecture and can contribute within 1 week
4. **Given** a developer needs to implement a new event type, **When** they use the event-pattern skill, **Then** the skill generates producer and consumer code following established patterns

---

### Edge Cases

- What happens when the event streaming system (Kafka) is temporarily unavailable? System should queue events locally and replay when connectivity is restored.
- How does the system handle event ordering when multiple users modify the same task simultaneously? System should use event timestamps and last-write-wins conflict resolution with audit trail preservation.
- What happens when a microservice crashes while processing an event? System should use dead-letter queues to capture failed events and retry with exponential backoff.
- How does the system handle clock skew across distributed services? System should use UTC timestamps and tolerate up to 5 seconds of clock drift.
- What happens when a user sets a recurring task pattern that would create thousands of instances? System should validate patterns and limit to reasonable frequencies (minimum 1-minute intervals).
- How does full-text search handle special characters, emojis, and non-English text? System should support Unicode, normalize text, and handle special characters gracefully.
- What happens when the monitoring system itself fails? System should have external health checks and fallback alerting mechanisms.
- How does the system handle database connection failures during event processing? System should retry with exponential backoff and use circuit breakers to prevent cascade failures.

## Requirements *(mandatory)*

### Functional Requirements

#### Event-Driven Architecture

- **FR-001**: System MUST publish events for all task state changes (create, update, delete, complete, archive) via Dapr Pub/Sub with Redpanda Cloud backend
- **FR-002**: System MUST support event subscriptions by multiple independent services without coupling using Dapr Pub/Sub component abstraction
- **FR-003**: System MUST guarantee at-least-once event delivery to all subscribers through Redpanda Cloud
- **FR-004**: System MUST preserve event ordering for events related to the same task using Kafka partition keys
- **FR-005**: System MUST support event replay for service recovery and debugging through Redpanda Cloud retention policies

#### Real-Time Synchronization

- **FR-006**: System MUST deliver task updates to all active user sessions within 2 seconds
- **FR-007**: System MUST maintain persistent connections to clients for real-time updates
- **FR-008**: System MUST automatically reconnect clients after temporary network interruptions
- **FR-009**: System MUST synchronize missed updates when clients reconnect after being offline

#### Time-Based Reminders

- **FR-010**: System MUST support scheduling reminders at exact times with 10-second accuracy using Dapr Bindings (cron) API
- **FR-011**: System MUST support recurring reminders with cron expression syntax via Dapr Bindings
- **FR-012**: System MUST deliver reminder notifications through multiple channels (in-app, email, push)
- **FR-013**: System MUST handle timezone conversions for users in different locations
- **FR-014**: System MUST persist scheduled reminders in Redis state store for durability across service restarts

#### Advanced Recurring Patterns

- **FR-015**: System MUST support recurring task patterns: daily, weekly, monthly, yearly
- **FR-016**: System MUST support weekday-only recurring patterns (Monday-Friday)
- **FR-017**: System MUST support custom cron expressions for power users
- **FR-018**: System MUST validate recurring patterns to prevent excessive task creation
- **FR-019**: System MUST allow users to modify recurring patterns without affecting past instances

#### Full-Text Search

- **FR-020**: System MUST index task titles, descriptions, tags, and notes using PostgreSQL tsvector columns with GIN indexes
- **FR-021**: System MUST return search results ranked by relevance within 1 second using ts_rank
- **FR-022**: System MUST support partial word matching using prefix search and fuzzy matching with pg_trgm extension
- **FR-023**: System MUST support search filters (by date, priority, tags, completion status) combined with full-text queries
- **FR-024**: System MUST update tsvector search indexes within 5 seconds of task changes using database triggers

#### Audit Trail

- **FR-025**: System MUST record all task operations (create, read, update, delete) with timestamps
- **FR-026**: System MUST capture user identity, IP address, and user agent for each operation
- **FR-027**: System MUST record before and after values for all field changes
- **FR-028**: System MUST retain audit logs for minimum 90 days
- **FR-029**: System MUST support audit log export in standard formats (JSON, CSV)

#### Microservices Architecture

- **FR-030**: System MUST separate concerns into independent services: Recurring Task Service, Notification Service, Audit Service, WebSocket Sync Service
- **FR-031**: Each microservice MUST be independently deployable without affecting other services
- **FR-032**: Each microservice MUST expose health check endpoints for monitoring
- **FR-033**: Each microservice MUST implement graceful shutdown to complete in-flight requests
- **FR-034**: Microservices MUST communicate exclusively through events (no direct service-to-service calls)

#### Cloud Deployment

- **FR-035**: System MUST be deployable to Oracle OKE (Oracle Kubernetes Engine) on Oracle Cloud free tier
- **FR-036**: System MUST support horizontal scaling of all microservices based on load
- **FR-037**: System MUST use Neon PostgreSQL (existing) and managed Redis for state operations
- **FR-038**: System MUST implement health checks for automatic pod restart on failures
- **FR-039**: System MUST support zero-downtime deployments with rolling updates

#### CI/CD Pipeline

- **FR-040**: System MUST automatically build and test code on every pull request
- **FR-041**: System MUST scan code for security vulnerabilities before deployment
- **FR-042**: System MUST automatically deploy to staging environment on merge to main branch
- **FR-043**: System MUST require manual approval for production deployments
- **FR-044**: System MUST automatically rollback failed deployments

#### Monitoring and Observability

- **FR-045**: System MUST collect metrics for all services (CPU, memory, request rates, error rates) using Prometheus
- **FR-046**: System MUST aggregate logs from all services using Oracle Cloud Logging (Loki deferred for resource conservation)
- **FR-047**: System MUST trace requests across service boundaries for debugging using Dapr distributed tracing
- **FR-048**: System MUST alert operations team when error rates exceed thresholds via Prometheus Alertmanager
- **FR-049**: System MUST provide Grafana dashboards showing system health and performance

#### Reusable Intelligence

- **FR-050**: System MUST provide 5 specialized agents for common development tasks
- **FR-051**: System MUST provide 5 reusable skills for code generation and automation
- **FR-052**: System MUST provide 3 architectural blueprints documenting key patterns
- **FR-053**: All agents, skills, and blueprints MUST include documentation and usage examples
- **FR-054**: Reusable intelligence MUST be versioned and maintained alongside code

#### Collaboration and Social Features

- **FR-055**: System MUST support friend connections between users with unique user IDs
- **FR-056**: System MUST provide real-time friends section showing online status and activity
- **FR-057**: System MUST support direct messaging between friends
- **FR-058**: System MUST support creation of collaboration groups with admin-managed permissions
- **FR-059**: System MUST allow group admins to toggle individual permissions per member (add tasks, edit tasks, delete tasks, comment, assign)
- **FR-060**: System MUST support task assignments to specific group members
- **FR-061**: System MUST support comments on tasks with @mentions of group members
- **FR-062**: System MUST support viewing personal tasks from user profiles (with privacy controls)
- **FR-063**: System MUST deliver real-time notifications for mentions, assignments, and comments
- **FR-064**: Group members MUST see real-time task updates based on their permission level
- **FR-065**: Group admins MUST be able to promote other members to admin status
- **FR-066**: Only group owner and admins MUST be able to manage the collaborator list and permissions
- **FR-067**: All tasks within a group MUST be owned by the group (not individual members)
- **FR-068**: Group admins MUST be able to assign full access to specific members for all group operations

### Key Entities

- **Task Event**: Represents a state change in a task (type, timestamp, task_id, user_id, before_state, after_state, metadata)
- **Scheduled Reminder**: Represents a future notification (task_id, user_id, scheduled_time, cron_expression, notification_channels, status)
- **Audit Log Entry**: Represents a recorded operation (operation_type, timestamp, user_id, ip_address, user_agent, resource_type, resource_id, before_values, after_values)
- **WebSocket Connection**: Represents an active client session (connection_id, user_id, connected_at, last_heartbeat, subscribed_events)
- **Search Index**: Represents indexed task content for full-text search (task_id, indexed_content, last_updated, search_vector)
- **User**: Represents a system user (user_id, username, email, profile_settings, privacy_settings)
- **Friend Connection**: Represents a friendship between two users (user_id_1, user_id_2, status, connected_at, online_status)
- **Collaboration Group**: Represents a group for task collaboration (group_id, name, admin_user_id, created_at, member_count)
- **Group Membership**: Represents a user's membership in a group (group_id, user_id, role, permissions, joined_at)
- **Task Assignment**: Represents assignment of a task to a user (task_id, assigned_to_user_id, assigned_by_user_id, assigned_at, status)
- **Task Comment**: Represents a comment on a task (comment_id, task_id, user_id, content, mentions, created_at, updated_at)
- **Direct Message**: Represents a message between friends (message_id, from_user_id, to_user_id, content, sent_at, read_at)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Task updates appear on all active user sessions within 2 seconds of the change
- **SC-002**: Reminder notifications are delivered within 10 seconds of scheduled time
- **SC-003**: Full-text search returns results within 1 second for queries across 10,000+ tasks
- **SC-004**: System handles 1,000 concurrent WebSocket connections without degradation
- **SC-005**: Event processing latency remains under 100ms at p95 for all event types
- **SC-006**: System achieves 99.9% uptime in production (less than 43 minutes downtime per month)
- **SC-007**: CI/CD pipeline completes build, test, and deployment within 10 minutes
- **SC-008**: All microservices scale automatically when CPU exceeds 70% utilization
- **SC-009**: Failed deployments are automatically rolled back within 2 minutes
- **SC-010**: Monitoring dashboards show real-time metrics with less than 10-second delay
- **SC-011**: Audit logs capture 100% of task operations with complete before/after state
- **SC-012**: Development teams can deploy new microservices using provided agents in under 1 hour

## Assumptions

- Users have stable internet connections for real-time synchronization (system handles temporary disconnections gracefully)
- Oracle Cloud free tier provides sufficient resources for initial deployment (2 AMD VMs + 4 Arm Ampere cores with 24GB RAM)
- Redpanda Cloud provides Kafka-compatible API with at-least-once delivery guarantees
- Existing Neon PostgreSQL database can be extended with new tables for audit logs, search indexes (tsvector), and collaboration features
- Managed Redis instance (Oracle Cloud or external provider) is available for Dapr state store operations
- Users accept eventual consistency for non-critical operations (e.g., audit log writes may lag by seconds)
- Development team has access to GitHub Actions for CI/CD pipeline
- Prometheus and Grafana can be deployed within Oracle OKE cluster with acceptable resource overhead
- Oracle Cloud Logging provides sufficient log aggregation capabilities (Loki deferred for resource conservation)
- Dapr runtime can be deployed on Oracle OKE with full component support (Pub/Sub, State, Bindings, Secrets, Service Invocation)
- WebSocket connections are supported by Oracle Cloud load balancer
- Users understand cron expression syntax or the UI provides a visual cron builder
- Existing task schema supports the required fields (priority, tags, due_date, recurring patterns)
- Better Auth JWT tokens can be validated across all microservices for authentication

## Dependencies

- **Cloud Platform**: Oracle OKE (Oracle Kubernetes Engine) on Oracle Cloud free tier
- **Event Streaming**: Redpanda Cloud (Kafka-compatible managed service)
- **Service Runtime**: Dapr with Pub/Sub, State (Redis backend), Bindings (cron), Secrets, Service Invocation
- **Database**: Neon PostgreSQL (existing) for persistent application data
- **State Store**: Managed Redis instance for Dapr state operations (WebSocket connections, sessions, rate limiting, distributed locks)
- **CI/CD**: GitHub Actions for automated build, test, security scanning, and deployment
- **Monitoring**: Prometheus (metrics), Grafana (dashboards), Oracle Cloud Logging (log aggregation)
- **Authentication**: Better Auth (existing) with JWT token-based authentication
- **Search**: PostgreSQL full-text search with tsvector columns and GIN indexes (built into Neon)
- **Notification Channels**: Email service (SendGrid, AWS SES, or similar), push notification service (optional)

## Out of Scope

- Mobile native applications (iOS/Android) - web application only for Phase V
- Multi-tenancy and organization management - single-user or group-based collaboration only
- Custom notification channels beyond email and in-app - no SMS, Slack, or third-party integrations
- Advanced analytics and reporting dashboards - basic metrics only
- Task templates and automation workflows - manual task creation only
- Integration with external calendar systems (Google Calendar, Outlook) - standalone system only
- Advanced security features (SSO, SAML, MFA) - basic authentication only
- Data export and migration tools - manual export only
- Custom branding and white-labeling - standard UI only

## Non-Functional Requirements

### Performance

- Event processing latency: p95 < 100ms, p99 < 500ms
- WebSocket message delivery: < 2 seconds end-to-end
- Search query response time: < 1 second for 10,000+ tasks
- API response time: p95 < 200ms, p99 < 1 second
- Database query time: p95 < 50ms, p99 < 200ms

### Scalability

- Support 10,000 concurrent WebSocket connections per service instance
- Support 1,000 events per second through the event streaming system
- Support horizontal scaling of all microservices (2-10 replicas per service)
- Support 100,000+ tasks per user without performance degradation
- Support 1 million audit log entries with efficient querying

### Reliability

- System uptime: 99.9% (less than 43 minutes downtime per month)
- Event delivery: at-least-once guarantee with idempotent consumers
- Data durability: zero data loss for committed transactions
- Automatic recovery: services restart automatically on failure
- Graceful degradation: system remains functional if non-critical services fail

### Security

- All API endpoints require JWT token-based authentication via Better Auth
- All data in transit encrypted with TLS 1.3
- All data at rest encrypted using cloud provider encryption
- Audit logs capture all security-relevant operations
- Secrets managed through Dapr Secrets API with Kubernetes secrets backend
- Regular security scanning in CI/CD pipeline

### Observability

- All services emit structured logs with correlation IDs
- All services expose Prometheus metrics endpoints
- Distributed tracing across all service boundaries
- Real-time dashboards for system health and performance
- Automated alerts for error rates, latency, and resource utilization

### Maintainability

- All services follow consistent coding standards and patterns
- All services include comprehensive unit and integration tests
- All services include API documentation (OpenAPI/Swagger)
- All infrastructure defined as code (Helm charts, Terraform)
- All reusable intelligence (agents, skills, blueprints) documented and versioned
