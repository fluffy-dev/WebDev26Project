"""
Serializers for the game application.

LevelSerializer is a ModelSerializer used by the CBV (APIView).
AttemptSubmitSerializer is a plain Serializer used by the FBV,
keeping score calculation logic fully server-side.
"""

from rest_framework import serializers
from .models import Level, Attempt


class LevelSerializer(serializers.ModelSerializer):
    """Full read/write representation of a Level."""

    class Meta:
        model = Level
        fields = ["id", "title", "content_text", "mode", "base_reward", "difficulty"]


class AttemptSubmitSerializer(serializers.Serializer):
    """
    Validates raw typing data sent by the client after a level ends.

    The client provides only measurable facts (wpm, accuracy, level_id).
    The server re-derives earned_score from the level's base_reward to
    prevent point manipulation.
    """

    level_id = serializers.IntegerField()
    wpm = serializers.FloatField(min_value=0, max_value=500)
    accuracy = serializers.FloatField(min_value=0, max_value=100)

    def validate_level_id(self, value: int) -> int:
        if not Level.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Level not found.")
        return value

    def validate_wpm(self, value: float) -> float:
        if value < 0:
            raise serializers.ValidationError("WPM cannot be negative.")
        return round(value, 2)

    def validate_accuracy(self, value: float) -> float:
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Accuracy must be between 0 and 100.")
        return round(value, 2)


class AttemptSerializer(serializers.ModelSerializer):
    """Read representation of a completed attempt."""

    level_title = serializers.CharField(source="level.title", read_only=True)

    class Meta:
        model = Attempt
        fields = ["id", "level_title", "wpm", "accuracy", "earned_score", "completed_at"]
