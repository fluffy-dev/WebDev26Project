from django.urls import path
from balances.presentation.views import BalanceView, TransactionListView
from balances.presentation.health import HealthView

urlpatterns = [
    path("balance/<uuid:user_id>", BalanceView.as_view(), name="balance"),
    path("transactions/<uuid:user_id>", TransactionListView.as_view(), name="transactions"),
    path("health", HealthView.as_view(), name="balance-health"),
]
