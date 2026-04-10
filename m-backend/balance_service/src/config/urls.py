from django.urls import path, include

urlpatterns = [
    path("", include("balances.presentation.urls")),
]
