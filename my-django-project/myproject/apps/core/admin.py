# hotel/admin.py
from django.contrib import admin
from .models import Client, Employee, Room, Service, Booking
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'phone', 'created_at')
    search_fields = ('name', 'surname', 'email')
    list_filter = ('created_at',)


@admin.register(Employee)
class PerfilEmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'phone', 'hire_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'position')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'type', 'capacity', 'price', 'available')
    search_fields = ('number', 'type')
    list_filter = ('type', 'available')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    list_filter = ('price',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'room', 'check_in', 'check_out', 'status', 'total_display')
    search_fields = ('cliente__name', 'cliente__surname', 'room__number')
    list_filter = ('status', 'services')

    def total_display(self, obj):
        return f"{obj.total():.2f}"
    total_display.short_description = 'total'

    # to show services in the list view
    def services_list(self, obj):
        services = obj.services.all()
        if services:
            return ", ".join([s.name for s in services])
        return "-"
    services_list.short_description = 'services'

    readonly_fields = ('created_at',)
