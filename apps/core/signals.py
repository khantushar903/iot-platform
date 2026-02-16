from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AuditLog, Factory, Line, Machine, Operator


def _log(instance, action: str):
    AuditLog.objects.create(
        user=None,  # admin user tracking comes later
        action=action,
        model=instance.__class__.__name__,
        changes_json={},
    )


@receiver(post_save, sender=Factory)
def audit_factory(sender, instance, created, **kwargs):
    _log(instance, "created" if created else "updated")


@receiver(post_save, sender=Line)
def audit_line(sender, instance, created, **kwargs):
    _log(instance, "created" if created else "updated")


@receiver(post_save, sender=Machine)
def audit_machine(sender, instance, created, **kwargs):
    _log(instance, "created" if created else "updated")


@receiver(post_save, sender=Operator)
def audit_operator(sender, instance, created, **kwargs):
    _log(instance, "created" if created else "updated")
