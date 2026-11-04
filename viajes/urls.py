from django.urls import path
from . import views

app_name = "viajes"

urlpatterns = [

    path('', views.index, name='index'),
    path('<int:destino_id>/', views.detalle, name='detalle'),


    path('crear/', views.crear_destino, name='crear_destino'),
    path('<int:destino_id>/editar/', views.editar_destino, name='editar_destino'),
    path('<int:destino_id>/eliminar/', views.eliminar_destino, name='eliminar_destino'),


    path('<int:destino_id>/resultados/', views.results, name='results'),
    path('<int:destino_id>/votar/', views.vote, name='vote'),

    path('<int:destino_id>/opciones/agregar/', views.agregar_opcion, name='agregar_opcion'),
    path('<int:destino_id>/opciones/<int:choice_id>/eliminar/', views.eliminar_opcion, name='eliminar_opcion'),
]