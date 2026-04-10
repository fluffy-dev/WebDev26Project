#!/bin/sh
set -e

python manage.py migrate --run-syncdb || true

# Start the Kafka consumer in the background
python manage.py run_leaderboard_consumer &

# Start Gunicorn
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --timeout 30
