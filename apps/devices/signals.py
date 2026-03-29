from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.devices.models import Event


@receiver(post_save, sender=Event)
def invalidate_realtime_dashboard_cache(sender, instance: Event, created: bool, **kwargs):
    if not created:
        return
    if instance.event_type != "production_cycle":
        return

    cache_key = f"dash:realtime:factory:{instance.factory_id}"
    try:
        cache.delete(cache_key)
    except Exception:
        # Redis/cache may be unavailable; don't break event ingestion/tests
        pass
