"""URL routes for the levels presentation layer."""

from django.urls import path

from .views import LevelDetailView, LevelListView, LevelSubmitView, LevelStatsView
from .health import HealthView

urlpatterns = [
    # Traefik routes external /level/* to this service and strips the /level prefix.
    path("", LevelListView.as_view()),
    path("<uuid:level_id>", LevelDetailView.as_view()),
    path("submit", LevelSubmitView.as_view()),
    path("stats", LevelStatsView.as_view()),
    path("health", HealthView.as_view(), name="level-health"),
]
