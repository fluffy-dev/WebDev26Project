"""DRF serializers for request validation and response shaping."""

from __future__ import annotations

from rest_framework import serializers


class LevelSerializer(serializers.Serializer):
    """Shapes level data for API responses."""

    id = serializers.UUIDField()
    text = serializers.CharField()
    cost = serializers.IntegerField()
    goal_wpm = serializers.IntegerField()
    level_type = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class LevelListSerializer(serializers.Serializer):
    """Shapes paginated level list responses."""

    count = serializers.IntegerField()
    results = LevelSerializer(many=True)


class SubmitInputSerializer(serializers.Serializer):
    """Validates POST /level request body."""

    level_id = serializers.UUIDField()
    wpm = serializers.IntegerField(min_value=1)


class SubmitResponseSerializer(serializers.Serializer):
    """Shapes submit result responses."""

    id = serializers.UUIDField()
    level_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    wpm = serializers.IntegerField()
    rewarded_credits = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class LevelStatsSerializer(serializers.Serializer):
    """Shapes per-user stats output."""

    user_id = serializers.UUIDField()
    best_wpm = serializers.IntegerField()
