from django.urls import path
from news.views import show_json, show_json_by_id, add_news_entry_ajax, edit_news_entry_ajax, delete_news_ajax, show_news_page

app_name = 'news'
urlpatterns = [
    path('', show_news_page, name='main'),
    path('json/', show_json, name='show_json'),
    path('json/<uuid:id>/', show_json_by_id, name='show_json_by_id'),
    path('add/', add_news_entry_ajax, name='add_news_entry_ajax'),
    path('edit/<uuid:id>/', edit_news_entry_ajax, name='edit_news_entry_ajax'),
    path('delete/<uuid:id>/', delete_news_ajax, name='delete_news_ajax'),
]

