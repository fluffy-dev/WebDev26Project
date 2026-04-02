from django.apps import AppConfig


class GameConfig(AppConfig):
    """Configuration for the game application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.game"
    label = "game"
