"""
Serializers for the leaderboard application.

Uses ModelSerializer to project the minimum fields needed for a fast
leaderboard render: rank is computed by enumeration in the view.
"""

from rest_framework import serializers
from apps.accounts.models import Profile


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    """Flattened read-only projection of a Profile for leaderboard display."""

    username = serializers.CharField(source="user.username")
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["id", "username", "avatar_url", "total_score", "best_wpm"]

    def get_avatar_url(self, obj: Profile) -> str:
        request = self.context.get("request")
        if request and obj.avatar and obj.avatar.image:
            return request.build_absolute_uri(obj.avatar.image.url)
        return ""
