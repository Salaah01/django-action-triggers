"""Module to support sending messages to AWS SQS."""

import asyncio
from functools import partial

from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.message_broker.enums import BrokerType
from action_triggers.utils.module_import import MissingImportWrapper

try:
    import boto3  # type: ignore[import]
except ImportError:  # pragma: no cover
    boto3 = MissingImportWrapper("boto3")  # type: ignore[assignment]


class AwsSqsConnection(ConnectionBase):
    """Connection class for AWS SQS."""

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

    def validate_queue_provided(self) -> None:
        """Validate that the queue url or name is provided in the
        parameters.
        """

        # TODO: change to `queue_arn` and `queue_name`
        if not self.params.get("queue_url") and not self.params.get(
            "queue_name"
        ):
            self._errors.add_params_error(  # type: ignore[attr-defined]
                "queue",
                "Either a queue URL or name must be provided.",
            )

    def validate(self) -> None:
        """Validate the connection details."""

        self.validate_endpoint_url_provided()
        self.validate_queue_provided()
        super().validate()

    def get_queue_url(self) -> str:
        """Get the queue URL from the parameters or fetch it from AWS using the
        queue name.

        :return: The queue URL.
        """

        if self.params.get("queue_url"):
            return self.params["queue_url"]

        response = self.conn.get_queue_url(QueueName=self.params["queue_name"])
        return response["QueueUrl"]

    async def connect(self) -> None:
        """Connect to the AWS SQS service."""

        loop = asyncio.get_event_loop()
        self.conn = boto3.client("sqs", **self.conn_details)
        self.queue_url = await loop.run_in_executor(None, self.get_queue_url)

    async def close(self) -> None:
        """Close the connection to the AWS SQS service."""

        self.conn = None
        self.queue_url = None  # type: ignore[assignment]


class AwsSqsBroker(BrokerBase):
    """Broker class for AWS SQS.

    :param broker_key: The key for the broker (must exist in the
        `settings.ACTION_TRIGGERS["brokers"]` dictionary)).
    :param conn_params: The connection parameters to use for establishing the
        connection to the broker.
    """

    broker_type = BrokerType.AWS_SQS
    conn_class = AwsSqsConnection

    async def _send_message_impl(
        self,
        conn: AwsSqsConnection,
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
                conn.conn.send_message,
                QueueUrl=conn.queue_url,
                MessageBody=message,
            ),
        )
