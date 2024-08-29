import json
import os
import typing as _t

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", ":memory:"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    },
}

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.auth",
    "action_triggers",
    "tests",
)

MIDDLEWARE: _t.List[str] = []

ROOT_URLCONF = "tests.urls"

USE_TZ = True

TIME_ZONE = "UTC"

SECRET_KEY = "foobar"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    }
]


STATIC_URL = "/static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Message broker connection details
# These are the default values if the environment variables are not set. In
# this case, we will assume that the message brokers are running locally.

DEFAULT_RABBIT_MQ_CONN_DETAILS = {
    "host": os.getenv("RABBIT_MQ_HOST", "localhost"),
    "port": os.getenv("RABBIT_MQ_PORT", 5672),
}
RABBIT_MQ_CONN_DETAILS = (
    json.loads(os.getenv("RABBIT_MQ_CONN_DETAILS", "{}"))
    or DEFAULT_RABBIT_MQ_CONN_DETAILS
)
DEFAULT_KAFKA_CONN_DETAILS = {
    "bootstrap.servers": "localhost:9092",
}
KAFKA_CONN_DETAILS = (
    json.loads(os.getenv("KAFKA_CONN_DETAILS", "{}"))
    or DEFAULT_KAFKA_CONN_DETAILS
)


ACTION_TRIGGERS = {
    "brokers": {
        "rabbitmq_1": {
            "broker_type": "rabbitmq",
            "conn_details": RABBIT_MQ_CONN_DETAILS,
            "params": {
                "queue": "test_queue_1",
            },
        },
        "rabbitmq_2": {
            "broker_type": "rabbitmq",
            "conn_details": RABBIT_MQ_CONN_DETAILS,
            "params": {
                "queue": "test_queue_2",
            },
        },
        "kafka_1": {
            "broker_type": "kafka",
            "conn_details": KAFKA_CONN_DETAILS,
            "params": {
                "topic": "test_topic_1",
            },
        },
        "kafka_2": {
            "broker_type": "kafka",
            "conn_details": KAFKA_CONN_DETAILS,
            "params": {
                "topic": "test_topic_2",
            },
        },
    },
    "whitelisted_content_types": (
        "tests.customermodel",
        "tests.customerordermodel",
        "tests.m2mmodel",
        "tests.one2onemodel",
    ),
}

ACTION_TRIGGER_SETTINGS = {
    "ALLOWED_DYNAMIC_IMPORT_PATHS": (
        "tests.test_dynamic_loading.get_webhook_headers",
        "tests.test_dynamic_loading.WEBHOOK_API_TOKEN",
        "tests.test_dynamic_loading.get_api_token",
    )
}
