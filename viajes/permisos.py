from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Destino


def destino_gestionable(vista):
    """Exige sesión y que el usuario sea dueño del destino o administrador."""

    @wraps(vista)
    @login_required
    def envoltura(request, destino_id, *args, **kwargs):
        destino = get_object_or_404(Destino, pk=destino_id)
        if not destino.puede_gestionar(request.user):
            raise PermissionDenied
        return vista(request, destino_id, *args, **kwargs)

    return envoltura
