from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ChoiceForm, DestinoForm
from .models import Choice, Destino


def index(request):
    lista_destinos = Destino.objects.all()
    return render(request, 'viajes/index.html', {'lista_destinos': lista_destinos})


def detalle(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    return render(
        request,
        'viajes/detalle.html',
        {'destino': destino, 'choice_form': ChoiceForm()},
    )


def crear_destino(request):
    if request.method == 'POST':
        form = DestinoForm(request.POST)
        if form.is_valid():
            destino = form.save()
            return redirect('viajes:detalle', destino_id=destino.id)
    else:
        form = DestinoForm()
    return render(request, 'viajes/destino_form.html', {'form': form, 'titulo': 'Crear Nuevo Destino'})


def editar_destino(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    if request.method == 'POST':
        form = DestinoForm(request.POST, instance=destino)
        if form.is_valid():
            form.save()
            return redirect('viajes:detalle', destino_id=destino.id)
    else:
        form = DestinoForm(instance=destino)
    return render(request, 'viajes/destino_form.html', {'form': form, 'titulo': 'Editar Destino'})


def eliminar_destino(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    if request.method == 'POST':
        destino.delete()
        return redirect('viajes:index')
    return render(request, 'viajes/destino_confirm_delete.html', {'destino': destino})


@require_POST
def agregar_opcion(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    form = ChoiceForm(request.POST)
    if form.is_valid():
        opcion = form.save(commit=False)
        opcion.destino = destino
        opcion.save()
        return redirect('viajes:detalle', destino_id=destino.id)
    return render(request, 'viajes/detalle.html', {'destino': destino, 'choice_form': form})


@require_POST
def eliminar_opcion(request, destino_id, choice_id):
    opcion = get_object_or_404(Choice, pk=choice_id, destino_id=destino_id)
    opcion.delete()
    return redirect('viajes:detalle', destino_id=destino_id)


@require_POST
def vote(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    try:
        selected_choice = destino.choice_set.get(pk=request.POST['choice'])
    except (KeyError, ValueError, Choice.DoesNotExist):
        return render(
            request,
            'viajes/detalle.html',
            {
                'destino': destino,
                'choice_form': ChoiceForm(),
                'error_message': 'No seleccionaste ninguna opción.',
            },
        )
    selected_choice.votes = F('votes') + 1
    selected_choice.save(update_fields=['votes'])
    return redirect('viajes:results', destino_id=destino.id)


def results(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    opciones = destino.choice_set.order_by('-votes', 'choice_text')
    return render(request, 'viajes/results.html', {'destino': destino, 'opciones': opciones})
