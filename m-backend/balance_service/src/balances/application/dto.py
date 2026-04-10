from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BalanceResponseDTO:
    """Wire representation of a user's balance."""

    id: UUID
    user_id: UUID
    balance: int
    updated_at: datetime


@dataclass(frozen=True)
class TransactionResponseDTO:
    """Wire representation of a single transaction."""

    id: UUID
    event_id: UUID
    amount: int
    type: str
    created_at: datetime


@dataclass(frozen=True)
class TransactionListDTO:
    """Paginated transaction list."""

    count: int
    results: list[TransactionResponseDTO]
