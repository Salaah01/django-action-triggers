from contextlib import asynccontextmanager
import asyncio

try:
    import aio_pika  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    aio_pika = None
try:
    from aiokafka import AIOKafkaConsumer, AIOKafkaProducer  # type: ignore[import]  # noqa E501
except ImportError:  # pragma: no cover
    AIOKafkaConsumer = AIOKafkaProducer = None
from django.conf import settings


async def get_rabbitmq_conn(key: str = "rabbitmq_1"):
    """Get a connection to a RabbitMQ broker.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "rabbitmq_1".

    Returns:
        Connection: The connection to the broker
    """

    return await aio_pika.connect_robust(
        **settings.ACTION_TRIGGERS["brokers"][key]["conn_details"],  # type: ignore[index]  # noqa E501
    )


@asynccontextmanager
async def get_kafka_conn(key: str = "kafka_1"):
    """Get a connection to a Kafka broker.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "kafka_1".

    Yields:
        Consumer: The connection to the broker
    """

    consumer = AIOKafkaConsumer(
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        group_id="test_group_1",
        **settings.ACTION_TRIGGERS["brokers"][key]["conn_details"],  # type: ignore[index]  # noqa E501
    )

    await consumer.start()

    yield consumer

    await consumer.stop()


@asynccontextmanager
async def get_kafka_consumer(key: str = "kafka_1"):
    """Consume a message from a Kafka broker.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "kafka_1".

    Returns:
        Consumer: The Kafka consumer
    """

    with get_kafka_conn(key) as conn:
        conn.subscribe(
            settings.ACTION_TRIGGERS["brokers"][key]["params"]["topic"],  # type: ignore[index]  # noqa E501
        )

        yield conn


@asynccontextmanager
async def get_kafka_producer(key: str = "kafka_1"):
    """Get a Kafka producer.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "kafka_1".

    Yields:
        Producer: The Kafka producer
    """

    producer = AIOKafkaProducer(
        **settings.ACTION_TRIGGERS["brokers"][key]["conn_details"],  # type: ignore[index]  # noqa E501
    )
    await producer.start()
    yield producer

    await producer.close()


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
        except Exception:
            return False


def can_connect_to_kafka() -> bool:
    """Check if the service can connect to Kafka.

    Returns:
        bool: True if the service can connect to Kafka, False otherwise
    """
    if AIOKafkaConsumer is None or AIOKafkaProducer is None:
        return False

    async def _can_connect_to_kafka():
        try:
            async with get_kafka_conn():
                return True
        except Exception:
            return False

    return asyncio.run(_can_connect_to_kafka())
