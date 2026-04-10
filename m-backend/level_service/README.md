# Level Service — Complete Service Documentation

## Purpose

Manages typing level content and records user attempts (submits).
Responsible for:
- Listing and paginating available levels
- Returning individual level data
- Accepting and scoring user typing attempts
- Publishing reward events to Kafka when a submit earns credits

This service has **no authentication logic**. It receives identity via trusted headers
injected by Traefik after the auth service validates the token.

---

## Technology Stack

| Concern          | Choice                      | Reason                                              |
|------------------|-----------------------------|-----------------------------------------------------|
| Framework        | Django 5 + DRF 3.15         | Consistent with other services                      |
| Database         | PostgreSQL 16               | Stores levels and submit history                    |
| ORM              | Django ORM (psycopg3)       | F() expressions for safe credit calculation         |
| Event publishing | confluent-kafka             | Publishes `submit.rewarded` after positive rewards  |
| Config           | python-decouple             | `.env`-based                                        |
| Testing          | pytest-django + factory-boy |                                                     |
| WSGI server      | Gunicorn                    |                                                     |

---

## Directory Structure

```
level_service/
├── Dockerfile
├── entrypoint.sh
├── requirements.txt
├── pytest.ini
├── .env
└── src/
    ├── manage.py
    ├── config/
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── wsgi.py
    │   ├── urls.py
    │   └── settings/
    │       ├── __init__.py
    │       ├── base.py
    │       ├── development.py
    │       └── production.py
    └── levels/
        ├── admin.py
        ├── apps.py
        ├── domain/
        │   ├── entities.py         # LevelEntity, SubmitEntity
        │   ├── repositories.py     # AbstractLevelRepository, AbstractSubmitRepository
        │   └── services.py         # RewardCalculator (pure domain logic)
        ├── application/
        │   ├── dto.py              # SubmitLevelDTO, LevelResponseDTO, SubmitResponseDTO
        │   ├── exceptions.py       # LevelNotFoundError, etc.
        │   └── use_cases/
        │       ├── list_levels.py      # ListLevelsUseCase
        │       ├── get_level.py        # GetLevelUseCase
        │       └── submit_level.py     # SubmitLevelUseCase
        ├── infrastructure/
        │   ├── models.py               # Level, Submit Django models
        │   ├── repositories.py         # DjangoLevelRepository, DjangoSubmitRepository
        │   └── kafka/
        │       └── producer.py         # SubmitEventProducer
        ├── presentation/
        │   ├── serializers.py
        │   ├── views.py
        │   ├── urls.py
        │   └── exception_handler.py
        └── tests/
            ├── conftest.py
            ├── factories.py
            ├── test_reward_calculator.py   # pure unit tests
            ├── test_use_cases.py
            └── test_views.py
```

---

## Domain Model

```
LevelEntity (frozen dataclass)
  id           : UUID
  text         : str       — the passage the user types
  cost         : int       — maximum credits this level can award
  goal_wpm     : int       — target words-per-minute
  created_at   : datetime
  updated_at   : datetime

SubmitEntity (frozen dataclass)
  id                : UUID
  level_id          : UUID
  user_id           : UUID
  wpm               : int
  rewarded_credits  : int  — computed, stored after calculation
  created_at        : datetime
```

---

## Reward Calculation

Domain service `RewardCalculator` lives in `domain/services.py`.
Pure Python, no side effects, fully unit-testable.

```
rewarded_credits = floor( min(1.0, user_wpm / goal_wpm) * level_cost )
```

- If `user_wpm >= goal_wpm`: full `level_cost` awarded.
- If `user_wpm < goal_wpm`: proportional fraction of `level_cost`.
- If the user has **already submitted this level** (any prior Submit record for same user+level):
  `rewarded_credits = 0`. They can retype for practice, no farming.

The "already submitted" check happens in `SubmitLevelUseCase` before calling `RewardCalculator`.

---

## Database Schema

```sql
CREATE TABLE levels (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text        TEXT NOT NULL,
    cost        INTEGER NOT NULL CHECK (cost > 0),
    goal_wpm    INTEGER NOT NULL CHECK (goal_wpm > 0),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE submits (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level_id          UUID NOT NULL REFERENCES levels(id),
    user_id           UUID NOT NULL,         -- not FK, lives in auth service
    wpm               INTEGER NOT NULL CHECK (wpm > 0),
    rewarded_credits  INTEGER NOT NULL DEFAULT 0,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Prevent double-reward: partial index for existence check
CREATE INDEX idx_submits_user_level ON submits(user_id, level_id);
```

`user_id` is stored as a plain UUID column (not a FK) because users live in a separate
service and database. Referential integrity is enforced at the application level.

---

## API Endpoints

All endpoints require a valid JWT. Traefik validates it via ForwardAuth and injects:
- `X-User-Id`: UUID string of the authenticated user
- `X-Username`: username string

Views read identity from these headers. No JWT parsing in this service.

---

### `GET /level`

Returns a paginated list of levels.

**Query params**
- `start` (int, default 0) — offset
- `limit` (int, default 20, max 100) — page size

**Response `200`**
```json
{
  "count": 42,
  "results": [
    {
      "id": "uuid",
      "text": "The quick brown fox...",
      "cost": 100,
      "goal_wpm": 60,
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

---

### `GET /level/{uuid}`

Returns a single level by id.

**Response `200`**
```json
{
  "id": "uuid",
  "text": "...",
  "cost": 100,
  "goal_wpm": 60,
  "created_at": "...",
  "updated_at": "..."
}
```

**Errors**
- `404` — level not found

---

### `POST /level`

Submits a typing attempt for a level.
`user_id` is read from the `X-User-Id` header (injected by Traefik).

**Request**
```json
{
  "level_id": "uuid",
  "wpm": 72
}
```

**Response `201`**
```json
{
  "id": "uuid",
  "level_id": "uuid",
  "user_id": "uuid",
  "wpm": 72,
  "rewarded_credits": 100,
  "created_at": "..."
}
```

**Notes**
- If user has submitted this level before: `rewarded_credits` will be `0`.
- A Kafka event is only published when `rewarded_credits > 0`.

**Errors**
- `404` — level_id not found
- `400` — validation failure (wpm missing, non-positive, etc.)

---

## Kafka Events Published

### Topic: `submit.rewarded`

Published by `SubmitEventProducer` only when `rewarded_credits > 0`.

```json
{
  "event": "submit.rewarded",
  "event_id": "submit-uuid",
  "user_id": "uuid",
  "username": "alice",
  "amount": 80
}
```

**Message key**: `user_id`

**Field notes**
- `event_id` is the Submit's UUID. Used as idempotency key in balance and leaderboard services.
  One submit → one reward event. Consumers deduplicate on this field.

**Consumers**: `balance_service`, `leaderboard_service`

---

## Inter-Service Communication

This service **produces** events. It does not consume any.
It does not make HTTP calls to any other service.

```
Client → Traefik [auth-verify middleware] → GET /level
Client → Traefik [auth-verify middleware] → GET /level/{uuid}
Client → Traefik [auth-verify middleware] → POST /level
                                             ↓ (rewarded_credits > 0)
                                         Kafka [submit.rewarded]
                                             ↓                  ↓
                                     balance_service    leaderboard_service
```

Identity flow:
```
Client sends: Authorization: Bearer <token>
Traefik calls: GET http://auth_service/verify  (Authorization header forwarded)
Auth service returns: 200, X-User-Id, X-Username
Traefik forwards to level_service with: X-User-Id, X-Username headers set
level_service reads: request.headers["X-User-Id"]
```

---

## Code Style & Principles

Identical to auth service. Key points specific to this service:

- **`RewardCalculator`** is a pure domain service — no DB, no Kafka. Input: wpm, goal_wpm, cost.
  Output: int. Covered by pure unit tests only.
- **`SubmitLevelUseCase`** is the only place that checks prior submissions and calls
  the calculator. Keep this logic here, never leak it into views.
- **Views never do math.** Views validate, delegate, serialize.
- **`user_id` comes from headers**, never from request body. If a client sends `user_id`
  in the body, it is ignored.
- Pagination uses `start` / `limit` offsets. Keep `limit` capped at 100 server-side.

---

## CLI Setup Sequence

```bash
mkdir level_service && cd level_service
python3.12 -m venv .venv && source .venv/bin/activate

pip install django==5.0.* djangorestframework==3.15.* \
  psycopg[binary]==3.1.* confluent-kafka==2.4.* \
  python-decouple==3.8 pytest-django==4.8.* \
  pytest-mock==3.14.* factory-boy==3.3.* Faker==25.0.*
pip freeze > requirements.txt

mkdir src && cd src
django-admin startproject config .
python manage.py startapp levels

python manage.py makemigrations levels
python manage.py migrate

pytest src/levels/tests/ -v
```

---

## Environment Variables

```env
DJANGO_ENV=development
SECRET_KEY=
ALLOWED_HOSTS=*
POSTGRES_DB=level_db
POSTGRES_USER=level_user
POSTGRES_PASSWORD=
POSTGRES_HOST=postgres_level
POSTGRES_PORT=5432
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```