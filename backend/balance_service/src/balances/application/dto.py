from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BalanceResponseDTO:
    """Wire representation of a user's balance.

    Args:
        id: Balance record UUID.
        user_id: Owning user's UUID.
        balance: Current credit total.
        updated_at: Timestamp of last mutation.
    """

    id: UUID
    user_id: UUID
    balance: int
    updated_at: datetime


@dataclass(frozen=True)
class TransactionResponseDTO:
    """Wire representation of a single transaction.

    Args:
        id: Transaction record UUID.
        event_id: Source Kafka event UUID.
        amount: Credits moved.
        type: "CREDIT" or "DEBIT".
        created_at: Timestamp of the transaction.
    """

    id: UUID
    event_id: UUID
    amount: int
    type: str
    created_at: datetime


@dataclass(frozen=True)
class TransactionListDTO:
    """Paginated transaction list.

    Args:
        count: Total number of transactions for the user.
        results: Current page of transactions.
    """

    count: int
    results: list[TransactionResponseDTO]
