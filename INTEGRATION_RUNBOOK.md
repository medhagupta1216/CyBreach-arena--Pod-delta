# Integration Runbook (Pod Delta – Dev 4)

This runbook is for a new developer bringing up Kafka/Redpanda consumption, Redis coordination, and the live WebSocket server, then proving the three architecture flows.

## 1. Prerequisites

- Python 3.11+
- Docker Desktop (Redpanda + Redis)
- Optional: `kcat` / Redpanda `rpk` for producing test events

## 2. Start infrastructure

```bash
cp .env.example .env
docker compose up -d redis redpanda redpanda-init
```

Confirm:

```bash
docker compose ps
```

Redpanda is advertised at `localhost:19092`. Redis is `localhost:6379`.

Topics created by `redpanda-init` include every consume/publish topic plus `{topic}.dlt`.

## 3. Start the API (consumer + WebSocket)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On startup the process:

1. Connects to Redis
2. Starts the WebSocket manager (Redis pub/sub fan-out)
3. Starts the Kafka producer (`acks=all`)
4. Starts the consumer group `pod-delta-integration`
5. Schedules a 24h analytics flush loop

### Health

```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/integration/health
curl http://127.0.0.1:8000/metrics
```

Healthy Redis + Kafka shows `"kafka_producer": true` and `"kafka_consumer": true`. If Kafka is down the API still serves Notification/Analytics REST; integration is `degraded`.

## 4. Mint a tenant JWT

The WebSocket and cached-score endpoints reuse `app.core.security`. Example:

```bash
python -c "from jose import jwt; from app.core.settings import settings; print(jwt.encode({'sub':'42','tenant_id':'tenant-demo'}, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM))"
```

Store the token as `TOKEN`.

## 5. Verify Flow A – Notifications

Open a WebSocket (in-app channel):

```bash
# Example with websocat
websocat "ws://127.0.0.1:8000/ws/tenant-demo?token=$TOKEN"
```

Produce a wallet event (Docker Redpanda):

```bash
docker compose exec redpanda rpk topic produce wallet.transaction --brokers redpanda:9092
```

Paste one line of JSON, then Ctrl-D:

```json
{"event_id":"wallet-1","event_version":"1.0","event_type":"wallet.transaction","tenant_id":"tenant-demo","correlation_id":"corr-1","occurred_at":"2026-09-18T10:00:00Z","source":"pod-alpha","transaction_id":"txn-1","amount":100,"currency":"USD","direction":"credit","user_id":42}
```

Expect:

1. Notification Hub row created (`GET /api/v1/notifications/user/42`)
2. WebSocket message `{ "type": "notification", ... }`
3. Kafka topic `notification.sent` contains a validated payload
4. Repeating the same `event_id` is a no-op (Redis idempotency)
5. Bursting more than `RATE_LIMIT_MAX_EVENTS` in 60s emits `notification.sent` with `rate_limited: true` and Redis key `rate_limit:tenant-demo:wallet.transaction`

Also try `achievement.awarded`, `engagement.lifecycle`, and `engagement.completed`.

## 6. Verify Flow B – Score display

Produce:

```json
{"event_id":"score-1","event_type":"mod3.score","tenant_id":"tenant-demo","correlation_id":"corr-score","occurred_at":"2026-09-18T10:05:00Z","source":"module-3","score":81.5,"previous_score":77.0,"trend":"up","components":{"identity":80,"detection":83}}
```

on topic `mod3.score`.

Expect:

1. Redis `GET score:tenant-demo` returns the full payload (TTL 3600)
2. WebSocket `{ "type": "score_update", "score": 81.5, ... }`
3. Topic `score.displayed` published (`push_delivered` true if a socket was connected)
4. Drill-down:

```bash
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/v1/integration/score/tenant-demo
```

Tenant mismatch returns 403.

## 7. Verify Flow C – Analytics

Consumed events are buffered at `analytics:buffer:{tenant_id}`. Flush on demand (does not run ClickHouse queries; it hands off to the existing Analytics Engine):

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/v1/integration/analytics/flush/tenant-demo
```

Expect `analytics.report` on Kafka and a record via `GET /api/v1/analytics/tenant/tenant-demo` (or dashboard routes).

The scheduled path uses `ANALYTICS_FLUSH_INTERVAL_SECONDS` (default 86400).

## 8. Leaderboard / benchmark live updates

Produce `leaderboard.updated` or `benchmark.computed` with `tenant_id: tenant-demo`. The WebSocket client should receive `leaderboard_updated` / `benchmark_computed`. No Notification Hub send unless you extend handlers.

## 9. Dead letters

Send invalid JSON (missing `tenant_id` or `score: 200`). Consumer commits the offset and publishes to `mod3.score.dlt` (or the matching `{topic}.dlt`). Check Prometheus `pod_delta_events_dlt_total`.

## 10. Multi-instance WebSocket

Run a second uvicorn on port 8001 with the same `REDIS_URL`. Connect a client to instance A, publish a score from Kafka. Instance B publishes on `ws:tenant:{tenant_id}`; instance A delivers locally. Session hash lives in `ws_session:{tenant_id}`.

## 11. Tests (no Docker required)

```bash
pytest -q
```

Unit coverage: event contracts, sliding-window limiter, score cache, score flow, WebSocket fan-out. Integration-style tests mock Kafka and use FakeRedis for consumer dispatch, DLT, and idempotency.

## 12. Configuration map

| Variable | Meaning |
|---|---|
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:19092` from compose |
| `KAFKA_CONSUMER_GROUP` | `pod-delta-integration` |
| `KAFKA_ENABLE` | Set `false` to skip broker connections |
| `REDIS_URL` | Rate limit, score cache, WS |
| `DATABASE_URL` / `POSTGRES_DSN` | Preferences + delivery logs |
| `CLICKHOUSE_URL` | Documented for the platform; aggregations stay with Analytics |
| `SECRET_KEY` | JWT for `/ws/{tenant_id}` |

## 13. What this service does not do

- React dashboard components
- SMTP / SendGrid / customer webhook HTTP delivery internals
- ClickHouse SQL
- Resilience score math
- Wallet ledger, security tests, leaderboard ranking
