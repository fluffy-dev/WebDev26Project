"""
Domain models for the typing game: Level definitions and Attempt records.
"""

from django.db import models
from apps.accounts.models import Profile


class Level(models.Model):
    """
    A single typing challenge.

    mode differentiates between the standard typing exercise and the
    interactive Cat Survival branching game.  base_reward is the
    maximum score a player can earn; it is multiplied by the accuracy
    modifier at submission time.
    """

    class Mode(models.TextChoices):
        STANDARD = "standard", "Standard"
        CAT_SURVIVAL = "cat_survival", "Cat Survival"

    title = models.CharField(max_length=128)
    content_text = models.TextField()
    mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.STANDARD)
    base_reward = models.IntegerField(default=100)
    difficulty = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["difficulty", "title"]
        verbose_name = "Level"
        verbose_name_plural = "Levels"

    def __str__(self) -> str:
        return f"[{self.get_mode_display()}] {self.title} (diff {self.difficulty})"


class Attempt(models.Model):
    """
    Immutable record of a single play-through of a level.

    earned_score is computed by the backend on submission from
    base_reward * accuracy_modifier and must never be trusted from
    the client payload.
    """

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="attempts")
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="attempts")
    wpm = models.FloatField()
    accuracy = models.FloatField()
    earned_score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]
        verbose_name = "Attempt"
        verbose_name_plural = "Attempts"

    def __str__(self) -> str:
        return (
            f"{self.profile.user.username} on {self.level.title}: "
            f"{self.wpm:.1f} WPM / {self.accuracy:.1f}% acc"
        )
