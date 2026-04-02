"""URL patterns for the game application."""

from django.urls import path
from . import views

urlpatterns = [
    path("levels/", views.LevelAPIView.as_view(), name="level-list"),
    path("levels/<int:pk>/", views.LevelAPIView.as_view(), name="level-detail"),
    path("attempts/submit/", views.submit_attempt, name="submit-attempt"),
]
