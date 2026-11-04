from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

def lista_usuarios(request):
    usuarios = User.objects.all()
    context = {'usuarios': usuarios}
    return render(request, 'usuarios/index.html', context)

def perfil(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    context = {'usuario': usuario}
    return render(request, 'usuarios/perfil.html', context)