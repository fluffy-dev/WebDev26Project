"""Get level by id use case."""

from __future__ import annotations

import uuid

from levels.application.dto import LevelResponseDTO
from levels.application.exceptions import LevelNotFoundError
from levels.domain.repositories import AbstractLevelRepository


class GetLevelUseCase:
    """Retrieves a single level by its UUID."""

    def __init__(self, level_repository: AbstractLevelRepository) -> None:
        self._level_repository = level_repository

    def execute(self, level_id: uuid.UUID) -> LevelResponseDTO:
        """Fetches level details.

        Args:
            level_id: UUID of the level to retrieve.

        Returns:
            Level data DTO.

        Raises:
            LevelNotFoundError: If no level with this id exists.
        """
        level = self._level_repository.get_by_id(level_id)

        if level is None:
            raise LevelNotFoundError(f"Level '{level_id}' not found.")

        return LevelResponseDTO(
            id=level.id,
            text=level.text,
            cost=level.cost,
            goal_wpm=level.goal_wpm,
            level_type=level.level_type,
            created_at=level.created_at,
            updated_at=level.updated_at,
        )
