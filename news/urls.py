from django.urls import path
from news.views import show_json, show_json_by_id, add_news_entry_ajax, edit_news_entry_ajax, delete_news, show_news_page, show_news_detail, get_news_json, show_xml, show_xml_by_id, add_news_flutter

app_name = 'news'
urlpatterns = [
    path('', show_news_page, name='show_news_page'),
    path('create-flutter/', add_news_flutter, name='create_news_flutter'),
    path('json/', show_json, name='show_json'),
    path('json/<uuid:news_id>/', show_json_by_id, name='show_json_by_id'),
    path('get-news-json/<uuid:id>/', get_news_json, name='get_news_json'),
    path('add-news-entry-ajax/', add_news_entry_ajax, name='add_news_entry_ajax'),
    path('edit-news-ajax/<uuid:id>/', edit_news_entry_ajax, name='edit_news_entry_ajax'),
    path('delete-news-ajax/<uuid:id>/', delete_news, name='delete_news_ajax'),
    path('xml/', show_xml, name='show_xml'),
    path('xml/<uuid:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('detail/<uuid:news_id>/', show_news_detail, name='show_news_detail'),
]