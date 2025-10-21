from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.event_list, name='event_list'),            # user lihat daftar acara
    path('events/<int:id>/', views.event_detail, name='event_detail'), # detail acara
    path('admin/events/add/', views.event_create, name='event_create'),
    path('admin/events/<int:id>/edit/', views.event_update, name='event_update'),
    path('admin/events/<int:id>/delete/', views.event_delete, name='event_delete'),
]
