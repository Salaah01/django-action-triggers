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
            "`action_config_name`",
            "`string`",
            "A unique name for the action configuration.",
        ],
        [
            "`action_type`",
            "`string`",
            "The type of the action (e.g: `aws_lambda`, etc.)",
        ],
        [
            "`conn_details`",
            "`dict`",
            "Connection details required to establish a connection with the action, such as host, port, username, and password.",
        ],
        [
            "`params`",
            "`dict`",
            "Additional parameters specific to the action, such as the function name for AWS Lambda.",
        ],
    ]

    with open(
        os.path.join(SOURCE_DIR, "actions", "config_options.rst"), "w+"
    ) as f:
        f.write(tabulate(data, headers=headers, tablefmt="rst"))
