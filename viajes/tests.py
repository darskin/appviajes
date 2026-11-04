from django.test import TestCase
from django.urls import reverse

from .models import Choice, Destino


class ViajesTests(TestCase):
    def setUp(self):
        self.destino = Destino.objects.create(
            nombre='Guatavita', descripcion='Laguna', presupuesto=100000
        )

    def test_index_y_detalle(self):
        self.assertContains(self.client.get(reverse('viajes:index')), 'Guatavita')
        self.assertContains(self.client.get(reverse('viajes:detalle', args=[self.destino.id])), 'COP')

    def test_crear_editar_eliminar(self):
        datos = {'nombre': 'Tabio', 'descripcion': 'Peña', 'presupuesto': 5000}
        self.client.post(reverse('viajes:crear_destino'), datos)
        d = Destino.objects.get(nombre='Tabio')
        datos['nombre'] = 'Tabio 2'
        self.client.post(reverse('viajes:editar_destino', args=[d.id]), datos)
        d.refresh_from_db()
        self.assertEqual(d.nombre, 'Tabio 2')
        self.client.post(reverse('viajes:eliminar_destino', args=[d.id]))
        self.assertFalse(Destino.objects.filter(pk=d.id).exists())

    def test_presupuesto_negativo_invalido(self):
        r = self.client.post(reverse('viajes:crear_destino'),
                             {'nombre': 'x', 'descripcion': 'y', 'presupuesto': -1})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Destino.objects.count(), 1)

    def test_agregar_votar_y_eliminar_opcion(self):
        self.client.post(reverse('viajes:agregar_opcion', args=[self.destino.id]),
                         {'choice_text': 'Fin de semana'})
        c = Choice.objects.get()
        self.client.post(reverse('viajes:vote', args=[self.destino.id]), {'choice': c.id})
        c.refresh_from_db()
        self.assertEqual(c.votes, 1)
        self.client.post(reverse('viajes:eliminar_opcion', args=[self.destino.id, c.id]))
        self.assertEqual(Choice.objects.count(), 0)

    def test_voto_sin_opcion_y_get_no_permitido(self):
        r = self.client.post(reverse('viajes:vote', args=[self.destino.id]), {})
        self.assertContains(r, 'No seleccionaste')
        self.assertEqual(self.client.get(reverse('viajes:vote', args=[self.destino.id])).status_code, 405)
