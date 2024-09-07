"""Module to support sending messages to AWS SNS."""

import asyncio
from functools import partial

from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.message_broker.enums import BrokerType
from action_triggers.utils.module_import import MissingImportWrapper

try:
    import boto3  # type: ignore[import]
except ImportError:  # pragma: no cover
    boto3 = MissingImportWrapper("boto3")  # type: ignore[assignment]


class AwsSnsConnection(ConnectionBase):
    """Connection class for AWS SNS."""

    def validate_endpoint_url_provided(self) -> None:
        """Validate that the endpoint url is provided in the connection
        details.
        """

        if "endpoint_url" not in self.conn_details.keys():
            self._errors.add_params_error(  # type: ignore[attr-defined]
                "endpoint_url",
                "An endpoint_url must be provided.",
            )

    def validate_topic_provided(self) -> None:
        """Validate that the topic is provided."""

        if "topic" not in self.params.keys():
            self._errors.add_params_error(  # type: ignore[attr-defined]
                "topic",
                "A topic must be provided.",
            )

    def validate(self) -> None:
        """Validate the connection details."""

        self.validate_endpoint_url_provided()
        self.validate_topic_provided()
        super().validate()

    async def connect(self) -> None:
        """Connect to the AWS SQS service."""

        loop = asyncio.get_event_loop()
        self.conn = loop.run_in_executor(
            None,
            partial(
                boto3.client,
                "sns",
                **self.conn_details,
            ),
        )

    async def close(self) -> None:
        """Close the connection to the AWS SNS service."""

        self.conn = None
