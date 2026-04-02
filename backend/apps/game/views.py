"""
API views for the game application.

submit_attempt  — FBV using @api_view  (satisfies course FBV requirement).
LevelAPIView    — CBV using APIView    (satisfies course CBV + CRUD requirement).
"""

from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from apps.accounts.models import Profile
from .models import Level, Attempt
from .serializers import AttemptSubmitSerializer, AttemptSerializer, LevelSerializer


def _calculate_reward(base_reward: int, accuracy: float) -> int:
    """
    Derive the final point award from base_reward and accuracy percentage.

    The accuracy modifier is a linear scale from 0.0 to 1.0 so that a
    perfect run earns the full base_reward and a 50% accurate run earns
    half the reward.  Minimum award is 1 point to keep the game fair.
    """
    modifier = accuracy / 100.0
    return max(1, round(base_reward * modifier))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_attempt(request: Request) -> Response:
    """
    Validate and persist a completed level attempt.

    Calculates the earned score server-side from the level's base_reward
    and the submitted accuracy.  Updates the user's profile atomically
    inside a database transaction so that profile totals are always
    consistent with individual attempt records.
    """
    serializer = AttemptSubmitSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    level = Level.objects.get(pk=serializer.validated_data["level_id"])
    wpm: float = serializer.validated_data["wpm"]
    accuracy: float = serializer.validated_data["accuracy"]
    earned = _calculate_reward(level.base_reward, accuracy)

    with transaction.atomic():
        profile: Profile = Profile.objects.select_for_update().get(user=request.user)
        attempt = Attempt.objects.create(
            profile=profile,
            level=level,
            wpm=wpm,
            accuracy=accuracy,
            earned_score=earned,
        )
        profile.award(earned, wpm)

    out = AttemptSerializer(attempt)
    return Response(
        {**out.data, "new_total_score": profile.total_score, "new_currency": profile.virtual_currency},
        status=status.HTTP_201_CREATED,
    )


class LevelAPIView(APIView):
    """
    CRUD interface for Level resources.

    GET    /api/levels/       — list all levels    (authenticated)
    POST   /api/levels/       — create a level     (admin only)
    GET    /api/levels/<pk>/  — retrieve one level (authenticated)
    PUT    /api/levels/<pk>/  — update a level     (admin only)
    DELETE /api/levels/<pk>/  — delete a level     (admin only)
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get(self, request: Request, pk: int | None = None) -> Response:
        if pk:
            try:
                level = Level.objects.get(pk=pk)
            except Level.DoesNotExist:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            return Response(LevelSerializer(level).data)

        levels = Level.objects.all()
        return Response(LevelSerializer(levels, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = LevelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request: Request, pk: int) -> Response:
        try:
            level = Level.objects.get(pk=pk)
        except Level.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = LevelSerializer(level, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, pk: int) -> Response:
        try:
            level = Level.objects.get(pk=pk)
        except Level.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        level.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
