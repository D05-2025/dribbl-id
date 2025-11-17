from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('json/', views.show_json, name='event_json'),

    path('', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('<int:event_id>/delete/', views.delete_event, name='delete_event'),
]
