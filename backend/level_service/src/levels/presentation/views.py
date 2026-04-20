"""HTTP views — thin adapters between HTTP and application use cases."""

from __future__ import annotations

import uuid

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from levels.application.use_cases.get_level import GetLevelUseCase
from levels.application.use_cases.get_level_stats import GetLevelStatsUseCase
from levels.application.use_cases.list_levels import ListLevelsUseCase
from levels.application.use_cases.submit_level import SubmitLevelUseCase
from levels.domain.services import RewardCalculator
from levels.infrastructure.kafka.producer import SubmitEventProducer
from levels.infrastructure.repositories import DjangoLevelRepository, DjangoSubmitRepository
from levels.presentation.serializers import (
    LevelListSerializer,
    LevelSerializer,
    LevelStatsSerializer,
    SubmitInputSerializer,
    SubmitResponseSerializer,
)


def _level_repository() -> DjangoLevelRepository:
    return DjangoLevelRepository()


def _submit_repository() -> DjangoSubmitRepository:
    return DjangoSubmitRepository()


def _event_producer() -> SubmitEventProducer:
    return SubmitEventProducer()


class LevelListView(APIView):
    """GET /level — returns a paginated list of levels."""

    def get(self, request: Request) -> Response:
        """Handles level listing with start/limit pagination."""
        start = max(0, int(request.query_params.get("start", 0)))
        limit = max(1, int(request.query_params.get("limit", 20)))

        use_case = ListLevelsUseCase(level_repository=_level_repository())
        result = use_case.execute(start=start, limit=limit)

        return Response(LevelListSerializer(result).data, status=status.HTTP_200_OK)


class LevelDetailView(APIView):
    """GET /level/{uuid} — returns a single level."""

    def get(self, request: Request, level_id: uuid.UUID) -> Response:
        """Handles level detail retrieval."""
        use_case = GetLevelUseCase(level_repository=_level_repository())
        result = use_case.execute(level_id)
        return Response(LevelSerializer(result).data, status=status.HTTP_200_OK)


class LevelSubmitView(APIView):
    """POST /level — submits a typing attempt."""

    def post(self, request: Request) -> Response:
        """Handles typing attempt submission.

        Identity is read exclusively from Traefik-injected headers.
        Any user_id in the request body is ignored.
        """
        serializer = SubmitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id_header = request.headers.get("X-User-Id")
        username_header = request.headers.get("X-Username")

        if not user_id_header:
             return Response({"detail": "X-User-Id header is missing"}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_id = uuid.UUID(user_id_header)
        username = username_header or "unknown"

        from levels.application.dto import SubmitLevelDTO

        use_case = SubmitLevelUseCase(
            level_repository=_level_repository(),
            submit_repository=_submit_repository(),
            reward_calculator=RewardCalculator(),
            event_producer=_event_producer(),
        )
        result = use_case.execute(
            SubmitLevelDTO(
                level_id=serializer.validated_data["level_id"],
                user_id=user_id,
                username=username,
                wpm=serializer.validated_data["wpm"],
            )
        )

        return Response(SubmitResponseSerializer(result).data, status=status.HTTP_201_CREATED)


class LevelStatsView(APIView):
    """GET /level/stats — return the caller's best WPM."""

    def get(self, request: Request) -> Response:
        user_id_header = request.headers.get("X-User-Id")
        if not user_id_header:
            return Response({"detail": "X-User-Id header is missing"}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = uuid.UUID(user_id_header)
        use_case = GetLevelStatsUseCase(submit_repository=_submit_repository())
        dto = use_case.execute(user_id=user_id)
        return Response(LevelStatsSerializer(dto).data, status=status.HTTP_200_OK)
