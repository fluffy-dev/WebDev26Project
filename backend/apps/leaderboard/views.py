"""
Leaderboard API view.

Implemented as a FBV with @api_view (satisfies FBV requirement).
The query is O(1) index scan on total_score thanks to db_index=True
on Profile.total_score — no aggregation or subqueries at request time.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.accounts.models import Profile
from .serializers import LeaderboardEntrySerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def leaderboard(request: Request) -> Response:
    """
    Return the top-10 players ordered by their pre-computed total_score.

    select_related fetches User and Avatar in a single JOIN, preventing
    N+1 queries when the serializer accesses nested relations.
    """
    top_profiles = (
        Profile.objects.select_related("user", "avatar")
        .order_by("-total_score")[:10]
    )
    serializer = LeaderboardEntrySerializer(
        top_profiles, many=True, context={"request": request}
    )
    return Response(serializer.data)
