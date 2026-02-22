from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.devices.models import Device, Event
from apps.devices.pagination import EventCursorPagination
from apps.devices.serializers import DeviceSerializer, EventCreateSerializer, EventSerializer
from services.ingestion_service import IngestionService


class EventCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idempotency_key = request.headers.get("Idempotency-Key")
        try:
            factory = request.user.userprofile.factory
        except Exception:
            return Response(
                {"detail": "No factory assigned to this user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Ensure device belongs to user's factory
        if not Device.objects.filter(
            device_id=serializer.validated_data["device_id"], factory=factory
        ).exists():
            return Response(
                {"detail": "Device not found in your factory."},
                status=status.HTTP_404_NOT_FOUND,
            )

        event, created = IngestionService.create_event(
            factory_id=str(factory.id),
            device_id=serializer.validated_data["device_id"],
            payload=serializer.validated_data["payload"],
            timestamp=serializer.validated_data["timestamp"],
            event_type=serializer.validated_data["event_type"],
            idempotency_key=idempotency_key,
        )

        if not created:
            return Response(
                {"error": "duplicate", "existing_id": event.id},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"id": event.id, "status": "processed"},
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        try:
            factory = request.user.userprofile.factory
        except Exception:
            return Response(
                {"detail": "No factory assigned to this user."},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = Event.objects.select_related("device").filter(factory=factory).order_by("-timestamp")

        # Filters (query params)
        device_id = request.query_params.get("device_id")
        event_type = request.query_params.get("event_type")
        start = request.query_params.get("start")
        end = request.query_params.get("end")

        if device_id:
            qs = qs.filter(device__device_id=device_id)

        if event_type:
            qs = qs.filter(event_type=event_type)

        if start:
            start_dt = parse_datetime(start)
            if start_dt:
                qs = qs.filter(timestamp__gte=start_dt)

        if end:
            end_dt = parse_datetime(end)
            if end_dt:
                qs = qs.filter(timestamp__lte=end_dt)

        paginator = EventCursorPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = EventSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DeviceListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceSerializer

    def get_queryset(self):
        try:
            factory = self.request.user.userprofile.factory
        except Exception:
            return Device.objects.none()
        return Device.objects.filter(factory=factory).select_related("factory", "machine")


class DeviceDetailAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceSerializer

    def get_queryset(self):
        try:
            factory = self.request.user.userprofile.factory
        except Exception:
            return Device.objects.none()
        return Device.objects.filter(factory=factory).select_related("factory", "machine")
