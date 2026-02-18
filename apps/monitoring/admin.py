from django.contrib import admin

from .models import DowntimeLog, DowntimeReason, Shift

admin.site.register(Shift)
admin.site.register(DowntimeReason)
admin.site.register(DowntimeLog)
