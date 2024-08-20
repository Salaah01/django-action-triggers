"""Module to generate tables for the message brokers documentation."""

import os

from tabulate import tabulate

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_ROOT = os.path.dirname(CURRENT_DIR)
SOURCE_DIR = os.path.join(DOCS_ROOT, "source")


def config_options():
    headers = ["Field", "Type", "Description"]

    data = [
        [
            "`broker_config_name`",
            "`string`",
            "A unique name for the broker configuration.",
        ],
        [
            "`broker_type`",
            "`string`",
            "The type of the broker. Can be either `rabbitmq` or `kafka`.",
        ],
        [
            "`conn_details`",
            "`dict`",
            "Connection details required to establish a connection with the broker, such as host, port, username, and password.",
        ],
        [
            "`params`",
            "`dict`",
            "Additional parameters specific to the broker, such as the name of the queue for RabbitMQ or the topic for Kafka.",
        ],
    ]

    with open(
        os.path.join(SOURCE_DIR, "message_brokers", "config_options.rst"), "a+"
    ) as f:
        f.write(tabulate(data, headers=headers, tablefmt="rst"))
