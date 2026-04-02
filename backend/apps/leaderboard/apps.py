from django.apps import AppConfig


class LeaderboardConfig(AppConfig):
    """Configuration for the leaderboard application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.leaderboard"
    label = "leaderboard"
