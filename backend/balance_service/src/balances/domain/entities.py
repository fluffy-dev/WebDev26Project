from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID


@dataclass(frozen=True)
class BalanceEntity:
    """Represents a user's current credit wallet.

    Args:
        id: Primary key UUID.
        user_id: The owning user's UUID (unique per user).
        balance: Non-negative integer credit total.
        updated_at: Timestamp of the last mutation.
    """

    id: UUID
    user_id: UUID
    balance: int
    updated_at: datetime


@dataclass(frozen=True)
class TransactionEntity:
    """An immutable record of a single balance change.

    Args:
        id: Primary key UUID.
        event_id: The Kafka event UUID used as the idempotency key.
        balance_id: Foreign key to the owning Balance.
        amount: Positive integer credit delta.
        type: Either "CREDIT" or "DEBIT".
        created_at: Timestamp of the transaction.
    """

    id: UUID
    event_id: UUID
    balance_id: UUID
    amount: int
    type: Literal["CREDIT", "DEBIT"]
    created_at: datetime
