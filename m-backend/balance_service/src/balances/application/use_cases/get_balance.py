from __future__ import annotations

from uuid import UUID

from balances.application.dto import BalanceResponseDTO
from balances.application.exceptions import BalanceNotFoundError
from balances.domain.repositories import AbstractBalanceRepository


class GetBalanceUseCase:
    """Return a user's current balance."""

    def __init__(self, balance_repository: AbstractBalanceRepository) -> None:
        self._balance_repository = balance_repository

    def execute(self, user_id: UUID) -> BalanceResponseDTO:
        """Fetch and return the balance for a user."""
        balance = self._balance_repository.get_by_user_id(user_id)
        if balance is None:
            raise BalanceNotFoundError(f"No balance found for user {user_id}")

        return BalanceResponseDTO(
            id=balance.id,
            user_id=balance.user_id,
            balance=balance.balance,
            updated_at=balance.updated_at,
        )
