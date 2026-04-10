# Typing App — Project Overview

## What This Is

A typing practice platform built as a microservices system.
Users register, type through levels, earn credits based on speed, and compete on a daily leaderboard.

---

## High-Level Architecture

```
Internet
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                        DMZ                              │
│                                                         │
│   ┌──────────────────────────────────────────────────┐  │
│   │              Traefik (Reverse Proxy)             │  │
│   │                                                  │  │
│   │  1. Strips X-User-Id / X-Username from clients   │  │
│   │  2. Routes /auth/* → auth_service (no auth check)│  │
│   │  3. All other routes → ForwardAuth middleware     │  │
│   │     → calls auth_service GET /verify             │  │
│   │     → injects X-User-Id, X-Username on success   │  │
│   │     → rejects with 401 on failure                │  │
│   └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
    │               │                  │               │
    ▼               ▼                  ▼               ▼
auth_service  level_service    balance_service  leaderboard_service
(postgres)    (postgres)       (postgres)       (redis only)
    │               │
    │               │
    └───────┬───────┘
            ▼
          Kafka
            │
    ┌───────┴────────┐
    ▼                ▼
balance_service  leaderboard_service
  (consumer)        (consumer)

Debezium (CDC) ──► Kafka [dbz.public.users] ──► balance_service (consumer)
(monitors auth postgres)
```

---

## Services at a Glance

| Service             | Role                          | Owns                    | DB          | Kafka role       |
|---------------------|-------------------------------|-------------------------|-------------|------------------|
| `auth_service`      | Identity provider             | Users, ProfileImages    | Postgres    | Producer         |
| `level_service`     | Game content + scoring        | Levels, Submits         | Postgres    | Producer         |
| `balance_service`   | User wallet                   | Balances, Transactions  | Postgres    | Consumer only    |
| `leaderboard_service`| Daily rankings               | Redis ZSET              | Redis only  | Consumer only    |

---

## Network Layout

Two Docker networks:

```
dmz        — Traefik ↔ internet. Only Traefik has a port exposed to the host.
internal   — All services, databases, Kafka, Redis. Not reachable from outside.
```

Traefik sits on both networks. Services on `internal` only — they cannot be accessed
directly from the internet. All traffic passes through Traefik.

---

## Authentication & Identity Flow

```
1. Client → POST /auth/login
   Traefik routes to auth_service (no auth check for /auth/* prefix)
   auth_service returns { access_token, refresh_token, user_id }

2. Client → GET /level (with Authorization: Bearer <token>)
   Traefik: strips any X-User-Id / X-Username headers from client (security)
   Traefik: calls GET http://auth_service/verify  (ForwardAuth)
     auth_service validates JWT
     returns: 200, X-User-Id: <uuid>, X-Username: <name>
   Traefik: injects those headers, forwards request to level_service
   level_service: reads user_id from request.headers["X-User-Id"]
   level_service: does NOT touch JWT
```

- JWT is parsed **only** in auth_service.
- All other services receive `X-User-Id` and `X-Username` as trusted headers.
- No shared JWT secret across services.

---

## Kafka Topics & Event Flow

```
Topic: user.registered
  Producer:  auth_service (UserEventProducer)
  Also CDC:  Debezium → dbz.public.users (parallel capture of same INSERT)
  Consumers: balance_service → creates Balance(user_id, balance=0)

Topic: submit.rewarded
  Producer:  level_service (SubmitEventProducer) — only when rewarded_credits > 0
  Consumers: balance_service   → credits the wallet
             leaderboard_service → increments Redis ZSET score
```

### Event Schema: `user.registered`

```json
{
  "event": "user.registered",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "alice"
}
```

### Event Schema: `submit.rewarded`

```json
{
  "event": "submit.rewarded",
  "event_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "alice",
  "amount": 80
}
```

`event_id` = Submit's UUID. Unique per submit. Used by all consumers as idempotency key.

---

## Reward Calculation (Level Service)

```
rewarded_credits = floor( min(1.0, user_wpm / goal_wpm) * level_cost )
```

- Full reward if user meets or exceeds the target WPM.
- Proportional reward if below target.
- **Zero reward** if user has submitted this level before (no farming).
- Kafka event only published when `rewarded_credits > 0`.

---

## Idempotency Guarantees

| Consumer         | Event                | Idempotency mechanism                        |
|------------------|----------------------|----------------------------------------------|
| balance_service  | `user.registered`    | UNIQUE constraint on `balances.user_id`       |
| balance_service  | `submit.rewarded`    | UNIQUE constraint on `transactions.event_id`  |
| leaderboard      | `submit.rewarded`    | Redis SET `processed_events:daily` checked before ZINCRBY |

All consumers use `enable.auto.commit=false` and commit offset only after successful processing.
On duplicate detection (IntegrityError or SET membership), offset is committed without re-processing.

---

## Daily Leaderboard Reset

Runs at **00:00 UTC** every day.

```
RENAME leaderboard:daily → leaderboard:archive:YYYY-MM-DD
EXPIRE leaderboard:archive:YYYY-MM-DD 604800  (7 days)
```

`RENAME` is atomic — no empty-leaderboard window. The next `ZINCRBY` recreates the key.
Archives are kept for 7 days, then evicted by Redis TTL.

---

## Debezium CDC

Monitors `postgres_auth.public.users` table.
Every committed `INSERT` produces a message on `dbz.public.users`.
This is the primary mechanism for `balance_service` to create wallets.
The application-level `user.registered` Kafka publish from `auth_service` is belt-and-suspenders.
Consumers deduplicate via `UNIQUE(user_id)` on the balances table.

Register connector once after infrastructure is up:
```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @infra/debezium/users-connector.json
```

---

## Infrastructure Services

| Service        | Image                              | Purpose                                    |
|----------------|------------------------------------|--------------------------------------------|
| traefik        | traefik:v3.0                       | Reverse proxy, ForwardAuth, routing        |
| postgres_auth  | postgres:16-alpine                 | auth_service database                      |
| postgres_level | postgres:16-alpine                 | level_service database                     |
| postgres_balance | postgres:16-alpine               | balance_service database                   |
| redis          | redis:7-alpine                     | leaderboard ZSET + processed_events SET    |
| kafka          | confluentinc/cp-kafka:7.6.0        | Event bus                                  |
| zookeeper      | confluentinc/cp-zookeeper:7.6.0    | Kafka coordination                         |
| debezium       | debezium/connect:2.6               | CDC from postgres_auth                     |

---

## Shared Code Conventions (All Services)

### Architecture Pattern: DDD Layering

```
domain/          — pure Python entities + abstract repository interfaces
                   zero framework imports, fully unit-testable in isolation

application/     — use cases + DTOs + application exceptions
                   depends on domain interfaces only
                   orchestrates domain logic, calls repositories and producers

infrastructure/  — concrete implementations: Django ORM repos, Kafka producers/consumers, Redis
                   depends on application + domain
                   the only layer that imports Django, confluent_kafka, redis-py

presentation/    — DRF views, serializers, URL routing, exception handler
                   depends on application DTOs and use cases only
                   thin: validate input → call use case → serialize output
```

Inner layers never import from outer layers. This is strictly enforced.

### Code Style

- Python 3.12
- Google-style docstrings on all public methods
- Type hints on all function signatures
- No inline comments — code is self-documenting; docstrings explain *why*
- `frozen=True` dataclasses for entities and DTOs
- `pytest` with `pytest-django`; no `unittest.TestCase`
- `factory_boy` for test data; no raw `Model.objects.create()` in tests
- `python-decouple` for config; no `os.environ.get()` calls in code

### Dependency Injection

Use cases receive repositories and producers via `__init__`. Views instantiate concrete
implementations and pass them in. No DI container — the wiring is explicit and visible.

```python
# In views.py
use_case = SubmitLevelUseCase(
    level_repository=DjangoLevelRepository(),
    submit_repository=DjangoSubmitRepository(),
    event_producer=SubmitEventProducer(),
)
```

### Settings Split

Every service follows the same pattern:

```
config/settings/
  base.py         — shared: installed apps, DRF config, DB, Kafka
  development.py  — DEBUG=True, local file storage
  production.py   — HTTPS flags, S3
  __init__.py     — routes based on DJANGO_ENV env var
```

### Exception Handling

Each service defines `ApplicationError` subclasses in `application/exceptions.py`.
A `custom_exception_handler` in `presentation/exception_handler.py` maps them to HTTP
status codes via a `_STATUS_MAP` dict. Views never contain `try/except` for domain errors.

---

## Starting the System

```bash
# 1. Start infrastructure
docker compose up -d zookeeper kafka redis \
  postgres_auth postgres_level postgres_balance debezium

# 2. Wait for kafka to be ready, then start services
docker compose up -d auth_service level_service balance_service leaderboard_service traefik

# 3. Register Debezium connector (once)
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @infra/debezium/users-connector.json

# 4. Create Django superuser for auth admin (profile image management)
docker compose exec auth_service python manage.py createsuperuser

# 5. Access points
#   Traefik dashboard: http://localhost:8080
#   API:               http://localhost (port 80 via Traefik)
#   Auth admin:        http://localhost/admin  (routes through Traefik to auth_service)
```

---

## API Surface (All Routes via Traefik port 80)

| Method | Path                        | Auth | Service            |
|--------|-----------------------------|------|--------------------|
| POST   | /auth/login                 | No   | auth_service       |
| POST   | /auth/registration          | No   | auth_service       |
| POST   | /auth/refresh               | No   | auth_service       |
| GET    | /auth/users/{user_id}       | Yes  | auth_service       |
| GET    | /level                      | Yes  | level_service      |
| GET    | /level/{uuid}               | Yes  | level_service      |
| POST   | /level                      | Yes  | level_service      |
| GET    | /balance/{user_id}          | Yes  | balance_service    |
| GET    | /transactions/{user_id}     | Yes  | balance_service    |
| GET    | /leaderboard                | Yes  | leaderboard_service|

---

## Adding a New Service Checklist

1. Create service directory and run `django-admin startproject config .` inside `src/`
2. Run `python manage.py startapp <name>`
3. Copy `settings/` split pattern from any existing service
4. Create DDD layers: `domain/`, `application/`, `infrastructure/`, `presentation/`
5. Add `Dockerfile` and `entrypoint.sh` (identical pattern to existing services)
6. Add service to `docker-compose.yml` with Traefik labels
7. If it needs auth: add `auth-verify@file` middleware label in Traefik config
8. If it produces Kafka events: follow `SubmitEventProducer` pattern
9. If it consumes Kafka events: follow `KafkaEventConsumer` base class pattern
10. Write tests: pure unit tests for domain + use cases, integration tests for views