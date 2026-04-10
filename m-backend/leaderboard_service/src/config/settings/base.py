from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*").split(",")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "leaderboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# No database — this service uses Redis only.
DATABASES = {}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "EXCEPTION_HANDLER": "leaderboard.presentation.exception_handler.custom_exception_handler",
}

# Redis
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")

# Kafka
KAFKA_BOOTSTRAP_SERVERS = config("KAFKA_BOOTSTRAP_SERVERS", default="localhost:9092")
KAFKA_GROUP_ID = config("KAFKA_GROUP_ID", default="leaderboard-service")
KAFKA_TOPIC_SUBMIT_REWARDED = config("KAFKA_TOPIC_SUBMIT_REWARDED", default="submit.rewarded")

# Leaderboard
LEADERBOARD_TOP_N = config("LEADERBOARD_TOP_N", default=10, cast=int)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
