"""Module to support sending messages to Redis."""

from action_triggers.message_broker.base import BrokerBase, ConnectionBase
from action_triggers.message_broker.enums import BrokerType
from action_triggers.utils.module_import import MissingImportWrapper

try:
    import redis.asyncio as redis  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    redis = MissingImportWrapper("redis")  # type: ignore[assignment]


class RedisConnection(ConnectionBase):
    """Connection class for Redis."""

    def validate_either_url_or_host_provided(self) -> None:
        """Validate that either a URL or host is provided in the connection
        details.
        """

        if not self.conn_details.get("url") and not self.conn_details.get(
            "host"
        ):
            self._errors.add_params_error(  # type: ignore[attr-defined]
                "url",
                "Either a URL or host must be provided.",
            )

    def validate_channel_exists(self) -> None:
        """Validate that the channel exists in the parameters."""

        if not self.params.get("channel"):
            self._errors.add_params_error(  # type: ignore[attr-defined]
                "channel",
                "Channel name must be provided.",
            )

    def validate(self) -> None:
        """Validate the connection details."""

        self.validate_either_url_or_host_provided()
        self.validate_channel_exists()
        super().validate()

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
        self, conn: redis.Redis, message: str
    ) -> None:
        """Send a message to the Redis server.

        :param conn: The connection to the Redis server.
        :param message: The message to send.
        """

        await conn.conn.publish(self.params["channel"], message)
