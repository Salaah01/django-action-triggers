import asyncio
from contextlib import asynccontextmanager
from copy import deepcopy

try:
    import aio_pika
except ImportError:
    aio_pika = None  # type: ignore[assignment]
from django.conf import settings


@asynccontextmanager
async def get_rabbitmq_conn(key: str = "rabbitmq_1"):
    """Get a connection to a RabbitMQ broker.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "rabbitmq_1".

    Returns:
        Connection: The connection to the broker
    """

    conn_details = deepcopy(
        settings.ACTION_TRIGGERS["brokers"][key]["conn_details"]  # type: ignore[index]  # noqa E501
    )
    conn_details["port"] = int(conn_details["port"])
    conn = await aio_pika.connect_robust(**conn_details)
    yield conn
    await conn.close()


def can_connect_to_rabbitmq() -> bool:
    """Check if the service can connect to RabbitMQ.

    Returns:
        bool: True if the service can connect to RabbitMQ, False otherwise
    """

    if aio_pika is None:
        return False

    async def _can_connect_to_rabbitmq():
        try:
            async with get_rabbitmq_conn():
                return True
        except Exception as e:
            raise e
            return False

    return asyncio.run(_can_connect_to_rabbitmq())
