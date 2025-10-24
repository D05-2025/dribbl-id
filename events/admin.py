from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'is_public', 'created_by', 'created_at')
    list_filter = ('is_public', 'date', 'created_by')
    search_fields = ('title', 'description', 'location')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'date', 'time', 'location')
        }),
        ('Media', {
            'fields': ('image_url',)
        }),
        ('Settings', {
            'fields': ('is_public', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )