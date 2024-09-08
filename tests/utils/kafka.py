import asyncio
from contextlib import asynccontextmanager

try:
    from aiokafka import (  # type: ignore[import]  # noqa E501
        AIOKafkaConsumer,
        AIOKafkaProducer,
    )
except ImportError:  # pragma: no cover
    AIOKafkaConsumer = AIOKafkaProducer = None
from django.conf import settings


@asynccontextmanager
async def get_kafka_consumer(key: str = "kafka_1"):
    """Consume a message from a Kafka broker.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "kafka_1".

    Returns:
        Consumer: The Kafka consumer
    """

    consumer = AIOKafkaConsumer(
        settings.ACTION_TRIGGERS["brokers"][key]["params"]["topic"],  # type: ignore[index]  # noqa E501
        enable_auto_commit=True,
        **settings.ACTION_TRIGGERS["brokers"][key]["conn_details"],  # type: ignore[index]  # noqa E501
    )
    await consumer.start()
    yield consumer
    await consumer.stop()


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


def can_connect_to_kafka() -> bool:
    """Check if the service can connect to Kafka.

    Returns:
        bool: True if the service can connect to Kafka, False otherwise
    """
    if AIOKafkaConsumer is None or AIOKafkaProducer is None:
        return False

    async def _can_connect_to_kafka():
        try:
            async with get_kafka_consumer():
                return True
        except Exception as e:
            raise e
            return False

    return asyncio.run(_can_connect_to_kafka())
