"""Настройки для продакшена."""
from .base import *  # noqa: F401, F403

DEBUG = False

# Обязательно задать реальные хосты в env
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ["localhost", "127.0.0.1"]:  # noqa: F405
    raise ValueError(
        "В production задайте ALLOWED_HOSTS реальным доменом, например: example.com,www.example.com"
    )

# HTTPS и cookies
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Логи: WARNING+ в файл и консоль
LOG_DIR = BASE_DIR / "logs"  # noqa: F405
LOG_DIR.mkdir(exist_ok=True)

LOGGING["handlers"]["file"] = {  # noqa: F405
    "class": "logging.FileHandler",
    "filename": str(LOG_DIR / "django.log"),
    "formatter": "verbose",
}
LOGGING["root"]["handlers"] = ["console", "file"]  # noqa: F405
LOGGING["root"]["level"] = "WARNING"  # noqa: F405
LOGGING["loggers"]["django"]["level"] = "WARNING"  # noqa: F405
LOGGING["loggers"]["django.request"]["level"] = "ERROR"  # noqa: F405
