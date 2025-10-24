from django.urls import path
from .views import (
    show_teams, 
    add_team, 
    team_detail, 
    get_team, 
    edit_team, 
    delete_team
)

app_name = 'teams'

urlpatterns = [
    path('', show_teams, name='show_teams'),
    path('add/', add_team, name='add_team'),
    path('<str:team_name>/', team_detail, name='team_detail'),
    
    # New AJAX URLs for Admin
    path('get/<str:team_name>/', get_team, name='get_team_data'),
    path('edit/<str:team_name>/', edit_team, name='edit_team'),
    path('delete/<str:team_name>/', delete_team, name='delete_team'),
]

