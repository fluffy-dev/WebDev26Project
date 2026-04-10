"""URL routes for the levels presentation layer."""

from django.urls import path

from .views import LevelDetailView, LevelListView, LevelSubmitView

urlpatterns = [
    path("level", LevelListView.as_view()),
    path("level/<uuid:level_id>", LevelDetailView.as_view()),
    path("level/submit", LevelSubmitView.as_view()),
]
