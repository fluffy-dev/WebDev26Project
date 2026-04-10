from django.urls import path
from balances.presentation.views import BalanceView, TransactionListView

urlpatterns = [
    path("balance/<uuid:user_id>", BalanceView.as_view(), name="balance"),
    path("transactions/<uuid:user_id>", TransactionListView.as_view(), name="transactions"),
]
