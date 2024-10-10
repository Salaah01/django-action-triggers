"""Module to generate tables for the API documentation."""

import os

from tabulate import tabulate

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_ROOT = os.path.dirname(CURRENT_DIR)
SOURCE_DIR = os.path.join(DOCS_ROOT, "source")


def optional_installations():
    headers = ["Integration", "Installation Command"]
    data = [
        ["RabbitMQ", "`pip install django-action-triggers[rabbitmq]`"],
        ["Kafka", "`pip install django-action-triggers[kafka]`"],
        ["Redis", "`pip install django-action-triggers[redis]`"],
        ["AWS SQS", "`pip install django-action-triggers[aws]`"],
        ["AWS SNS", "`pip install django-action-triggers[aws]`"],
        ["GCP Pub/Sub", "`pip install django-action-triggers[gcp]`"],
        ["AWS Lambda", "`pip install django-action-triggers[aws]`"],
        ["Webooks", "`pip install django-action-triggers[webhooks]`"],
    ]

    with open(
        os.path.join(SOURCE_DIR, "partials/optional_installations.rst"), "w+"
    ) as f:
        f.write(tabulate(data, headers, tablefmt="rst"))
