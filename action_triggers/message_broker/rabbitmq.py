import typing as _t

from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.message_broker.enums import BrokerType
from action_triggers.message_broker.exceptions import MissingDependenciesError

try:
    import pika  # type: ignore[import-untyped]
except ImportError:
    raise MissingDependenciesError("RabbitMQ", "rabbitmq", "pika")


class RabbitMQConnection(ConnectionBase):
    """Connection class for RabbitMQ."""

    def connect(self):
        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(**self.conn_params)
        )


class RabbitMQBroker(BrokerBase):
    """Broker class for RabbitMQ."""

    broker_type = BrokerType.RABBITMQ
    conn_class = RabbitMQConnection

    def __init__(self, conn_params: dict, **kwargs):
        super().__init__(conn_params, **kwargs)
        self.queue = kwargs.get("queue")
        self.exchange = kwargs.get("exchange", "")

    def validate(self) -> None:
        if not self.queue:
            raise ValueError("Queue name must be provided.")

    def _send_message_impl(self, conn: _t.Any, message: str) -> None:
        """Send a message to the RabbitMQ broker.

        Args:
            conn: The connection to the broker.
            message: The message to send.
        """

        channel = conn.conn.channel()
        channel.queue_declare(queue=self.queue)
        channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.queue,
            body=message,
        )
