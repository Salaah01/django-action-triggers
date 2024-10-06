"""Module to support sending messages to RabbitMQ."""

import typing as _t
from copy import deepcopy

from action_triggers.base.config import ActionTriggerActionBase
from action_triggers.config_required_fields import HasField
from action_triggers.core.config import ConnectionCore
from action_triggers.enums import ActionTriggerType
from action_triggers.message_broker.error import MessageBrokerError
from action_triggers.utils.module_import import MissingImportWrapper

try:
    import aio_pika  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    aio_pika = MissingImportWrapper("aio_pika")  # type: ignore[assignment]


class RabbitMQConnection(ConnectionCore):
    """Connection class for RabbitMQ."""

    error_class = MessageBrokerError
    required_conn_detail_fields = ()
    required_params_fields = (HasField("queue", str),)

    def validate(self) -> None:
        # Python 3.8 requires the port to be an integer.
        # Resetting the cached connection details to ensure that when the lazy
        # property is accessed, the updated port is used.
        super().validate()
        self._conn_details = None
        if "port" in self._user_conn_details:
            self._user_conn_details = deepcopy(self._user_conn_details)
            self._user_conn_details["port"] = int(
                self._user_conn_details["port"]
            )

    async def connect(self) -> None:
        self.conn = await aio_pika.connect_robust(
            **self.conn_details,
        )

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
        self.conn = None


class RabbitMQBroker(ActionTriggerActionBase):
    """Broker class for RabbitMQ.

    :param hey: The key for the broker (must existing in
        `settings.ACTION_TRIGGERS["brokers"]`).
    :param conn_params: The connection parameters to use for establishing the
        connection.
    :param params: Additional parameters to use for the message broker.
    :param kwargs: Additional keyword arguments to pass to the subclass.
    """

    conn_class = RabbitMQConnection
    action_trigger_type = ActionTriggerType.BROKERS

    def __init__(
        self,
        key: str,
        conn_params: _t.Union[dict, None],
        params: _t.Union[dict, None],
        **kwargs,
    ):
        super().__init__(key, conn_params, params, **kwargs)
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
