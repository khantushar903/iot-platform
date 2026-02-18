from django.contrib import admin

from .models import Device, Event

admin.site.register(Device)
admin.site.register(Event)
