from __future__ import annotations

from uuid import UUID

from balances.application.exceptions import BalanceNotFoundError
from balances.domain.repositories import AbstractBalanceRepository, AbstractTransactionRepository


class CreditBalanceUseCase:
    """Apply a rewarded-credit event to the user's wallet.

    Atomically increments the balance and records an immutable transaction.
    The UNIQUE constraint on transactions.event_id enforces idempotency at the
    database level; the consumer catches IntegrityError and commits the offset.

    Args:
        balance_repository: Balance persistence port.
        transaction_repository: Transaction persistence port.
    """

    def __init__(
        self,
        balance_repository: AbstractBalanceRepository,
        transaction_repository: AbstractTransactionRepository,
    ) -> None:
        self._balance_repository = balance_repository
        self._transaction_repository = transaction_repository

    def execute(self, event_id: UUID, user_id: UUID, amount: int) -> None:
        """Increment balance and record transaction in a single DB transaction.

        Args:
            event_id: Kafka event UUID used as the idempotency key.
            user_id: Target user's UUID.
            amount: Positive integer credits to add.

        Raises:
            BalanceNotFoundError: If the user has no wallet yet.
        """
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
