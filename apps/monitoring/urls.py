from django.urls import path

from apps.monitoring.views import LineSummaryView, RealtimeDashboardView

urlpatterns = [
    path("dashboards/realtime/", RealtimeDashboardView.as_view(), name="dashboards-realtime"),
    path(
        "dashboards/line/<uuid:line_id>/summary/",
        LineSummaryView.as_view(),
        name="dashboards-line-summary",
    ),
]
