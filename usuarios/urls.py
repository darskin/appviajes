from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_usuarios, name='lista_usuarios'),
    path('<int:user_id>/', views.perfil, name='perfil'),
]