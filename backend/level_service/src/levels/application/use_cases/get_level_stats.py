from __future__ import annotations

import uuid

from levels.application.dto import LevelStatsResponseDTO
from levels.domain.repositories import AbstractSubmitRepository


class GetLevelStatsUseCase:
    """Return simple per-user stats from the submits table."""

    def __init__(self, submit_repository: AbstractSubmitRepository) -> None:
        self._submit_repository = submit_repository

    def execute(self, user_id: uuid.UUID) -> LevelStatsResponseDTO:
        best_wpm = self._submit_repository.get_best_wpm(user_id=user_id)
        return LevelStatsResponseDTO(user_id=user_id, best_wpm=best_wpm)

