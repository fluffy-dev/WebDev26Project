from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from balances.domain.entities import BalanceEntity, TransactionEntity


class AbstractBalanceRepository(ABC):
    """Port for balance persistence operations."""

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> BalanceEntity | None:
        """Return the balance for a user, or None if it does not exist.

        Args:
            user_id: The user's UUID.

        Returns:
            A BalanceEntity, or None.
        """

    @abstractmethod
    def create(self, user_id: UUID) -> BalanceEntity:
        """Persist a new zero-balance wallet for a user.

        Args:
            user_id: The user's UUID.

        Returns:
            The newly created BalanceEntity.
        """

    @abstractmethod
    def increment(self, user_id: UUID, amount: int) -> None:
        """Atomically add credits to a user's balance using a DB-level expression.

        Args:
            user_id: Target user's UUID.
            amount: Positive integer credits to add.
        """


class AbstractTransactionRepository(ABC):
    """Port for transaction persistence operations."""

    @abstractmethod
    def create(
        self,
        event_id: UUID,
        balance_id: UUID,
        amount: int,
        transaction_type: str,
    ) -> TransactionEntity:
        """Persist a new transaction record.

        Args:
            event_id: Kafka event UUID, stored as the idempotency key.
            balance_id: The owning balance's UUID.
            amount: Positive integer credits.
            transaction_type: "CREDIT" or "DEBIT".

        Returns:
            The created TransactionEntity.
        """

    @abstractmethod
    def list_by_user_id(
        self,
        user_id: UUID,
        start: int,
        limit: int,
    ) -> tuple[int, list[TransactionEntity]]:
        """Return a page of transactions and the total count for a user.

        Args:
            user_id: The user whose transactions to fetch.
            start: Zero-based offset.
            limit: Maximum number of results.

        Returns:
            A tuple of (total_count, transactions).
        """
