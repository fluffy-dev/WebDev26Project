from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*").split(",")

FORCE_SCRIPT_NAME = config("FORCE_SCRIPT_NAME", default="") or None

INSTALLED_APPS = [
    "django_prometheus",
    "django.contrib.admin",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "balances.apps.BalancesConfig",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "config.middleware.ForwardedPrefixMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST", default="localhost"),
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "EXCEPTION_HANDLER": "balances.presentation.exception_handler.custom_exception_handler",
}

# Kafka
KAFKA_BOOTSTRAP_SERVERS = config("KAFKA_BOOTSTRAP_SERVERS", default="localhost:9092")
KAFKA_GROUP_ID = config("KAFKA_GROUP_ID", default="balance-service")
KAFKA_TOPIC_USER_REGISTERED = config("KAFKA_TOPIC_USER_REGISTERED", default="user.registered")
KAFKA_TOPIC_SUBMIT_REWARDED = config("KAFKA_TOPIC_SUBMIT_REWARDED", default="submit.rewarded")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Observability ────────────────────────────────────────────────────────────
OTLP_ENDPOINT = config("OTLP_ENDPOINT", default="http://tempo:4317")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(service)s %(env)s %(message)s",
        }
    },
    "filters": {
        "service_context": {"()": "config.logging.ServiceContextFilter", "service_name": "balance_service"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["service_context"],
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

# S3 / Storage — only enabled when AWS_STORAGE_BUCKET_NAME is set
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL", default="")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default="us-east-1")
AWS_S3_FILE_OVERWRITE = False
AWS_S3_URL_PROTOCOL = "http"

if AWS_STORAGE_BUCKET_NAME and AWS_S3_ENDPOINT_URL:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_S3_URL_PROTOCOL}://localhost:9000/{AWS_STORAGE_BUCKET_NAME}/"
    # Keep staticfiles local in dev to avoid brittle collectstatic-on-S3 behavior.
    STATIC_URL = AWS_S3_CUSTOM_DOMAIN
else:
    STATIC_URL = "typecat-static/"

STATIC_ROOT = BASE_DIR / "staticfiles"