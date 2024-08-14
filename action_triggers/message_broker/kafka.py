import typing as _t

from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.message_broker.enums import BrokerType
from action_triggers.message_broker.exceptions import MissingDependenciesError

try:
    from kafka import KafkaProducer  # type: ignore[import-untyped]
except ImportError:
    raise MissingDependenciesError("Kafka", "kafka", "kafka-python")


class KafkaConnection(ConnectionBase):
    """Connection class for Kafka."""

    def connect(self):
        self.conn = KafkaProducer(**self.conn_params)


class KafkaBroker(BrokerBase):
    """Broker class for Kafka."""

    broker_type = BrokerType.KAFKA
    conn_class = KafkaConnection

    def __init__(self, conn_params: dict, **kwargs):
        super().__init__(conn_params, **kwargs)
        self.topic = kwargs.get("topic", None)

    def validate(self) -> None:
        if not self.topic:
            raise ValueError("Topic name must be provided.")

    def _send_message_impl(self, conn: _t.Any, message: str) -> None:
        """Send a message to the Kafka broker.

        Args:
            conn: The connection to the broker.
            message: The message to send.
        """

        conn.conn.send(self.topic, message.encode())
