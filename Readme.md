# AppViajes

Plataforma web para registrar destinos de viaje, votar opciones de plan y generar itinerarios con IA.
Proyecto integrador **ExpoUninpahu 2026** — Ingeniería de Software.

**Equipo:** Johnny Esteban Buitrago Ortiz, Cristian Camilo Pachon Roman, Yulieth Alejandra Leon Pineda

## Arquitectura
Django (app web) + microservicio Node.js (IA, Swagger) + PostgreSQL + Docker Compose. 

## Documentación
La documentación de la Entrega 1 (SRS, diagramas UML, backlog y matriz de trazabilidad) se entrega en la carpeta Entrega1_AppViajes.

## Ejecutar en local
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```
Abrir <http://127.0.0.1:8000/>. Pruebas: `.venv/bin/python manage.py test viajes`.

## Estado
| Entrega | Contenido | Estado |
|---|---|---|
| 1 | SRS, UML, backlog, GitHub | En curso |
| 2 | CRUD, login, roles, Docker, despliegue | Pendiente (CRUD de destinos listo) |
| 3 | Microservicio Node.js, Swagger, IA, Compose | Pendiente |
