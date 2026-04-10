from django.urls import path
from leaderboard.presentation.views import LeaderboardView

urlpatterns = [
    path("", LeaderboardView.as_view(), name="leaderboard"),
]
