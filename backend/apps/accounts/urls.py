"""URL patterns for the accounts application."""

from django.urls import path
from . import views

urlpatterns = [
    path("auth/register/", views.register, name="register"),
    path("auth/me/", views.me, name="me"),
    path("avatars/", views.AvatarAPIView.as_view(), name="avatar-list"),
    path("avatars/<int:pk>/", views.AvatarAPIView.as_view(), name="avatar-detail"),
]
