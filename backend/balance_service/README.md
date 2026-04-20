# Balance Service — Complete Service Documentation

## Purpose

Acts as each user's credit wallet. Responsible for:
- Creating a zero-balance wallet when a new user registers (via Kafka)
- Crediting rewards when a submit is rewarded (via Kafka)
- Serving a user's current balance over HTTP
- Serving a paginated transaction history over HTTP

**This service has no HTTP write endpoints.** All balance mutations arrive via Kafka.
This is a deliberate design decision: the wallet can only grow through the game loop,
preventing any accidental or malicious balance manipulation via HTTP.

---

## Technology Stack

| Concern          | Choice                        | Reason                                                  |
|------------------|-------------------------------|----------------------------------------------------------|
| Framework        | Django 5 + DRF 3.15           | Consistent with other services                           |
| Database         | PostgreSQL 16                 | ACID transactions for balance atomicity                  |
| ORM              | Django ORM (psycopg3)         | F() expressions for DB-level atomic increments           |
| Event consuming  | confluent-kafka               | Consumes `user.registered` and `submit.rewarded`         |
| Consumer runner  | Django management command     | Long-running process in a separate container/process     |
| Config           | python-decouple               |                                                          |
| Testing          | pytest-django + factory-boy   |                                                          |
| WSGI server      | Gunicorn                      | HTTP read endpoints only                                 |

---

## Directory Structure

```
balance_service/
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
    └── balances/
        ├── admin.py
        ├── apps.py
        ├── domain/
        │   ├── entities.py         # BalanceEntity, TransactionEntity
        │   └── repositories.py     # AbstractBalanceRepository, AbstractTransactionRepository
        ├── application/
        │   ├── dto.py              # BalanceResponseDTO, TransactionResponseDTO
        │   ├── exceptions.py       # BalanceNotFoundError, DuplicateEventError
        │   └── use_cases/
        │       ├── create_balance.py   # CreateBalanceUseCase — triggered by user.registered
        │       ├── credit_balance.py   # CreditBalanceUseCase — triggered by submit.rewarded
        │       ├── get_balance.py      # GetBalanceUseCase
        │       └── list_transactions.py # ListTransactionsUseCase
        ├── infrastructure/
        │   ├── models.py               # Balance, Transaction Django models
        │   ├── repositories.py         # DjangoBalanceRepository, DjangoTransactionRepository
        │   └── kafka/
        │       └── consumer.py         # BalanceEventConsumer (management command)
        ├── presentation/
        │   ├── serializers.py
        │   ├── views.py
        │   ├── urls.py
        │   └── exception_handler.py
        └── tests/
            ├── conftest.py
            ├── factories.py
            ├── test_use_cases.py
            └── test_views.py
```

---

## Domain Model

```
BalanceEntity (frozen dataclass)
  id          : UUID
  user_id     : UUID
  balance     : int       — always >= 0, never negative
  updated_at  : datetime

TransactionEntity (frozen dataclass)
  id          : UUID
  event_id    : UUID      — idempotency key, unique constraint in DB
  balance_id  : UUID
  amount      : int       — always positive
  type        : Literal["CREDIT", "DEBIT"]
  created_at  : datetime
```

`TransactionType.CREDIT` = balance increases (submit reward, registration bonus if any).
`TransactionType.DEBIT` = balance decreases (reserved for future spend mechanic, not used now).

---

## Database Schema

```sql
CREATE TABLE balances (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID UNIQUE NOT NULL,
    balance     INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TYPE transaction_type AS ENUM ('CREDIT', 'DEBIT');

CREATE TABLE transactions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id    UUID UNIQUE NOT NULL,   -- idempotency key from Kafka message
    balance_id  UUID NOT NULL REFERENCES balances(id),
    amount      INTEGER NOT NULL CHECK (amount > 0),
    type        transaction_type NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Atomic Balance Update

Balance is **never read then written in Python**. The ORM `F()` expression translates to:

```sql
UPDATE balances
SET balance = balance + 80,
    updated_at = NOW()
WHERE user_id = '<uuid>';
```

This is a single atomic statement. No race condition. No `SELECT` + `UPDATE` window.

---

## Kafka Topics Consumed

### `user.registered` (and/or `dbz.public.users`)

Triggers `CreateBalanceUseCase`.

```json
{
  "event": "user.registered",
  "user_id": "uuid",
  "username": "alice"
}
```

Creates a `Balance` row with `balance = 0` for the given `user_id`.
Idempotent: if the balance already exists for that `user_id`, the event is silently skipped.

---

### `submit.rewarded`

Triggers `CreditBalanceUseCase`.

```json
{
  "event": "submit.rewarded",
  "event_id": "submit-uuid",
  "user_id": "uuid",
  "username": "alice",
  "amount": 80
}
```

Creates a `Transaction` with `type=CREDIT` and atomically increments `balances.balance`.
`event_id` must be unique. If a duplicate arrives (Kafka retry), the `UNIQUE` constraint
on `transactions.event_id` catches it. The consumer catches the `IntegrityError` and commits
the Kafka offset without re-processing — this is the idempotency guarantee.

---

## API Endpoints

All endpoints require a valid JWT. `X-User-Id` is injected by Traefik.

---

### `GET /balance/{user_id}`

Returns the current balance for a user.

**Response `200`**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "balance": 420,
  "updated_at": "..."
}
```

**Errors**
- `404` — no balance record found for this user_id (user may not have registered yet)

---

### `GET /transactions/{user_id}`

Returns paginated transaction history.

**Query params**
- `start` (int, default 0)
- `limit` (int, default 20, max 100)

**Response `200`**
```json
{
  "count": 15,
  "results": [
    {
      "id": "uuid",
      "event_id": "uuid",
      "amount": 80,
      "type": "CREDIT",
      "created_at": "..."
    }
  ]
}
```

---

## Kafka Consumer — Running as Management Command

The consumer runs as a **separate process** alongside Gunicorn.
It is a Django management command so it has full ORM access.

```bash
# In the container, entrypoint.sh starts both:
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 &
python manage.py run_balance_consumer
```

Or run as a separate container with `command: python manage.py run_balance_consumer`.

Consumer logic:
1. Poll Kafka for messages.
2. Deserialize JSON payload.
3. Route by `event` field to the appropriate use case.
4. If use case succeeds: commit Kafka offset.
5. If `IntegrityError` on `event_id` duplicate: log as INFO, commit offset (idempotent skip).
6. If any other exception: log as ERROR, do **not** commit offset (message retried).

---

## Inter-Service Communication

This service **consumes** events. It does not produce any.
It does not make HTTP calls to any other service.

```
auth_service / Debezium → Kafka [user.registered]  → balance_service consumer
level_service            → Kafka [submit.rewarded]  → balance_service consumer

Client → Traefik [auth-verify] → GET /balance/{user_id}
Client → Traefik [auth-verify] → GET /transactions/{user_id}
```

---

## Idempotency Strategy

| Scenario                          | Handling                                             |
|-----------------------------------|------------------------------------------------------|
| Duplicate `user.registered` event | `user_id` UNIQUE on balances; skip if exists         |
| Duplicate `submit.rewarded` event | `event_id` UNIQUE on transactions; catch IntegrityError, commit offset |
| Consumer crash after processing but before commit | Message replayed; duplicate caught by DB constraint |
| Consumer crash before processing  | Message replayed from last committed offset; processed normally |

---

## Code Style & Principles

- **No HTTP write path** — enforced at the URL configuration level. `POST /balance` does not exist.
- **Balance mutation only via use cases** triggered by Kafka events, never directly.
- **`F()` expressions** for all balance updates — never fetch-then-set.
- **Idempotency over reliability** — prefer committing and skipping duplicates over
  blocking the consumer queue on a repeated message.
- **Transaction type enum** at the model level — future DEBIT support requires no schema change.
- **Consumer and HTTP server run as separate processes** — they scale independently.
  Consumer parallelism is controlled by Kafka partition count.

---

## CLI Setup Sequence

```bash
mkdir balance_service && cd balance_service
python3.12 -m venv .venv && source .venv/bin/activate

pip install django==5.0.* djangorestframework==3.15.* \
  psycopg[binary]==3.1.* confluent-kafka==2.4.* \
  python-decouple==3.8 pytest-django==4.8.* \
  pytest-mock==3.14.* factory-boy==3.3.*
pip freeze > requirements.txt

mkdir src && cd src
django-admin startproject config .
python manage.py startapp balances

python manage.py makemigrations balances
python manage.py migrate

pytest src/balances/tests/ -v
```

---

## Environment Variables

```env
DJANGO_ENV=development
SECRET_KEY=
ALLOWED_HOSTS=*
POSTGRES_DB=balance_db
POSTGRES_USER=balance_user
POSTGRES_PASSWORD=
POSTGRES_HOST=postgres_balance
POSTGRES_PORT=5432
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_GROUP_ID=balance-service
KAFKA_TOPIC_USER_REGISTERED=user.registered
KAFKA_TOPIC_SUBMIT_REWARDED=submit.rewarded
```