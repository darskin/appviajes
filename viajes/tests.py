from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Choice, Destino, Voto


class BaseTestCase(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user('ana', password='clave-segura-123')
        self.beto = User.objects.create_user('beto', password='clave-segura-123')
        self.admin = User.objects.create_user('admin', password='clave-segura-123', is_staff=True)
        self.destino = Destino.objects.create(
            nombre='Guatavita', descripcion='Laguna', presupuesto=100000, propietario=self.ana
        )

    def entrar(self, usuario):
        self.client.login(username=usuario, password='clave-segura-123')


class AccesoPublicoTests(BaseTestCase):
    def test_visitante_consulta_destinos_opciones_y_resultados(self):
        Choice.objects.create(destino=self.destino, choice_text='Fin de semana')
        self.assertContains(self.client.get(reverse('viajes:index')), 'Guatavita')
        self.assertContains(self.client.get(reverse('viajes:detalle', args=[self.destino.id])), 'Fin de semana')
        self.assertEqual(self.client.get(reverse('viajes:results', args=[self.destino.id])).status_code, 200)

    def test_visitante_es_redirigido_al_login_al_gestionar(self):
        for nombre, args in [('crear_destino', []), ('editar_destino', [self.destino.id]),
                             ('eliminar_destino', [self.destino.id])]:
            r = self.client.get(reverse(f'viajes:{nombre}', args=args))
            self.assertEqual(r.status_code, 302)
            self.assertIn('/cuentas/login/', r.url)

    def test_visitante_no_puede_votar(self):
        op = Choice.objects.create(destino=self.destino, choice_text='A')
        r = self.client.post(reverse('viajes:vote', args=[self.destino.id]), {'choice': op.id})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Voto.objects.count(), 0)


class CuentasTests(BaseTestCase):
    def test_registro_crea_viajero_e_inicia_sesion(self):
        r = self.client.post(reverse('registro'), {
            'username': 'carla', 'password1': 'clave-segura-123', 'password2': 'clave-segura-123'})
        self.assertRedirects(r, reverse('viajes:index'))
        carla = User.objects.get(username='carla')
        self.assertFalse(carla.is_staff)
        self.assertTrue(carla.groups.filter(name='Viajero').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), carla.id)

    def test_login_y_logout(self):
        r = self.client.post(reverse('login'), {'username': 'ana', 'password': 'clave-segura-123'})
        self.assertRedirects(r, reverse('viajes:index'))
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_con_clave_incorrecta(self):
        r = self.client.post(reverse('login'), {'username': 'ana', 'password': 'mala'})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)


class CrudYRolesTests(BaseTestCase):
    def test_viajero_crea_destino_y_queda_como_propietario(self):
        self.entrar('beto')
        self.client.post(reverse('viajes:crear_destino'),
                         {'nombre': 'Tabio', 'descripcion': 'Peña', 'presupuesto': 5000})
        self.assertEqual(Destino.objects.get(nombre='Tabio').propietario, self.beto)

    def test_viajero_edita_y_elimina_solo_los_suyos(self):
        self.entrar('ana')
        datos = {'nombre': 'Guatavita 2', 'descripcion': 'x', 'presupuesto': 10}
        self.client.post(reverse('viajes:editar_destino', args=[self.destino.id]), datos)
        self.destino.refresh_from_db()
        self.assertEqual(self.destino.nombre, 'Guatavita 2')
        self.client.post(reverse('viajes:eliminar_destino', args=[self.destino.id]))
        self.assertFalse(Destino.objects.filter(pk=self.destino.id).exists())

    def test_viajero_no_toca_destinos_ajenos(self):
        self.entrar('beto')
        datos = {'nombre': 'Hack', 'descripcion': 'x', 'presupuesto': 10}
        self.assertEqual(self.client.post(reverse('viajes:editar_destino', args=[self.destino.id]), datos).status_code, 403)
        self.assertEqual(self.client.post(reverse('viajes:eliminar_destino', args=[self.destino.id])).status_code, 403)
        self.assertEqual(self.client.post(reverse('viajes:agregar_opcion', args=[self.destino.id]),
                                          {'choice_text': 'x'}).status_code, 403)
        self.destino.refresh_from_db()
        self.assertEqual(self.destino.nombre, 'Guatavita')

    def test_administrador_gestiona_cualquier_destino(self):
        self.entrar('admin')
        datos = {'nombre': 'Editado por admin', 'descripcion': 'x', 'presupuesto': 10}
        self.client.post(reverse('viajes:editar_destino', args=[self.destino.id]), datos)
        self.destino.refresh_from_db()
        self.assertEqual(self.destino.nombre, 'Editado por admin')
        self.client.post(reverse('viajes:eliminar_destino', args=[self.destino.id]))
        self.assertFalse(Destino.objects.filter(pk=self.destino.id).exists())

    def test_eliminar_destino_elimina_opciones_y_votos(self):
        op = Choice.objects.create(destino=self.destino, choice_text='A')
        Voto.objects.create(usuario=self.beto, destino=self.destino, opcion=op)
        self.destino.delete()
        self.assertEqual(Choice.objects.count(), 0)
        self.assertEqual(Voto.objects.count(), 0)

    def test_presupuesto_debe_ser_mayor_que_cero(self):
        self.entrar('ana')
        for valor in (0, -1):
            r = self.client.post(reverse('viajes:crear_destino'),
                                 {'nombre': 'x', 'descripcion': 'y', 'presupuesto': valor})
            self.assertEqual(r.status_code, 200)
        self.assertEqual(Destino.objects.count(), 1)
        with self.assertRaises(ValidationError):
            Destino(nombre='x', descripcion='y', presupuesto=0).full_clean()


class VotacionTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.a = Choice.objects.create(destino=self.destino, choice_text='A')
        self.b = Choice.objects.create(destino=self.destino, choice_text='B')

    def votar(self, opcion):
        return self.client.post(reverse('viajes:vote', args=[self.destino.id]), {'choice': opcion.id})

    def test_un_voto_por_usuario_y_se_puede_cambiar(self):
        self.entrar('beto')
        self.votar(self.a)
        self.votar(self.a)
        self.assertEqual(Voto.objects.filter(usuario=self.beto).count(), 1)
        self.votar(self.b)
        self.assertEqual(Voto.objects.get(usuario=self.beto).opcion, self.b)

    def test_resultados_cuentan_votos_por_opcion(self):
        self.entrar('beto'); self.votar(self.a); self.client.logout()
        self.entrar('ana'); self.votar(self.a)
        r = self.client.get(reverse('viajes:results', args=[self.destino.id]))
        self.assertContains(r, 'A -- 2 votos')
        self.assertContains(r, 'B -- 0 votos')

    def test_voto_sin_opcion_y_get_no_permitido(self):
        self.entrar('beto')
        r = self.client.post(reverse('viajes:vote', args=[self.destino.id]), {})
        self.assertContains(r, 'No seleccionaste')
        self.assertEqual(self.client.get(reverse('viajes:vote', args=[self.destino.id])).status_code, 405)

    def test_agregar_y_eliminar_opcion_por_el_propietario(self):
        self.entrar('ana')
        self.client.post(reverse('viajes:agregar_opcion', args=[self.destino.id]), {'choice_text': 'C'})
        c = Choice.objects.get(choice_text='C')
        self.client.post(reverse('viajes:eliminar_opcion', args=[self.destino.id, c.id]))
        self.assertFalse(Choice.objects.filter(pk=c.id).exists())


class AdminTests(BaseTestCase):
    def test_django_admin_solo_para_personal(self):
        self.entrar('ana')
        self.assertEqual(self.client.get('/admin/').status_code, 302)
        self.client.logout()
        self.entrar('admin')
        User.objects.filter(username='admin').update(is_superuser=True)
        self.assertEqual(self.client.get('/admin/viajes/destino/').status_code, 200)
