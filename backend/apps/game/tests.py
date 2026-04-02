"""
Test suite for reward calculation and attempt submission endpoint.

Uses pytest-django fixtures.  The score manipulation prevention test
verifies that clients cannot inflate their own scores by passing
fabricated wpm/accuracy values beyond logical bounds.
"""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from apps.accounts.models import Avatar, Profile
from apps.game.models import Level
from apps.game.views import _calculate_reward


@pytest.fixture
def avatar(db):
    return Avatar.objects.create(name="TestCat")


@pytest.fixture
def user_with_profile(db, avatar):
    user = User.objects.create_user(username="testuser", password="testpass123")
    profile = Profile.objects.create(user=user, avatar=avatar)
    return user, profile


@pytest.fixture
def level(db):
    return Level.objects.create(
        title="Test Level",
        content_text="the quick brown fox",
        mode=Level.Mode.STANDARD,
        base_reward=100,
    )


@pytest.fixture
def auth_client(user_with_profile):
    user, _ = user_with_profile
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestRewardCalculation:
    """Unit tests for the reward calculation pure function."""

    def test_perfect_accuracy_yields_full_reward(self):
        assert _calculate_reward(100, 100.0) == 100

    def test_zero_accuracy_yields_minimum_reward(self):
        assert _calculate_reward(100, 0.0) == 1

    def test_fifty_percent_accuracy_yields_half_reward(self):
        assert _calculate_reward(100, 50.0) == 50

    def test_reward_cannot_exceed_base(self):
        assert _calculate_reward(200, 100.0) == 200


@pytest.mark.django_db
class TestAttemptSubmission:
    """Integration tests for the attempt submission endpoint."""

    def test_valid_submission_creates_attempt_and_updates_score(
        self, auth_client, user_with_profile, level
    ):
        _, profile = user_with_profile
        response = auth_client.post(
            reverse("submit-attempt"),
            {"level_id": level.id, "wpm": 60.0, "accuracy": 90.0},
            format="json",
        )
        assert response.status_code == 201
        profile.refresh_from_db()
        assert profile.total_score == 90

    def test_wpm_exceeding_maximum_is_rejected(self, auth_client, level):
        response = auth_client.post(
            reverse("submit-attempt"),
            {"level_id": level.id, "wpm": 9999.0, "accuracy": 100.0},
            format="json",
        )
        assert response.status_code == 400

    def test_accuracy_above_100_is_rejected(self, auth_client, level):
        response = auth_client.post(
            reverse("submit-attempt"),
            {"level_id": level.id, "wpm": 60.0, "accuracy": 150.0},
            format="json",
        )
        assert response.status_code == 400

    def test_unauthenticated_submission_is_rejected(self, level):
        client = APIClient()
        response = client.post(
            reverse("submit-attempt"),
            {"level_id": level.id, "wpm": 60.0, "accuracy": 100.0},
            format="json",
        )
        assert response.status_code == 401
