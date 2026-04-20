"""Django admin for level management."""

from django.contrib import admin

from .infrastructure.models import Level, Submit


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """Admin panel for managing typing levels."""

    list_display = ("id", "level_type", "goal_wpm", "cost", "created_at")
    search_fields = ("text",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Submit)
class SubmitAdmin(admin.ModelAdmin):
    """Admin panel for viewing submit history."""

    list_display = ("id", "user_id", "level", "wpm", "rewarded_credits", "created_at")
    readonly_fields = ("id", "created_at")
    list_filter = ("level",)
