from __future__ import annotations

from uuid import UUID

from balances.domain.repositories import AbstractBalanceRepository


class CreateBalanceUseCase:
    """Create a zero-balance wallet for a newly registered user."""

    def __init__(self, balance_repository: AbstractBalanceRepository) -> None:
        self._balance_repository = balance_repository

    def execute(self, user_id: UUID) -> None:
        """Persist a new balance row if one does not already exist."""
        existing = self._balance_repository.get_by_user_id(user_id)
        if existing is not None:
            return

        self._balance_repository.create(user_id=user_id)
