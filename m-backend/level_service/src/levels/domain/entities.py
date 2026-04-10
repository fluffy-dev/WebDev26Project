"""Domain entities — pure Python, zero framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LevelEntity:
    """Represents a typing level with its text, cost, and speed target."""

    id: uuid.UUID
    text: str
    cost: int
    goal_wpm: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class SubmitEntity:
    """Records a user's typing attempt on a level."""

    id: uuid.UUID
    level_id: uuid.UUID
    user_id: uuid.UUID
    wpm: int
    rewarded_credits: int
    created_at: datetime
