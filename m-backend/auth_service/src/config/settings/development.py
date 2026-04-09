from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"