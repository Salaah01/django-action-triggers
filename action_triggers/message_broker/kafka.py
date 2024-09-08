"""Module to support sending messages to Kafka."""

import typing as _t

from action_triggers.config_required_fields import HasField
from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.message_broker.enums import BrokerType
from action_triggers.utils.module_import import MissingImportWrapper

try:
    from aiokafka import AIOKafkaProducer  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    AIOKafkaProducer = MissingImportWrapper("AIOKafkaProducer")


class KafkaConnection(ConnectionBase):
    """Connection class for Kafka."""

    required_conn_detail_fields = (HasField("bootstrap_servers", str),)
    required_params_fields = (HasField("topic", str),)

    async def connect(self) -> None:
        self.conn = AIOKafkaProducer(**self.conn_details)
        await self.conn.start()

    async def close(self) -> None:
        if self.conn:
            await self.conn.stop()
        self.conn = None


class KafkaBroker(BrokerBase):
    """Broker class for Kafka."""

    broker_type = BrokerType.KAFKA
    conn_class = KafkaConnection

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
