#!/bin/sh
set -e

# Espera opcional si tu BD tarda (descomenta si aplica)
# sleep 3

python manage.py migrate --noinput
python manage.py seed_users --password "miPassSeguro123" --empresa "MiEmpresa"
python manage.py runserver 0.0.0.0:8000
