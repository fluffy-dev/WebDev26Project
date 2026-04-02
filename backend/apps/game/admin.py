from django.contrib import admin
from .models import Level, Attempt


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "mode", "difficulty", "base_reward"]
    list_filter = ["mode", "difficulty"]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ["profile", "level", "wpm", "accuracy", "earned_score", "completed_at"]
    list_select_related = ["profile__user", "level"]
