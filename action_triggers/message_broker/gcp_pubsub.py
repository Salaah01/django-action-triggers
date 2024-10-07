"""Module to support sending messages to GCP Pub/Sub.

Developer Notes:

Make sure you use the Google Pub/Sub emulator for development and testing. The
docs for the emulator can be found at
https://cloud.google.com/pubsub/docs/emulator.
"""

import asyncio
import typing as _t

from action_triggers.base.config import ActionTriggerActionBase
from action_triggers.config_required_fields import HasField
from action_triggers.core.config import ConnectionCore
from action_triggers.enums import ActionTriggerType
from action_triggers.message_broker.error import MessageBrokerError
from action_triggers.utils.module_import import MissingImportWrapper

try:
    from google.cloud import pubsub_v1  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    pubsub_v1 = MissingImportWrapper("pubsub_v1")


class GCPPubSubConnection(ConnectionCore):
    """Connection class for GCP Pub/Sub"""

    error_class = MessageBrokerError
    required_conn_detail_fields = (
        HasField("project", str),
        HasField("topic", str),
    )
    required_params_fields = ()

    async def connect(self):
        """Connect to the GCP Pub/Sub service"""
        self.conn = pubsub_v1.PublisherClient()
        loop = asyncio.get_event_loop()
        self.topic_path = await loop.run_in_executor(
            None,
            self.conn.topic_path,
            self.conn_details["project"],
            self.conn_details["topic"],
        )

    async def close(self):
        """Close the connection to the GCP Pub/Sub service"""
        self.conn = None
        self.topic_path = None


class GCPPubSubBroker(ActionTriggerActionBase):
    """Broker class for GCP Pub/Sub"""

    conn_class = GCPPubSubConnection
    action_trigger_type = ActionTriggerType.BROKERS

    async def _send_message_impl(self, conn: _t.Any, message: str):
        """Send a message to the GCP Pub/Sub broker

        :param conn: The connection to the broker
        :param message: The message to send
        """
        loop = asyncio.get_event_loop()
        future = conn.conn.publish(conn.topic_path, message.encode())
        await loop.run_in_executor(None, future.result)
