"""
Django settings for playground project.

Generated by 'django-admin startproject' using Django 4.2.15.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    "django-insecure--kj)q2!ig46k8h2e#1^p7-s5(6szq9jmv1y8de%da#)gh_1wi0"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "action_triggers",
    "sample_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "playground.urls"

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

WSGI_APPLICATION = "playground.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DB_CHOICES = {
    "sqlite": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "postgresql": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "django_action_triggers_playground",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    },
}

# Change the default key to point to the desired database defined in
# DB_CHOICES.
DATABASES = {
    "default": DB_CHOICES["postgresql"],
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Action triggers configuration
ACTION_TRIGGERS = {
    "brokers": {
        "rabbitmq_1": {
            "broker_type": "rabbitmq",
            "conn_details": {
                "host": "localhost",
                "port": 5672,
            },
            "params": {
                "queue": "test_queue_1",
            },
        },
        "rabbitmq_2": {
            "broker_type": "rabbitmq",
            "conn_details": {
                "host": "localhost",
                "port": 5672,
            },
            "params": {
                "queue": "test_queue_2",
            },
        },
        "kafka_1": {
            "broker_type": "kafka",
            "conn_details": {
                "bootstrap.servers": "localhost:29092",
            },
            "params": {
                "topic": "test_topic_1",
            },
        },
    },
    "whitelisted_content_types": (
        "sample_app.customer",
        "sample_app.product",
    ),
    "whitelisted_webhook_endpoint_patterns": (
        "https?://localhost:[0-9]+/webhook/[0-9]+/?",
        "https://example.com/",
    ),
}

ACTION_TRIGGER_SETTINGS = {
    "ALLOWED_DYNAMIC_IMPORT_PATHS": (
        "tests.test_dynamic_loading.get_webhook_headers",
        "tests.test_dynamic_loading.WEBHOOK_API_TOKEN",
        "tests.test_dynamic_loading.get_api_token",
    ),
    "MAX_BROKER_TIMEOUT": 5,
    "MAX_WEBHOOK_TIMEOUT": 30,
}
