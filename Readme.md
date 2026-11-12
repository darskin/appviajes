# AppViajes

Plataforma web para registrar destinos de viaje, votar opciones de plan y generar itinerarios con IA.
Proyecto integrador **ExpoUninpahu 2026** — Ingeniería de Software.

**Equipo:** Johnny Esteban Buitrago Ortiz, Cristian Camilo Pachon Roman, Yulieth Alejandra Leon Pineda

## Arquitectura
Django (app web) + microservicio Node.js (IA, Swagger) + PostgreSQL + Docker Compose.

## Roles
| Rol | Permisos |
|---|---|
| Visitante | Consulta destinos, opciones y resultados; puede registrarse e iniciar sesión. |
| Viajero | Crea destinos; edita/elimina los suyos y define sus opciones; vota (un voto por destino, se puede cambiar). |
| Administrador (`is_staff`) | Gestiona todos los destinos y usuarios; accede a Django Admin (`/admin/`). |

## Ejecutar en local
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser   # administrador
.venv/bin/python manage.py runserver
```
Abrir <http://127.0.0.1:8000/>. Pruebas: `.venv/bin/python manage.py test`.

## Docker (Django + PostgreSQL)
```bash
docker compose up --build
```
Abrir <http://localhost:8000/>. Administrador de prueba: `admin` / `admin12345` (solo local).

## Variables de entorno
`SECRET_KEY`, `DEBUG` (`True`/`False`), `ALLOWED_HOSTS`, `DATABASE_URL`, `CSRF_TRUSTED_ORIGINS`,
`DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_SUPERUSER_EMAIL`.
Sin `DATABASE_URL` se usa SQLite.

## Despliegue en Render
1. En Render: **New > Blueprint** y elegir este repositorio (usa `render.yaml`: servicio web Docker + PostgreSQL).
2. Definir `DJANGO_SUPERUSER_PASSWORD` cuando lo pida.
3. Al terminar, la app queda en `https://<nombre>.onrender.com/`.

## Estado
| Entrega | Contenido | Estado |
|---|---|---|
| 1 | SRS, UML, backlog, GitHub | Entregada |
| 2 | CRUD, login, roles, Django Admin, Dockerfile, despliegue inicial, diagrama de secuencia | Código y Docker listos; falta publicar en Render |
| 3 | Microservicio Node.js, Swagger, IA, Compose | Pendiente |
