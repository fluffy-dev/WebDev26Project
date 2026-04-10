from django.urls import path, include

urlpatterns = [
    path("leaderboard", include("leaderboard.presentation.urls")),
]
