"""Data Transfer Objects for the levels application boundary."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SubmitLevelDTO:
    """Input data for the submit level use case."""

    level_id: uuid.UUID
    user_id: uuid.UUID
    username: str
    wpm: int


@dataclass(frozen=True)
class LevelResponseDTO:
    """Public-facing level representation."""

    id: uuid.UUID
    text: str
    cost: int
    goal_wpm: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class LevelListResponseDTO:
    """Paginated list of levels."""

    count: int
    results: list[LevelResponseDTO]


@dataclass(frozen=True)
class SubmitResponseDTO:
    """Public-facing submit result."""

    id: uuid.UUID
    level_id: uuid.UUID
    user_id: uuid.UUID
    wpm: int
    rewarded_credits: int
    created_at: datetime
