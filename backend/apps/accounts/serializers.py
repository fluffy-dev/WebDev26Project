"""
Serializers for the accounts application.

RegisterSerializer uses the base Serializer class (not ModelSerializer)
to satisfy the FBV requirement while keeping full control over user
creation logic.  AvatarSerializer uses ModelSerializer for standard
CRUD operations on the Avatar model.
"""

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Avatar, Profile


class AvatarSerializer(serializers.ModelSerializer):
    """Full representation of an Avatar object including its media URL."""

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Avatar
        fields = ["id", "name", "image_url"]

    def get_image_url(self, obj: Avatar) -> str:
        request = self.context.get("request")
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)
        return ""


class RegisterSerializer(serializers.Serializer):
    """
    Handles new-user registration.

    Validates uniqueness of the username, existence of the chosen
    avatar_id, and password confirmation before atomically creating
    a User and its associated Profile.
    """

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    avatar_id = serializers.IntegerField()

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_avatar_id(self, value: int) -> int:
        if not Avatar.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Avatar not found.")
        return value

    def validate(self, data: dict) -> dict:
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data

    def create(self, validated_data: dict) -> User:
        avatar = Avatar.objects.get(pk=validated_data["avatar_id"])
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        user.profile.avatar = avatar
        user.profile.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Read-only snapshot of the authenticated user's profile."""

    username = serializers.CharField(source="user.username")
    avatar = AvatarSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "username", "avatar", "total_score", "virtual_currency", "best_wpm"]
