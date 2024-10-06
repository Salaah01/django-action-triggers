"""Module to support sending messages to Redis."""

from action_triggers.base.config import ActionTriggerActionBase
from action_triggers.config_required_fields import (
    HasAtLeastOneOffField,
    HasField,
)
from action_triggers.core.config import ConnectionCore
from action_triggers.enums import ActionTriggerType
from action_triggers.message_broker.error import MessageBrokerError
from action_triggers.utils.module_import import MissingImportWrapper

try:
    import redis.asyncio as redis  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    redis = MissingImportWrapper("redis")  # type: ignore[assignment]


class RedisConnection(ConnectionCore):
    """Connection class for Redis."""

    error_class = MessageBrokerError
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


class RedisBroker(ActionTriggerActionBase):
    """Broker class for Redis."""

    conn_class = RedisConnection
    action_trigger_type = ActionTriggerType.BROKERS

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
