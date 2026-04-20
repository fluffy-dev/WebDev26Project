"""Abstract repository interfaces — the domain's contract with infrastructure."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Optional

from .entities import LevelEntity, SubmitEntity


class AbstractLevelRepository(ABC):
    """Port for level persistence operations."""

    @abstractmethod
    def get_by_id(self, level_id: uuid.UUID) -> Optional[LevelEntity]:
        """Retrieves a level by its primary key."""

    @abstractmethod
    def list(self, start: int, limit: int) -> tuple[list[LevelEntity], int]:
        """Returns a page of levels and the total count.

        Args:
            start: Zero-based offset.
            limit: Maximum number of results.

        Returns:
            Tuple of (levels page, total count).
        """


class AbstractSubmitRepository(ABC):
    """Port for submit persistence operations."""

    @abstractmethod
    def has_prior_submit(self, user_id: uuid.UUID, level_id: uuid.UUID) -> bool:
        """Returns True if this user has already submitted this level."""

    @abstractmethod
    def save(self, submit: SubmitEntity) -> SubmitEntity:
        """Persists a new submit and returns the saved entity."""

    @abstractmethod
    def get_best_wpm(self, user_id: uuid.UUID) -> int:
        """Return the user's best recorded WPM (0 if none)."""
