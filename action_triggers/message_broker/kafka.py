"""Module to support sending messages to Kafka."""

import typing as _t

from action_triggers.base.config import ActionTriggerActionBase
from action_triggers.config_required_fields import HasField
from action_triggers.core.config import ConnectionCore
from action_triggers.enums import ActionTriggerType
from action_triggers.message_broker.error import MessageBrokerError
from action_triggers.utils.module_import import MissingImportWrapper

try:
    from aiokafka import AIOKafkaProducer  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    AIOKafkaProducer = MissingImportWrapper("AIOKafkaProducer")


class KafkaConnection(ConnectionCore):
    """Connection class for Kafka."""

    error_class = MessageBrokerError
    required_conn_detail_fields = (HasField("bootstrap_servers", str),)
    required_params_fields = (HasField("topic", str),)

    async def connect(self) -> None:
        self.conn = AIOKafkaProducer(**self.conn_details)
        await self.conn.start()

    async def close(self) -> None:
        if self.conn:
            await self.conn.stop()
        self.conn = None


class KafkaBroker(ActionTriggerActionBase):
    """Broker class for Kafka."""

    conn_class = KafkaConnection
    action_trigger_type = ActionTriggerType.BROKERS

    def __init__(
        self,
        broker_key: str,
        conn_params: _t.Union[dict, None],
        params: _t.Union[dict, None],
        **kwargs,
    ):
        super().__init__(broker_key, conn_params, params, **kwargs)
        self.topic = self.params.get("topic")

    async def _send_message_impl(self, conn: _t.Any, message: str) -> None:
        """Send a message to the Kafka broker.

        :param conn: The connection to the broker.
        :param message: The message to send.
        """

        await conn.conn.send_and_wait(self.topic, message.encode())
