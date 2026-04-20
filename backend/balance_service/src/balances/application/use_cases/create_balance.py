from __future__ import annotations

from uuid import UUID

from balances.domain.repositories import AbstractBalanceRepository


class CreateBalanceUseCase:
    """Create a zero-balance wallet for a newly registered user.

    Idempotent: if a balance already exists for the user_id the call is a no-op.
    The caller (Kafka consumer) is responsible for catching IntegrityError and
    committing the offset without re-raising.

    Args:
        balance_repository: Balance persistence port.
    """

    def __init__(self, balance_repository: AbstractBalanceRepository) -> None:
        self._balance_repository = balance_repository

    def execute(self, user_id: UUID) -> None:
        """Persist a new balance row if one does not already exist.

        Args:
            user_id: UUID of the newly registered user.
        """
        existing = self._balance_repository.get_by_user_id(user_id)
        if existing is not None:
            return

        self._balance_repository.create(user_id=user_id)
