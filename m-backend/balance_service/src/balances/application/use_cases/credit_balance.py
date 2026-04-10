from __future__ import annotations

from uuid import UUID

from balances.application.exceptions import BalanceNotFoundError
from balances.domain.repositories import AbstractBalanceRepository, AbstractTransactionRepository


class CreditBalanceUseCase:
    """Apply a rewarded-credit event to the user's wallet."""

    def __init__(
        self,
        balance_repository: AbstractBalanceRepository,
        transaction_repository: AbstractTransactionRepository,
    ) -> None:
        self._balance_repository = balance_repository
        self._transaction_repository = transaction_repository

    def execute(self, event_id: UUID, user_id: UUID, amount: int) -> None:
        """Increment balance and record transaction in a single DB transaction."""
        balance = self._balance_repository.get_by_user_id(user_id)
        if balance is None:
            raise BalanceNotFoundError(f"No balance found for user {user_id}")

        self._balance_repository.increment(user_id=user_id, amount=amount)
        self._transaction_repository.create(
            event_id=event_id,
            balance_id=balance.id,
            amount=amount,
            transaction_type="CREDIT",
        )
