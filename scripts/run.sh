#!/usr/bin/zsh

set -e

# Waiting for database to start
python manage.py wait_for_db
# Create static media folder
python manage.py collectstatic --noinput
# Migrate python database
python manage.py migrate

uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi
