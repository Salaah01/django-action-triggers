"""Module to support sending messages to AWS SQS."""

import asyncio
from functools import partial

from action_triggers.base.config import ActionTriggerActionBase
from action_triggers.config_required_fields import (
    HasAtLeastOneOffField,
    HasField,
)
from action_triggers.core.config import ConnectionCore
from action_triggers.enums import ActionTriggerType
from action_triggers.message_broker.error import MessageBrokerError
from action_triggers.utils.module_import import MissingImportWrapper

try:
    import boto3  # type: ignore[import]
except ImportError:  # pragma: no cover
    boto3 = MissingImportWrapper("boto3")  # type: ignore[assignment]


class AwsSqsConnection(ConnectionCore):
    """Connection class for AWS SQS."""

    error_class = MessageBrokerError
    required_conn_detail_fields = (HasField("endpoint_url", str),)
    required_params_fields = (
        HasAtLeastOneOffField(fields=("queue_url", "queue_name")),
    )

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


class AwsSqsBroker(ActionTriggerActionBase):
    """Broker class for AWS SQS."""

    conn_class = AwsSqsConnection
    action_trigger_type = ActionTriggerType.BROKERS

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
        await loop.run_in_executor(
            None,
            partial(
                conn.conn.send_message,
                QueueUrl=conn.queue_url,
                MessageBody=message,
            ),
        )
