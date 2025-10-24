from django.contrib import admin
from .models import Team, Player, Season, Match

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'team', 'jersey_number', 'position', 'is_active']
    list_filter = ['team', 'position', 'is_active']
    search_fields = ['full_name', 'team__name']
    ordering = ['team__name', 'full_name']

    def get_fields(self, request, obj=None):
        # Exclude height_cm and weight_kg from admin form
        fields = super().get_fields(request, obj)
        return [f for f in fields if f not in ['height_cm', 'weight_kg']]

admin.site.register(Team)
admin.site.register(Season)
admin.site.register(Match)
