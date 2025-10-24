from django.urls import path
from . import views
app_name = 'players'

urlpatterns = [
    path('', views.player_list, name='player_list'),
    path('add/', views.add_player, name='add_player'),
    path('edit/<int:player_id>/', views.edit_player, name='edit_player'),
    path('delete/<int:player_id>/', views.delete_player, name='delete_player'),
]
