"""Concrete Django ORM repository implementations."""

from __future__ import annotations

import uuid
from typing import Optional

from levels.domain.entities import LevelEntity, SubmitEntity
from levels.domain.repositories import AbstractLevelRepository, AbstractSubmitRepository
from levels.infrastructure.models import Level, Submit


class DjangoLevelRepository(AbstractLevelRepository):
    """ORM-backed level repository."""

    def get_by_id(self, level_id: uuid.UUID) -> Optional[LevelEntity]:
        """Retrieves a level by primary key."""
        try:
            return self._to_entity(Level.objects.get(pk=level_id))
        except Level.DoesNotExist:
            return None

    def list(self, start: int, limit: int) -> tuple[list[LevelEntity], int]:
        """Returns a page of levels and the total count."""
        qs = Level.objects.all()
        total = qs.count()
        page = qs[start : start + limit]
        return [self._to_entity(model) for model in page], total

    def _to_entity(self, model: Level) -> LevelEntity:
        return LevelEntity(
            id=model.id,
            text=model.text,
            cost=model.cost,
            goal_wpm=model.goal_wpm,
            level_type=model.level_type,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class DjangoSubmitRepository(AbstractSubmitRepository):
    """ORM-backed submit repository."""

    def has_prior_submit(self, user_id: uuid.UUID, level_id: uuid.UUID) -> bool:
        """Returns True if any prior submit exists for this user and level."""
        return Submit.objects.filter(user_id=user_id, level_id=level_id).exists()

    def save(self, submit: SubmitEntity) -> SubmitEntity:
        """Persists a new submit."""
        model = Submit.objects.create(
            id=submit.id,
            level_id=submit.level_id,
            user_id=submit.user_id,
            wpm=submit.wpm,
            rewarded_credits=submit.rewarded_credits,
        )
        return SubmitEntity(
            id=model.id,
            level_id=model.level_id,
            user_id=model.user_id,
            wpm=model.wpm,
            rewarded_credits=model.rewarded_credits,
            created_at=model.created_at,
        )

    def get_best_wpm(self, user_id: uuid.UUID) -> int:
        best = (
            Submit.objects.filter(user_id=user_id)
            .order_by("-wpm")
            .values_list("wpm", flat=True)
            .first()
        )
        return int(best) if best is not None else 0
