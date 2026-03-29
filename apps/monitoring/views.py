from datetime import date

from django.core.cache import cache
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from services.monitoring_service import get_line_summary, get_realtime_dashboard


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except Exception:
        raise ValidationError({"date": "Invalid date. Use YYYY-MM-DD."})


class RealtimeDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        factory_id = request.user.userprofile.factory_id
        cache_key = f"dash:realtime:factory:{factory_id}"

        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        data = get_realtime_dashboard(factory_id)
        cache.set(cache_key, data, timeout=60)
        return Response(data)


class LineSummaryView(APIView):
    def get(self, request, line_id):
        factory_id = request.user.userprofile.factory_id

        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if not start or not end:
            raise ValidationError(
                {"detail": "start and end query params are required (YYYY-MM-DD)."}
            )

        start_date = _parse_date(start)
        end_date = _parse_date(end)

        cache_key = f"dash:line_summary:{line_id}:{start}:{end}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        data = get_line_summary(
            factory_id=factory_id, line_id=line_id, start_date=start_date, end_date=end_date
        )
        if data is None:
            raise NotFound("Line not found.")

        cache.set(cache_key, data, timeout=60)
        return Response(data)
