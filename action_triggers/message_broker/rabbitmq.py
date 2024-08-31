import typing as _t
from copy import deepcopy

from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.message_broker.enums import BrokerType
from action_triggers.utils.module_import import MissingImportWrapper

try:
    import aio_pika  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    aio_pika = MissingImportWrapper("aio_pika")  # type: ignore[assignment]


class RabbitMQConnection(ConnectionBase):
    """Connection class for RabbitMQ."""

    def validate_queue_exists(self):
        """Validate the the queue exists either in the base configuration or
        the user provided parameters.
        """

        if not self.config.get("queue") and not self.params.get("queue"):
            self._errors.add_params_error(  # type: ignore[attr-defined]
                "queue",
                "Queue name must be provided.",
            )

    def validate(self) -> None:
        self.validate_queue_exists()
        super().validate()

        # Python 3.8 requires the port to be an integer.
        if "port" in self.conn_details:
            self.conn_details = deepcopy(self.conn_details)
            self.conn_details["port"] = int(self.conn_details["port"])

    async def connect(self) -> None:
        self.conn = await aio_pika.connect_robust(
            **self.conn_details,
        )

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
        self.conn = None


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

    async def _send_message_impl(self, conn: _t.Any, message: str) -> None:
        """Send a message to the RabbitMQ broker.

        :param conn: The connection to the broker.
        :param message: The message to send.
        """

        async with conn.conn as connection:
            async with connection.channel() as channel:
                await channel.default_exchange.publish(
                    aio_pika.Message(body=message.encode()),
                    routing_key=self.queue,
                )
