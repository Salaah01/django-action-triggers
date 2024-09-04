import asyncio
from contextlib import asynccontextmanager

try:
    import redis.asyncio as redis
except ImportError:
    redis = None  # type: ignore[assignment]
from django.conf import settings
from action_triggers.message_broker.redis import RedisConnection


@asynccontextmanager
async def get_redis_conn(key: str = "redis_with_host"):
    """Get a connection to a Redis broker.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "redis_with_host".

    Returns:
        Connection: The connection to the broker
    """


    async with RedisConnection(
        config=settings.ACTION_TRIGGERS["brokers"][key],
        conn_details={},
        params={},
    ) as conn:
        yield conn.conn


def can_connect_to_redis() -> bool:
    """Check if the service can connect to Redis.

    Returns:
        bool: True if the service can connect to Redis, False otherwise
    """

    if redis is None:
        return False

    async def _can_connect_to_redis():
        try:
            async with get_redis_conn():
                return True
        except Exception:
            return False

    return asyncio.run(_can_connect_to_redis())
