import typing as _t

import pika

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

INSTALLED_APPS = (
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
                "connection": pika.PlainCredentials("user", "password"),
            },
            "params": {
                "queue": "test_queue_2",
            },
        },
        "kafka_1": {
            "broker_type": "kafka",
            "conn_details": {
                "bootstrap_servers": "localhost:9092",
            },
            "params": {
                "topic": "test_topic_1",
            },
        },
        "kafka_2": {
            "broker_type": "kafka",
            "conn_details": {
                "bootstrap_servers": "localhost:9092",
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "PLAIN",
                "sasl_plain_username": "user",
                "sasl_plain_password": "password",
            },
            "params": {
                "topic": "test_topic_2",
            },
        },
    }
}
