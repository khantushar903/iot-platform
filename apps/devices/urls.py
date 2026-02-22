from django.urls import path

from apps.devices.views import DeviceDetailAPIView, DeviceListCreateAPIView, EventCreateAPIView

urlpatterns = [
    path("events/", EventCreateAPIView.as_view(), name="event-create"),
    path("devices/", DeviceListCreateAPIView.as_view(), name="device-list-create"),
    path("devices/<uuid:pk>/", DeviceDetailAPIView.as_view(), name="device-detail"),
]
