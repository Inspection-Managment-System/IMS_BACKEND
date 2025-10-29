from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())


# Get installed apps from environment and add hazard_identification
INSTALLED_APPS = config("INSTALLED_APPS", cast=Csv())
INSTALLED_APPS.append("hazard_identification")

MIDDLEWARE = config("MIDDLEWARE", cast=Csv())

ROOT_URLCONF = "ims_backend.urls"

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

WSGI_APPLICATION = "ims_backend.wsgi.application"

DATABASES = {
    # "default": {
    #     "ENGINE": config("DB_ENGINE"),
    #     "NAME": BASE_DIR / config("DB_NAME"),
    # },
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ims_db",
        "USER": "postgres",
        "PASSWORD": "admin123",
        "HOST": "localhost",
        "PORT": "5432",
    },
    "LW8Process": {
        "ENGINE": config("LW8_DB_ENGINE"),
        "NAME": config("LW8_DB_NAME"),
        "USER": config("LW8_DB_USER"),
        "PASSWORD": config("LW8_DB_PASSWORD"),
        "HOST": config("LW8_DB_HOST").encode("utf-8").decode("unicode_escape"),
        "OPTIONS": {
            "driver": config("LW8_DB_DRIVER", default="ODBC Driver 17 for SQL Server"),
        },
    },
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = config("LANGUAGE_CODE")
TIME_ZONE = config("TIME_ZONE")
USE_I18N = config("USE_I18N", cast=bool)
USE_TZ = config("USE_TZ", cast=bool)
DEFAULT_AUTO_FIELD = config("DEFAULT_AUTO_FIELD")
AUTH_USER_MODEL = config("AUTH_USER_MODEL")


CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv())

STATIC_URL = config("STATIC_URL")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (config("JWT_AUTHENTICATION_CLASS"),),
    "DEFAULT_PAGINATION_CLASS": config("DEFAULT_PAGINATION_CLASS"),
    "PAGE_SIZE": config("PAGE_SIZE"),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ALGORITHM": config("JWT_ALGORITHM"),
    "SIGNING_KEY": config("JWT_SIGNING_KEY"),
    "USER_ID_FIELD": config("JWT_USER_ID_FIELD"),
    "USER_ID_CLAIM": config("JWT_USER_ID_CLAIM"),
}

CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", cast=bool)
CORS_ALLOW_METHODS = config("CORS_ALLOW_METHODS", cast=Csv())
CORS_ALLOW_HEADERS = config("CORS_ALLOW_HEADERS", cast=Csv())
EMAIL_BACKEND = config("EMAIL_BACKEND")

EMAIL_HOST = config("EMAIL_HOST")
EMAIL_HOST_PORT = config("EMAIL_HOST_PORT")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

# Frontend URL for email links
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
