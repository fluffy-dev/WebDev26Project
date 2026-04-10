from __future__ import annotations

from uuid import UUID

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from balances.application.use_cases.get_balance import GetBalanceUseCase
from balances.application.use_cases.list_transactions import ListTransactionsUseCase
from balances.infrastructure.repositories import DjangoBalanceRepository, DjangoTransactionRepository
from balances.presentation.serializers import BalanceSerializer, TransactionListSerializer

_MAX_LIMIT = 100
_DEFAULT_LIMIT = 20


class BalanceView(APIView):
    """GET /balance/{user_id} — return a user's current credit total."""

    def get(self, request: Request, user_id: UUID) -> Response:
        """Fetch and return the balance for the given user."""
        use_case = GetBalanceUseCase(
            balance_repository=DjangoBalanceRepository(),
        )
        dto = use_case.execute(user_id=user_id)
        serializer = BalanceSerializer(
            {
                "id": dto.id,
                "user_id": dto.user_id,
                "balance": dto.balance,
                "updated_at": dto.updated_at,
            }
        )
        return Response(serializer.data)


class TransactionListView(APIView):
    """GET /transactions/{user_id} — return paginated transaction history."""

    def get(self, request: Request, user_id: UUID) -> Response:
        """Fetch and return a page of transactions for the given user."""
        start = max(0, int(request.query_params.get("start", 0)))
        limit = min(_MAX_LIMIT, int(request.query_params.get("limit", _DEFAULT_LIMIT)))

        use_case = ListTransactionsUseCase(
            transaction_repository=DjangoTransactionRepository(),
        )
        dto = use_case.execute(user_id=user_id, start=start, limit=limit)
        serializer = TransactionListSerializer(
            {
                "count": dto.count,
                "results": [
                    {
                        "id": tx.id,
                        "event_id": tx.event_id,
                        "amount": tx.amount,
                        "type": tx.type,
                        "created_at": tx.created_at,
                    }
                    for tx in dto.results
                ],
            }
        )
        return Response(serializer.data)
