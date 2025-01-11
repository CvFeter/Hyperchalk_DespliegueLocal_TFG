from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "collab"

urlpatterns = [
    path('', views.index, name='index'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('estadisticas/salas/', views.salas, name='salas'),
    path('list_salas/', views.list_salas, name='list_salas'),
    # path('estadisticas/salas/<room_name>/', views.salas_stats, name='estadisticas_sala'),
    path('add-library/', TemplateView.as_view(template_name='collab/add_library.html'),
         name='add-library'),
    path('<room_name>/', views.room, name='room'),
    path('<room_name>/replay/', views.replay, name='replay-room'),
    
]
