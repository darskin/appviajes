from django.shortcuts import render, get_object_or_404
from .models import Publicacion

def index(request):
    publicaciones = Publicacion.objects.order_by('-fecha_creacion')
    context = {'publicaciones': publicaciones}
    return render(request, 'blog/index.html', context)

def detalle(request, post_id):
    post = get_object_or_404(Publicacion, pk=post_id)
    context = {'post': post}
    return render(request, 'blog/detalle.html', context)