from django.urls import path
from authentication.views import register

urlpatterns = [
    path('register/', register, name='register'),
]