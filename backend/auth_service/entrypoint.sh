#!/bin/sh
set -e

echo "Waiting for postgres..."
until python -c "
import psycopg, os
psycopg.connect(
    host=os.environ['POSTGRES_HOST'],
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
)
" 2>/dev/null; do
  sleep 1
done

python manage.py migrate --noinput

python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin')

if not User.objects.filter(username=username).exists():
  User.objects.create_superuser(username=username, email=email, password=password)
  print('Created superuser:', username)
else:
  print('Superuser already exists:', username)
"

python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 60 \
  --access-logfile -
