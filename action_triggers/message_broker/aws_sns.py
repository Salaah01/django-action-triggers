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

    required_conn_detail_fields = []
    required_params_fields = []

    def validate_endpoint_url_provided(self) -> None:
        """Validate that the endpoint url is provided in the connection
        details.
        """

        if "endpoint_url" not in self.conn_details.keys():
            self._errors.add_params_error(  # type: ignore[attr-defined]
                "endpoint_url",
                "An endpoint_url must be provided.",
            )

    def validate_topic_arn_provided(self) -> None:
        """Validate that the topic is provided."""

        if not self.params.get("topic_arn"):
            self._errors.add_params_error(  # type: ignore[attr-defined]
                "topic",
                "A topic must be provided.",
            )

    def validate(self) -> None:
        """Validate the connection details."""

        self.validate_endpoint_url_provided()
        self.validate_topic_arn_provided()
        super().validate()

    async def connect(self) -> None:
        """Connect to the AWS SQS service."""

        self.conn = boto3.client("sns", **self.conn_details)

    async def close(self) -> None:
        """Close the connection to the AWS SNS service."""

        self.conn = None


class AwsSnsBroker(BrokerBase):
    """Broker class for AWS SQS.

    :param broker_key: The key for the broker (must exist in the
        `settings.ACTION_TRIGGERS["brokers"]` dictionary)).
    :param conn_params: The connection parameters to use for establishing the
        connection to the broker.
    """

    broker_type = BrokerType.AWS_SNS
    conn_class = AwsSnsConnection

    async def _send_message_impl(
        self,
        conn: AwsSnsConnection,
        message: str,
    ) -> None:
        """Send a message to the AWS SQS queue.

        :param conn: The connection to the AWS SQS service.
        :param message: The message to send.
        """

        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            None,
            partial(
                conn.conn.publish,
                TopicArn=conn.params["topic_arn"],
                Message=message,
            ),
        )
