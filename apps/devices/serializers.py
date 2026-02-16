from django.utils import timezone
from rest_framework import serializers

from apps.devices.models import Device, Event


class EventCreateSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    timestamp = serializers.DateTimeField()
    event_type = serializers.ChoiceField(
        choices=["production_cycle", "downtime_start", "downtime_end"]
    )
    payload = serializers.JSONField()

    def validate_device_id(self, value):
        if not Device.objects.filter(device_id=value, is_active=True).exists():
            raise serializers.ValidationError("Device not found or inactive")
        return value

    def validate_timestamp(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Future timestamps not allowed")
        return value


class EventSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source="device.device_id", read_only=True)

    class Meta:
        model = Event
        fields = ["id", "device_id", "timestamp", "event_type", "payload", "idempotency_key"]


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            "id",
            "factory",
            "machine",
            "device_id",
            "device_type",
            "last_seen_at",
            "is_active",
            "metadata",
        ]
        read_only_fields = ["id"]
