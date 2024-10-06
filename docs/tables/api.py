"""Module to generate tables for the API documentation."""

import os

from tabulate import tabulate

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_ROOT = os.path.dirname(CURRENT_DIR)
SOURCE_DIR = os.path.join(DOCS_ROOT, "source")


def field_descriptions():
    headers = ["Field", "Constraint", "Description"]
    data = [
        [
            "`config_signals`",
            '`{"signal": string}[]`',
            'The list of signals objects that will trigger the action. For example: `[{"signal": "post_save"}]`.',
        ],
        [
            "`content_types`",
            "`object[]`",
            "The list of content types that will trigger the action.",
        ],
        [
            "`content_types.app_label`",
            "`string`",
            "The app label of the model that will trigger the action.",
        ],
        [
            "`content_types.model_name`",
            "`string`",
            "The model name that will trigger the action.",
        ],
        [
            "`webhooks`",
            "`object[]` (optional)",
            "The list of webhooks that will be triggered.",
        ],
        ["`webhooks.url`", "`string`", "The URL of the webhook."],
        [
            "`webhooks.http_method`",
            "`string`",
            "The HTTP method of the webhook.",
        ],
        [
            "`webhooks.headers`",
            "`object[]` (optional)",
            "A key-value pair of headers that will be sent with the webhook. The value can receive the path to a callable that will be evaluated at runtime.",
        ],
        [
            "`webhooks.timeout_secs`",
            "`float`",
            "The timeout in seconds for the webhook to respond before aborting the request.",
        ],
        [
            "`msg_broker_queues`",
            "`object[]` (optional)",
            "The list of queues that will be receive the message.",
        ],
        [
            "`msg_broker_queues.name`",
            "`string`",
            "The name of the queue as defined in `settings.py.ACTION_TRIGGERS.brokers`",
        ],
        [
            "`msg_broker_queues.connection_details`",
            "`object[]` (optional)",
            "A key-value pair of connection details that will be used to connect to the broker. The value can receive the path to a callable that will be evaluated at runtime. If not provided, then `settings.ACTION_TRIGGERS.brokers.<name>.conn_details` will be used instead.",
        ],
        [
            "`msg_broker_queues.parameters`",
            "`object[]` (optional)",
            "A key-value pair of parameters that will be sent with the message. The value can receive the path to a callable that will be evaluated at runtime. If not provided, then `settings.ACTION_TRIGGERS.brokers.<name>.params` will be used instead.",
        ],
        [
            "`msg_broker_queues.timeout_secs`",
            "`float`",
            "The timeout in seconds for the message broker to respond before aborting the request.",
        ],
        ["`active`", "`boolean`", "Whether the trigger is enabled or not."],
        [
            "`payload`",
            "`object[]` (optional)",
            "A Django template like value. If the resulting value after any parsing is JSON-serializable, then the returning payload will be JSON, otherwise, it'll be just plain text.",
        ],
    ]

    with open(
        os.path.join(SOURCE_DIR, "api/field_descriptions.rst"), "w+"
    ) as f:
        f.write(tabulate(data, headers, tablefmt="rst"))
