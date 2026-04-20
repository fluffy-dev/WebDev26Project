from __future__ import annotations

from uuid import UUID

from balances.application.dto import TransactionListDTO, TransactionResponseDTO
from balances.domain.repositories import AbstractTransactionRepository


class ListTransactionsUseCase:
    """Return a paginated transaction history for a user.

    Args:
        transaction_repository: Transaction persistence port.
    """

    def __init__(self, transaction_repository: AbstractTransactionRepository) -> None:
        self._transaction_repository = transaction_repository

    def execute(self, user_id: UUID, start: int, limit: int) -> TransactionListDTO:
        """Fetch and return a page of transactions.

        Args:
            user_id: The user whose history to retrieve.
            start: Zero-based offset into the full result set.
            limit: Maximum number of results to return (capped at 100 by the view).

        Returns:
            A TransactionListDTO with count and current-page results.
        """
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
