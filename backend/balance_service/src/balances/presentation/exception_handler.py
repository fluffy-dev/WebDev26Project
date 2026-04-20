from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import exception_handler

from balances.application.exceptions import BalanceNotFoundError

_STATUS_MAP = {
    BalanceNotFoundError: 404,
}


def custom_exception_handler(exc, context) -> Response | None:
    """Map application exceptions to HTTP responses.

    Args:
        exc: The raised exception.
        context: DRF context dict containing the view and request.

    Returns:
        A DRF Response with the appropriate status code, or None to fall
        through to DRF's default handler for non-application exceptions.
    """
    status_code = _STATUS_MAP.get(type(exc))
    if status_code is not None:
        return Response({"detail": str(exc)}, status=status_code)

    return exception_handler(exc, context)
