import logging

from celery import shared_task

from apps.devices.models import Event

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def process_event_async(self, event_id: int) -> None:
    """
    Background processing for an ingested event.
    """
    try:
        event = Event.objects.select_related("device", "factory").get(id=event_id)

        logger.info(
            "Processed event in background",
            extra={
                "event_id": event.id,
                "factory_id": str(event.factory_id),
                "device_id": str(event.device_id),
                "event_type": event.event_type,
            },
        )

    except Event.DoesNotExist:
        logger.warning("Event not found for background processing", extra={"event_id": event_id})
        return
    except Exception as exc:
        raise self.retry(exc=exc)
