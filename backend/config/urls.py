"""
Root URL configuration.

All application routes are namespaced under /api/.
JWT token endpoints are mounted at /api/auth/token/.
Django admin is available at /admin/.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.game.urls")),
    path("api/", include("apps.leaderboard.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
