from django.urls import path
from . import views

app_name = "matches"

urlpatterns = [
    path("", views.match_schedule, name="schedule"),
    path("results/", views.match_results, name="results"),
    path("create/", views.match_create, name="create"),
    path("<int:pk>/", views.match_detail, name="detail"),
    path("<int:pk>/edit/", views.match_edit, name="edit"),
    path("<int:pk>/score/", views.match_update_score, name="score"),
    path("<int:pk>/delete/", views.match_delete, name="delete"),
    path("<int:pk>/boxscore/add/", views.boxscore_add, name="boxscore_add"),
    path("<int:pk>/boxscore/<int:box_id>/edit/", views.boxscore_edit, name="boxscore_edit"),
    path("json/", views.matches_json, name="api_json"),
    path("api/xml/", views.matches_xml, name="api_xml"),
]
