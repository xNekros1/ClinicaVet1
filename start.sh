#!/usr/bin/env bash
# Script de inicio para Render
set -o errexit

# Ejecutar migraciones (por si acaso no se ejecutaron en el build)
python manage.py migrate --noinput

# Iniciar servidor
exec gunicorn clinica_veterinaria.wsgi:application

