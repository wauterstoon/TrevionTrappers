from django.contrib import admin

from .models import Participation, Ride


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'start_time', 'departure', 'distance_km', 'status', 'created_by')
    list_filter = ('status', 'level', 'date')
    search_fields = ('title', 'departure', 'notes', 'created_by__username')


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('ride', 'user', 'status', 'km', 'updated_by', 'updated_at')
    list_filter = ('status', 'ride__date')
    search_fields = ('user__username', 'ride__title')
