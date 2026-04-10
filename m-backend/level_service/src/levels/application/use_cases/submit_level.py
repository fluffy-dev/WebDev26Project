"""Submit level attempt use case."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from levels.application.dto import SubmitLevelDTO, SubmitResponseDTO
from levels.application.exceptions import InvalidWpmError, LevelNotFoundError
from levels.domain.entities import SubmitEntity
from levels.domain.repositories import AbstractLevelRepository, AbstractSubmitRepository
from levels.domain.services import RewardCalculator
from levels.infrastructure.kafka.producer import SubmitEventProducer


class SubmitLevelUseCase:
    """Records a typing attempt and awards credits if applicable."""

    def __init__(
        self,
        level_repository: AbstractLevelRepository,
        submit_repository: AbstractSubmitRepository,
        reward_calculator: RewardCalculator,
        event_producer: SubmitEventProducer,
    ) -> None:
        self._level_repository = level_repository
        self._submit_repository = submit_repository
        self._reward_calculator = reward_calculator
        self._event_producer = event_producer

    def execute(self, dto: SubmitLevelDTO) -> SubmitResponseDTO:
        """Processes a typing attempt.

        Calculates the reward based on WPM vs goal. Skips reward if the user
        has submitted this level before. Publishes a Kafka event only when
        the user earns credits.

        Args:
            dto: Submit input data.

        Returns:
            Submit record with reward information.

        Raises:
            LevelNotFoundError: If the level does not exist.
            InvalidWpmError: If wpm is not a positive integer.
        """
        if dto.wpm <= 0:
            raise InvalidWpmError("WPM must be a positive integer.")

        level = self._level_repository.get_by_id(dto.level_id)
        if level is None:
            raise LevelNotFoundError(f"Level '{dto.level_id}' not found.")

        already_submitted = self._submit_repository.has_prior_submit(
            user_id=dto.user_id,
            level_id=dto.level_id,
        )

        rewarded_credits = 0
        if not already_submitted:
            rewarded_credits = self._reward_calculator.calculate(
                user_wpm=dto.wpm,
                goal_wpm=level.goal_wpm,
                level_cost=level.cost,
            )

        submit = SubmitEntity(
            id=uuid.uuid4(),
            level_id=dto.level_id,
            user_id=dto.user_id,
            wpm=dto.wpm,
            rewarded_credits=rewarded_credits,
            created_at=datetime.now(tz=timezone.utc),
        )

        saved = self._submit_repository.save(submit)

        if saved.rewarded_credits > 0:
            self._event_producer.publish_submit_rewarded(
                event_id=saved.id,
                user_id=saved.user_id,
                username=dto.username,
                amount=saved.rewarded_credits,
            )

        return SubmitResponseDTO(
            id=saved.id,
            level_id=saved.level_id,
            user_id=saved.user_id,
            wpm=saved.wpm,
            rewarded_credits=saved.rewarded_credits,
            created_at=saved.created_at,
        )
