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
            "A key-value pair of connection details that will be used to connect to the broker. The value can receive the path to a callable that will be evaluated at runtime.",
        ],
        [
            "`params`",
            "`dict`",
            "A key-value pair of parameters that will be used to configure the broker. The value can receive the path to a callable that will be evaluated at runtime.",
        ],
    ]

    with open(os.path.join(SOURCE_DIR, "message_brokers", "config_options.rst"), "a+") as f:
        f.write(tabulate(data, headers=headers, tablefmt="rst"))