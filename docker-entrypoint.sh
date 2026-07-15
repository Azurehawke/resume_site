#!/bin/sh
set -e

mkdir -p "${APP_DATA_DIR:-/data}/media"

python manage.py migrate --noinput

exec "$@"
