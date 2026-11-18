from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import ia_client
from .forms import ChoiceForm, DestinoForm, ItinerarioForm, RegistroForm
from .models import Choice, Destino, Voto
from .permisos import destino_gestionable


def registro(request):
    """CU-12: registra una cuenta con el rol de viajero."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            grupo, _ = Group.objects.get_or_create(name='Viajero')
            usuario.groups.add(grupo)
            login(request, usuario)
            messages.success(request, 'Cuenta creada. ¡Bienvenido!')
            return redirect('viajes:index')
    else:
        form = RegistroForm()
    return render(request, 'registration/registro.html', {'form': form})


def index(request):
    lista_destinos = Destino.objects.select_related('propietario')
    return render(request, 'viajes/index.html', {'lista_destinos': lista_destinos})


def _contexto_detalle(request, destino, **extra):
    voto = None
    if request.user.is_authenticated:
        voto = Voto.objects.filter(usuario=request.user, destino=destino).first()
    return {
        'destino': destino,
        'choice_form': ChoiceForm(),
        'voto_actual': voto,
        **extra,
    }


def detalle(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    return render(request, 'viajes/detalle.html', _contexto_detalle(request, destino))


@login_required
def crear_destino(request):
    if request.method == 'POST':
        form = DestinoForm(request.POST)
        if form.is_valid():
            destino = form.save(commit=False)
            destino.propietario = request.user
            destino.save()
            return redirect('viajes:detalle', destino_id=destino.id)
    else:
        form = DestinoForm()
    return render(request, 'viajes/destino_form.html', {'form': form, 'titulo': 'Crear Nuevo Destino'})


@destino_gestionable
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


@destino_gestionable
def eliminar_destino(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    if request.method == 'POST':
        destino.delete()
        return redirect('viajes:index')
    return render(request, 'viajes/destino_confirm_delete.html', {'destino': destino})


@require_POST
@destino_gestionable
def agregar_opcion(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    form = ChoiceForm(request.POST)
    if form.is_valid():
        opcion = form.save(commit=False)
        opcion.destino = destino
        opcion.save()
        return redirect('viajes:detalle', destino_id=destino.id)
    return render(request, 'viajes/detalle.html', _contexto_detalle(request, destino, choice_form=form))


@require_POST
@destino_gestionable
def eliminar_opcion(request, destino_id, choice_id):
    opcion = get_object_or_404(Choice, pk=choice_id, destino_id=destino_id)
    opcion.delete()
    return redirect('viajes:detalle', destino_id=destino_id)


@require_POST
@login_required
def vote(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    try:
        opcion = destino.choice_set.get(pk=request.POST['choice'])
    except (KeyError, ValueError, Choice.DoesNotExist):
        return render(
            request,
            'viajes/detalle.html',
            _contexto_detalle(request, destino, error_message='No seleccionaste ninguna opción.'),
        )
    # Un voto por usuario y destino; votar de nuevo cambia la opción elegida.
    Voto.objects.update_or_create(
        usuario=request.user, destino=destino, defaults={'opcion': opcion}
    )
    return redirect('viajes:results', destino_id=destino.id)


def results(request, destino_id):
    destino = get_object_or_404(Destino, pk=destino_id)
    opciones = destino.choice_set.annotate(votes=Count('voto')).order_by('-votes', 'choice_text')
    return render(request, 'viajes/results.html', {'destino': destino, 'opciones': opciones})


@login_required
def itinerario(request, destino_id):
    """CU-11: muestra un itinerario sugerido por IA (vía Node.js). No se guarda."""
    destino = get_object_or_404(Destino, pk=destino_id)
    resultado = error = None
    if request.method == 'POST':
        form = ItinerarioForm(request.POST)
        if form.is_valid():
            try:
                resultado = ia_client.generar_itinerario(
                    destino.nombre, destino.presupuesto, form.cleaned_data['dias']
                )
            except ia_client.IAServiceError as e:
                error = str(e)
    else:
        form = ItinerarioForm()
    return render(
        request,
        'viajes/itinerario.html',
        {'destino': destino, 'form': form, 'resultado': resultado, 'error': error},
    )
