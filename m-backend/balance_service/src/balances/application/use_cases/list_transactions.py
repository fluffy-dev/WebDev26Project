from __future__ import annotations

from uuid import UUID

from balances.application.dto import TransactionListDTO, TransactionResponseDTO
from balances.domain.repositories import AbstractTransactionRepository


class ListTransactionsUseCase:
    """Return a paginated transaction history for a user."""

    def __init__(self, transaction_repository: AbstractTransactionRepository) -> None:
        self._transaction_repository = transaction_repository

    def execute(self, user_id: UUID, start: int, limit: int) -> TransactionListDTO:
        """Fetch and return a page of transactions."""
        count, transactions = self._transaction_repository.list_by_user_id(
            user_id=user_id,
            start=start,
            limit=limit,
        )
        return TransactionListDTO(
            count=count,
            results=[
                TransactionResponseDTO(
                    id=tx.id,
                    event_id=tx.event_id,
                    amount=tx.amount,
                    type=tx.type,
                    created_at=tx.created_at,
                )
                for tx in transactions
            ],
        )
