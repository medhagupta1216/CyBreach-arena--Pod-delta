# CyBreach Arena – Pod Delta

This repository contains the backend service for the CyBreach Arena Pod Delta integration layer. It combines three functional areas in one FastAPI application:

- Notification Hub APIs
- Analytics Engine APIs
- Kafka/Redpanda + Redis + WebSocket integration processing

The code is primarily under the `app/` package, and the project is configured to run as a standalone backend service. The repository also contains some root-level front-end prototype artifacts, but the active application code for this pod is the FastAPI backend.

## Current project status

The project is actively wired for the following runtime behavior:

- FastAPI app boots in `app/main.py`
- Notification, preference, analytics, and integration routers are included
- Startup triggers `start_integration()` which initializes Redis, WebSocket manager, Kafka producer, and Kafka consumer
- SQLite is the default local database; Postgres and Redis/Kafka services are available through Docker Compose
- WebSocket tenant feed is available at `/ws/{tenant_id}`
- Prometheus metrics are exposed at `/metrics`
- App health endpoints are exposed at `/` and `/api/v1/health`
- Integration health is exposed at `/api/v1/integration/health`

## Repository structure

```text
.
├── app/
│   ├── api/
│   │   ├── analytics_engine_routes.py
│   │   ├── integration_routes.py
│   │   ├── notification_routes.py
│   │   ├── preference_routes.py
│   │   └── websocket_routes.py
│   ├── core/
│   ├── database/
│   ├── events/
│   ├── integration/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── alembic/
├── tests/
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── INTEGRATION_RUNBOOK.md
├── cybreach.db
├── cyberarena.zip
├── App.jsx
├── CyBreachArena.jsx
├── main.jsx
├── index.css
└── App.css
```

## Technology stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Pydantic 2.x
- Redis
- Redpanda / Kafka (via `aiokafka`)
- SQLite (local default)
- PostgreSQL (available in Docker Compose)
- ClickHouse (available in Docker Compose for analytics integrations)
- Uvicorn
- pytest

## Core application behavior

### 1. Notification Hub

The notification component exposes APIs under `/api/v1/notifications` and allows:

- Listing notifications with search, filters, pagination, and sorting
- Fetching notifications by user
- Fetching unread notifications and unread counts
- Creating notifications
- Updating notifications
- Deleting notifications
- Bulk mark-as-read and bulk delete operations
- Notification statistics for dashboards

Preference APIs are available under `/api/v1/preferences` for per-user delivery settings.

### 2. Analytics Engine

The analytics component exposes APIs under `/api/v1/analytics` and supports:

- Create, list, and fetch analytics records
- Filter by tenant, report month, score range, and date range
- Fetch dashboard summaries
- Fetch credit-flow, engagement, score, score-trend, and report endpoints
- Update and delete analytics records

### 3. Integration layer

The integration layer processes consumed Kafka topics and produces outbound events. The runtime is configured to consume events such as:

- `wallet.transaction`
- `engagement.lifecycle`
- `engagement.completed`
- `mod3.score`
- `achievement.awarded`
- `leaderboard.updated`
- `benchmark.computed`

It can publish:

- `notification.sent`
- `analytics.report`
- `score.displayed`

The integration layer also uses Redis for:

- rate limiting
- cached score storage
- WebSocket session state

## API overview

### Health and monitoring

- `GET /` — root health response
- `GET /api/v1/health` — app health
- `GET /api/v1/integration/health` — integration service health
- `GET /metrics` — Prometheus metrics

### Notification APIs

- `GET /api/v1/notifications/`
- `GET /api/v1/notifications/user/{user_id}`
- `GET /api/v1/notifications/unread`
- `GET /api/v1/notifications/unread/count`
- `GET /api/v1/notifications/stats`
- `POST /api/v1/notifications/`
- `PUT /api/v1/notifications/{notification_id}`
- `DELETE /api/v1/notifications/{notification_id}`
- `PATCH /api/v1/notifications/{notification_id}/read`
- `PATCH /api/v1/notifications/{notification_id}/status`
- `PATCH /api/v1/notifications/bulk/read`
- `DELETE /api/v1/notifications/bulk`

### Preference APIs

- `POST /api/v1/preferences/`
- `GET /api/v1/preferences/{user_id}`
- `PUT /api/v1/preferences/{user_id}`

### Analytics APIs

- `POST /api/v1/analytics`
- `GET /api/v1/analytics`
- `GET /api/v1/analytics/{id}`
- `GET /api/v1/analytics/tenant/{tenant_id}`
- `GET /api/v1/analytics/dashboard/{tenant_id}`
- `GET /api/v1/analytics/credit-flow/{tenant_id}`
- `GET /api/v1/analytics/engagement/{tenant_id}`
- `GET /api/v1/analytics/score/{tenant_id}`
- `GET /api/v1/analytics/score-trend/{tenant_id}`
- `GET /api/v1/analytics/report/{tenant_id}`
- `PUT /api/v1/analytics/{id}`
- `DELETE /api/v1/analytics/{id}`

### Integration APIs

- `GET /api/v1/integration/health`
- `GET /api/v1/integration/score/{tenant_id}`
- `GET /api/v1/integration/metrics`
- `POST /api/v1/integration/analytics/flush/{tenant_id}`

### WebSocket feed

- `ws://127.0.0.1:8000/ws/{tenant_id}?token=<JWT>`

JWT tokens must carry the tenant association, and the tenant in the path must match the token claim.

## Environment configuration

The app uses environment variables loaded from `.env` via `pydantic-settings`.

A base template is provided in `.env.example`.

Key variables include:

- `PROJECT_NAME`
- `VERSION`
- `ENVIRONMENT`
- `DATABASE_URL`
- `POSTGRES_DSN`
- `REDIS_URL`
- `KAFKA_BOOTSTRAP_SERVERS`
- `KAFKA_ENABLE`
- `SECRET_KEY`
- `CLICKHOUSE_URL`
- `RATE_LIMIT_WINDOW_SECONDS`
- `SCORE_CACHE_TTL_SECONDS`
- `WS_HEARTBEAT_SECONDS`

## Local development setup

### 1. Create environment and install dependencies

```powershell
Copy-Item .env.example .env
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt psycopg2-binary
```

### 2. Start supporting infrastructure

```powershell
docker compose up -d redis redpanda redpanda-init postgres
```

This starts:

- Redis on `localhost:6379`
- Redpanda on `localhost:19092`
- Postgres on `localhost:5432`

### 3. Start the FastAPI app

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Open the API docs

- Swagger: `http://127.0.0.1:8000/api/docs`
- ReDoc: `http://127.0.0.1:8000/api/redoc`
- OpenAPI: `http://127.0.0.1:8000/api/openapi.json`

## Docker Compose run

The project includes a full runtime stack in `docker-compose.yml`:

```powershell
docker compose up --build
```

This includes the API service plus Redis, Redpanda, Redpanda topic initialization, ClickHouse, and Postgres.

## Database

Current local default:

- SQLite file: `cybreach.db`

Docker Compose also includes PostgreSQL for a more production-like setup, with `DATABASE_URL` set to the Postgres connection string in the `api` service.

## Testing

The project includes pytest-based tests under `tests/`.

Run the suite with:

```powershell
pytest
```

Integration-focused verification is also described in `INTEGRATION_RUNBOOK.md`.

## Notes

- The app is a backend-oriented microservice and is designed to integrate with external producers and consumers through Kafka events.
- Redis is not only used for cache/rate-limit state; it is also used by the WebSocket manager for tenant session tracking.
- The root-level React files are present as UI artifacts or prototype assets, but they are not the main runtime for this repository’s backend service.

## Quick reference

```text
App root:         http://127.0.0.1:8000/
Health:           http://127.0.0.1:8000/api/v1/health
Integration:      http://127.0.0.1:8000/api/v1/integration/health
Docs:             http://127.0.0.1:8000/api/docs
Metrics:          http://127.0.0.1:8000/metrics
WebSocket:        ws://127.0.0.1:8000/ws/{tenant_id}?token=<JWT>
```

For end-to-end event validation and sample payloads, see `INTEGRATION_RUNBOOK.md`.

