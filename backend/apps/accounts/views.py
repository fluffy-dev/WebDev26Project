"""
API views for the accounts application.

register — FBV using @api_view decorator (satisfies course requirement).
AvatarAPIView — CBV using APIView (satisfies course requirement for CBV with CRUD).
MeView — returns the authenticated user's own profile.
"""

from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Avatar, Profile
from .serializers import AvatarSerializer, RegisterSerializer, ProfileSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request: Request) -> Response:
    """
    Register a new user account.

    Accepts username, password, password_confirm, and avatar_id.
    On success returns 201 with the created user's username.
    On validation failure returns 400 with field-level error messages.
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user: User = serializer.save()
    return Response({"username": user.username}, status=status.HTTP_201_CREATED)


class AvatarAPIView(APIView):
    """
    CRUD interface for the Avatar catalogue.

    GET    /api/avatars/       — list all avatars (public)
    POST   /api/avatars/       — create an avatar  (admin only)
    GET    /api/avatars/<pk>/  — retrieve one      (public)
    PUT    /api/avatars/<pk>/  — full update       (admin only)
    DELETE /api/avatars/<pk>/  — destroy           (admin only)
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request: Request, pk: int | None = None) -> Response:
        if pk:
            try:
                avatar = Avatar.objects.get(pk=pk)
            except Avatar.DoesNotExist:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = AvatarSerializer(avatar, context={"request": request})
            return Response(serializer.data)

        avatars = Avatar.objects.all()
        serializer = AvatarSerializer(avatars, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = AvatarSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request: Request, pk: int) -> Response:
        try:
            avatar = Avatar.objects.get(pk=pk)
        except Avatar.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AvatarSerializer(avatar, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, pk: int) -> Response:
        try:
            avatar = Avatar.objects.get(pk=pk)
        except Avatar.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request: Request) -> Response:
    """Return the authenticated user's profile data."""
    profile = Profile.objects.select_related("user", "avatar").get(user=request.user)
    serializer = ProfileSerializer(profile, context={"request": request})
    return Response(serializer.data)
