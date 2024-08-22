import typing as _t

from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.message_broker.enums import BrokerType
from action_triggers.utils.module_import import MissingImportWrapper

try:
    import pika  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    pika = MissingImportWrapper("pika")


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
    """Broker class for RabbitMQ.

    :param broker_key: The key for the broker (must existing in
        `settings.ACTION_TRIGGERS`).
    :param conn_params: The connection parameters to use for establishing the
        connection.
    :param params: Additional parameters to use for the message broker.
    :param kwargs: Additional keyword arguments to pass to the subclass.
    """

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

        :param conn: The connection to the broker.
        :param message: The message to send.
        """

        channel = conn.conn.channel()
        channel.queue_declare(queue=self.queue)
        channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.queue,
            body=message.encode("utf-8"),
        )
