#!/bin/sh
set -e

python manage.py migrate --noinput

# Crea el administrador inicial si se definen las variables (no falla si ya existe).
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py createsuperuser --noinput \
        --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" 2>/dev/null || true
fi

exec "$@"
