"""Maps application exceptions to DRF HTTP responses."""

from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from levels.application.exceptions import (
    ApplicationError,
    InvalidWpmError,
    LevelNotFoundError,
)

_STATUS_MAP: dict[type[ApplicationError], int] = {
    LevelNotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidWpmError: status.HTTP_400_BAD_REQUEST,
}


def custom_exception_handler(exc: Exception, context: dict) -> Response | None:
    """Translates application errors to structured HTTP error responses."""
    for exc_class, status_code in _STATUS_MAP.items():
        if isinstance(exc, exc_class):
            return Response({"detail": str(exc)}, status=status_code)

    return exception_handler(exc, context)
