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

## Microservicio ia-service (Node.js)
Genera itinerarios con IA generativa (Google Gemini). Django lo llama por HTTP desde `/viajes/<id>/itinerario/`.
- Documentación Swagger/OpenAPI pública: `<URL de ia-service>/docs` (JSON en `/openapi.json`).
- Endpoint: `POST /api/itinerario` con `{"destino": "...", "presupuesto": 300000, "dias": 2}`; `GET /health`.
- Pruebas: `cd ia-service && npm test`.

## Docker Compose (Django + ia-service + PostgreSQL)
```bash
cp .env.example .env      # poner GEMINI_API_KEY (https://aistudio.google.com/apikey)
docker compose up --build
```
- Django: <http://localhost:8000/> (administrador de prueba `admin` / `admin12345`, solo local).
- Swagger: <http://localhost:3000/docs>

## Variables de entorno
`SECRET_KEY`, `DEBUG` (`True`/`False`), `ALLOWED_HOSTS`, `DATABASE_URL`, `CSRF_TRUSTED_ORIGINS`,
`DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_SUPERUSER_EMAIL`,
`IA_SERVICE_URL`, `SERVICE_API_KEY` (misma clave en Django y ia-service), `GEMINI_API_KEY` (solo ia-service).
Sin `DATABASE_URL` se usa SQLite.

## Despliegue en Render
1. **New > Blueprint** y elegir este repositorio (`render.yaml`: Django, ia-service y PostgreSQL).
2. Pide `DJANGO_SUPERUSER_PASSWORD`, `GEMINI_API_KEY` e `IA_SERVICE_URL`. Esta última es la URL pública de `ia-service` (aparece cuando termine de crearse; se puede completar después en Environment).
3. Django: `https://<appviajes>.onrender.com/`. Swagger: `https://<ia-service>.onrender.com/docs`.

## Estado
| Entrega | Contenido | Estado |
|---|---|---|
| 1 | SRS, UML, backlog, GitHub | Entregada |
| 2 | CRUD, login, roles, Django Admin, Dockerfile, despliegue inicial, diagrama de secuencia | Entregada |
| 3 | Microservicio Node.js, Swagger, IA, Compose | Código listo; falta desplegar ia-service y configurar la clave de IA |
