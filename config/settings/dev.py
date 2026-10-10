"""Настройки для локальной разработки."""
from .base import *  # noqa: F401, F403

DEBUG = config("DEBUG", default=True, cast=bool)  # noqa: F405

# В разработке удобнее подробные логи
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["django"]["level"] = "DEBUG"  # noqa: F405

# Опционально: console email, если в .env не задан SMTP
if config("EMAIL_BACKEND", default="").endswith("console.EmailBackend"):  # noqa: F405
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
