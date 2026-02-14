from django.contrib import admin

from .models import AuditLog, Factory, Line, Machine, Operator


def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


make_active.short_description = "Bulk activate selected items"
make_inactive.short_description = "Bulk deactivate selected items"


@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    actions = [make_active, make_inactive]


class MachineInline(admin.TabularInline):
    model = Machine
    extra = 0


@admin.register(Line)
class LineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "factory", "is_active")
    list_filter = ("factory", "is_active")
    search_fields = ("name",)
    inlines = [MachineInline]
    actions = [make_active, make_inactive]


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "line", "get_factory", "is_active")
    list_filter = ("line__factory", "is_active", "line")
    search_fields = ("name", "serial_no")
    actions = [make_active, make_inactive]

    def get_factory(self, obj):
        return obj.line.factory

    get_factory.short_description = "Factory"


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "factory", "is_active")
    list_filter = ("factory", "is_active")
    search_fields = ("name", "employee_id")
    actions = [make_active, make_inactive]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "model")
    search_fields = ("action", "model", "user__username")
    list_filter = ("model", "action")
