"""Cliente HTTP de Django hacia el microservicio ia-service (Node.js)."""
import json
import urllib.error
import urllib.request

from django.conf import settings


class IAServiceError(Exception):
    """El microservicio no pudo generar el itinerario."""


def generar_itinerario(destino, presupuesto, dias):
    url = settings.IA_SERVICE_URL.rstrip('/') + '/api/itinerario'
    cuerpo = json.dumps({'destino': destino, 'presupuesto': presupuesto, 'dias': dias}).encode()
    cabeceras = {'Content-Type': 'application/json'}
    if settings.IA_SERVICE_API_KEY:
        cabeceras['X-API-Key'] = settings.IA_SERVICE_API_KEY
    peticion = urllib.request.Request(url, data=cuerpo, headers=cabeceras, method='POST')
    try:
        with urllib.request.urlopen(peticion, timeout=settings.IA_SERVICE_TIMEOUT) as r:
            return json.load(r)['itinerario']
    except urllib.error.HTTPError as e:
        try:
            detalle = json.load(e).get('error', '')
        except Exception:
            detalle = ''
        raise IAServiceError(detalle or f'El servicio de IA respondió con error {e.code}.') from e
    except (urllib.error.URLError, TimeoutError, OSError, KeyError, ValueError) as e:
        raise IAServiceError('No se pudo comunicar con el servicio de IA. Intenta de nuevo.') from e
