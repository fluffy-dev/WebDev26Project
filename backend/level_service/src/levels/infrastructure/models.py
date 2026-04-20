"""Django ORM models for the levels service."""

import uuid

from django.db import models


class LevelType(models.TextChoices):
    DEFAULT = "default", "Default"
    CAT_RUNNING = "cat_running", "Cat Running"


class Level(models.Model):
    """A typing level with text, scoring parameters, and metadata."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    cost = models.PositiveIntegerField()
    goal_wpm = models.PositiveIntegerField()
    level_type = models.CharField(max_length=32, choices=LevelType.choices, default=LevelType.DEFAULT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "levels"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Level({self.id}) goal={self.goal_wpm}wpm type={self.level_type}"


class Submit(models.Model):
    """A user's recorded typing attempt on a level."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="submits")
    user_id = models.UUIDField(db_index=True)
    wpm = models.PositiveIntegerField()
    rewarded_credits = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "submits"
        indexes = [
            models.Index(fields=["user_id", "level"], name="idx_submits_user_level"),
        ]

    def __str__(self) -> str:
        return f"Submit({self.id}) user={self.user_id} wpm={self.wpm}"
