"""Rutas principales de AppViajes."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import include, path

from viajes import views as viajes_views

urlpatterns = [
    path('', lambda request: redirect('viajes:index')),
    path('admin/', admin.site.urls),
    path('viajes/', include('viajes.urls')),
    path('cuentas/registro/', viajes_views.registro, name='registro'),
    path('cuentas/login/', auth_views.LoginView.as_view(), name='login'),
    path('cuentas/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
