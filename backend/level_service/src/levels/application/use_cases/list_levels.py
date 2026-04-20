"""List levels use case."""

from __future__ import annotations

from django.conf import settings

from levels.application.dto import LevelListResponseDTO, LevelResponseDTO
from levels.domain.repositories import AbstractLevelRepository


class ListLevelsUseCase:
    """Returns a paginated list of available typing levels."""

    def __init__(self, level_repository: AbstractLevelRepository) -> None:
        self._level_repository = level_repository

    def execute(self, start: int, limit: int) -> LevelListResponseDTO:
        """Fetches a page of levels.

        Args:
            start: Zero-based offset.
            limit: Number of results requested; capped at LEVELS_PAGE_LIMIT_MAX.

        Returns:
            Paginated level list with total count.
        """
        limit = min(limit, settings.LEVELS_PAGE_LIMIT_MAX)
        levels, total = self._level_repository.list(start=start, limit=limit)

        return LevelListResponseDTO(
            count=total,
            results=[
                LevelResponseDTO(
                    id=level.id,
                    text=level.text,
                    cost=level.cost,
                    goal_wpm=level.goal_wpm,
                    level_type=level.level_type,
                    created_at=level.created_at,
                    updated_at=level.updated_at,
                )
                for level in levels
            ],
        )
