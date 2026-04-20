"""Health check endpoint for the level service."""

from __future__ import annotations

import logging
import time

from django.db import connection
from django.db.utils import OperationalError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

_START_TIME = time.time()


class HealthView(APIView):
    """GET /health — liveness + readiness probe for level_service.

    Checks connectivity to the Postgres database.
    Returns a personality-flavoured status message alongside structured
    health data so monitoring tools can parse it.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request: Request) -> Response:
        """Return service health status.

        Returns:
            200 when all dependencies are reachable.
            503 when any dependency is unreachable.
        """
        uptime = int(time.time() - _START_TIME)
        checks: dict[str, str] = {}

        # --- Database check ---
        try:
            connection.ensure_connection()
            checks["postgres"] = "ok"
        except OperationalError as exc:
            logger.error("Health check: postgres unreachable: %s", exc)
            checks["postgres"] = "unreachable"

        healthy = all(v == "ok" for v in checks.values())

        payload = {
            "service": "level_service",
            "status": "healthy" if healthy else "degraded",
            "message": (
                "Level service is crushing it — WPM goals being met, "
                "credits flying, fingers on fire! ⌨️🔥"
                if healthy
                else "Level service is lagging — database is slow-typing today. 🐢"
            ),
            "uptime_seconds": uptime,
            "checks": checks,
        }

        status_code = 200 if healthy else 503
        return Response(payload, status=status_code)
