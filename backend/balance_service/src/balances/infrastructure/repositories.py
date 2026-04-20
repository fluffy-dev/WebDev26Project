from __future__ import annotations

from uuid import UUID

from django.db import transaction
from django.db.models import F

from balances.domain.entities import BalanceEntity, TransactionEntity
from balances.domain.repositories import AbstractBalanceRepository, AbstractTransactionRepository
from balances.infrastructure.models import Balance, Transaction


class DjangoBalanceRepository(AbstractBalanceRepository):
    """Django ORM implementation of balance persistence.

    Uses F() expressions for atomic increments — no Python-level
    read-then-write ever touches the balance field.
    """

    def get_by_user_id(self, user_id: UUID) -> BalanceEntity | None:
        """Fetch a balance by user UUID.

        Args:
            user_id: The owning user's UUID.

        Returns:
            A BalanceEntity if found, otherwise None.
        """
        try:
            row = Balance.objects.get(user_id=user_id)
        except Balance.DoesNotExist:
            return None
        return self._to_entity(row)

    def create(self, user_id: UUID) -> BalanceEntity:
        """Persist a new zero-balance wallet.

        Args:
            user_id: The owning user's UUID.

        Returns:
            The created BalanceEntity.
        """
        row = Balance.objects.create(user_id=user_id)
        return self._to_entity(row)

    def increment(self, user_id: UUID, amount: int) -> None:
        """Atomically add credits to the balance using a single UPDATE statement.

        Args:
            user_id: Target user's UUID.
            amount: Credits to add.
        """
        Balance.objects.filter(user_id=user_id).update(
            balance=F("balance") + amount,
        )

    @staticmethod
    def _to_entity(row: Balance) -> BalanceEntity:
        return BalanceEntity(
            id=row.id,
            user_id=row.user_id,
            balance=row.balance,
            updated_at=row.updated_at,
        )


class DjangoTransactionRepository(AbstractTransactionRepository):
    """Django ORM implementation of transaction persistence."""

    def create(
        self,
        event_id: UUID,
        balance_id: UUID,
        amount: int,
        transaction_type: str,
    ) -> TransactionEntity:
        """Persist a new transaction record.

        Args:
            event_id: Kafka event UUID (idempotency key).
            balance_id: UUID of the owning balance.
            amount: Positive integer credits.
            transaction_type: "CREDIT" or "DEBIT".

        Returns:
            The created TransactionEntity.
        """
        row = Transaction.objects.create(
            event_id=event_id,
            balance_id=balance_id,
            amount=amount,
            type=transaction_type,
        )
        return self._to_entity(row)

    def list_by_user_id(
        self,
        user_id: UUID,
        start: int,
        limit: int,
    ) -> tuple[int, list[TransactionEntity]]:
        """Return a page of transactions for a user ordered by newest first.

        Args:
            user_id: The user whose transactions to fetch.
            start: Zero-based offset.
            limit: Maximum number of results.

        Returns:
            Tuple of (total_count, page_results).
        """
        qs = Transaction.objects.filter(balance__user_id=user_id).order_by("-created_at")
        count = qs.count()
        page = qs[start : start + limit]
        return count, [self._to_entity(row) for row in page]

    @staticmethod
    def _to_entity(row: Transaction) -> TransactionEntity:
        return TransactionEntity(
            id=row.id,
            event_id=row.event_id,
            balance_id=row.balance_id,
            amount=row.amount,
            type=row.type,
            created_at=row.created_at,
        )
