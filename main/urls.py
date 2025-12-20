# authentication/urls.py
from django.urls import path
from main.views import register, login_user, logout_user, show_main, proxy_image

app_name = 'main'

urlpatterns = [
    path('proxy-image/', proxy_image, name='proxy_image'),
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
]
