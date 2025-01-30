from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "collab"

urlpatterns = [
    path('', views.index, name='index'),
    path('stats/', views.collab_stats, name='collab_stats'),
    path('stats/rooms/', views.rooms, name='rooms'),
    path('list_salas/', views.list_salas, name='list_salas'), #Json
    path('panel/<room_name>/', views.room_stats, name='room_stats'),
    path('api/participants/<room_name>/', views.get_users_pseudonym, name='participants'),
    path('api/elements/<room_name>/', views.get_elements, name='elements'),
    path('api/timeline/<room_name>/', views.get_user_movements_over_time, name='timeline'),
    path('api/heatmap/<room_name>/', views.get_heatmap_data, name='heatmap'),
    path('test-json-access/<room_name>/', views.test_single_json_access, name='test_json_access'),
    path('add-library/', TemplateView.as_view(template_name='collab/add_library.html'),
         name='add-library'),
    path('<room_name>/', views.room, name='room'),
    path('<room_name>/replay/', views.replay, name='replay-room'),
    
]
