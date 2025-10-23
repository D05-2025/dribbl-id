from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_at', 'user')
    list_filter = ('category', 'published_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'published_at'
    readonly_fields = ('id', 'published_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'category')
        }),
        ('Media', {
            'fields': ('thumbnail',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'user', 'published_at'),
            'classes': ('collapse',)
        }),
    )