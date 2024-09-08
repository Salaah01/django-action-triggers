"""Module to support sending messages to Redis."""

from action_triggers.config_required_fields import (
    HasAtLeastOneOffField,
    HasField,
)
from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.message_broker.enums import BrokerType
from action_triggers.utils.module_import import MissingImportWrapper

try:
    import redis.asyncio as redis  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    redis = MissingImportWrapper("redis")  # type: ignore[assignment]


class RedisConnection(ConnectionBase):
    """Connection class for Redis."""

    required_conn_detail_fields = (
        HasAtLeastOneOffField(fields=("url", "host")),
    )
    required_params_fields = (HasField("channel", str),)

    async def connect(self) -> None:
        """Connect to the Redis server."""
        if self.conn_details.get("url"):
            self.conn = await redis.from_url(**self.conn_details)
        else:
            self.conn = await redis.Redis(**self.conn_details)

    async def close(self) -> None:
        """Close the connection to the Redis server."""

        if self.conn:
            await self.conn.aclose()
        self.conn = None


class RedisBroker(BrokerBase):
    """Broker class for Redis.

    :param broker_key: The key for the broker (must existing in
        `settings.ACTION_TRIGGERS`).
    :param conn_params: The connection parameters to use for establishing the
        connection.
    :param params: Additional parameters to use for the message broker.
    :param kwargs: Additional keyword arguments to pass to the subclass.
    """

    broker_type = BrokerType.REDIS
    conn_class = RedisConnection

    async def _send_message_impl(
        self,
        conn: RedisConnection,
        message: str,
    ) -> None:
        """Send a message to the Redis server.

        :param conn: The connection to the Redis server.
        :param message: The message to send.
        """

        await conn.conn.publish(self.params["channel"], message)
