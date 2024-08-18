import typing as _t

from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.message_broker.enums import BrokerType
from action_triggers.message_broker.exceptions import MissingDependenciesError

try:
    import pika  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    raise MissingDependenciesError("RabbitMQ", "rabbitmq", "pika")


class RabbitMQConnection(ConnectionBase):
    """Connection class for RabbitMQ."""

    def validate(self) -> None:
        if not self.params.get("queue"):
            self._errors.add_params_error(  # type: ignore[attr-defined]
                "queue",
                "Queue name must be provided.",
            )
        self._errors.is_valid(raise_exception=True)

    def connect(self):
        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(**self.conn_details)
        )


class RabbitMQBroker(BrokerBase):
    """Broker class for RabbitMQ."""

    broker_type = BrokerType.RABBITMQ
    conn_class = RabbitMQConnection

    def __init__(
        self,
        broker_key: str,
        conn_params: _t.Union[dict, None],
        params: _t.Union[dict, None],
        **kwargs,
    ):
        super().__init__(broker_key, conn_params, params, **kwargs)
        self.queue = self.params.get("queue")
        self.exchange = self.params.get("exchange", "")

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
            body=message.encode("utf-8"),
        )