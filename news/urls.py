from django.urls import path
from news.views import show_news

urlpatterns = [
    path('news/<uuid:id>/', show_news, name='show_news'),
]