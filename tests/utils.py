from contextlib import contextmanager

try:
    import pika  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    pika = None
try:
    from confluent_kafka import (  # type: ignore[import-untyped]
        Consumer,
        Producer,
    )
except ImportError:  # pragma: no cover
    Consumer = Producer = None
from django.conf import settings


def get_rabbitmq_conn(key: str = "rabbitmq_1"):
    """Get a connection to a RabbitMQ broker.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "rabbitmq_1".

    Returns:
        pika.BlockingConnection: The connection to the broker
    """

    return pika.BlockingConnection(
        pika.ConnectionParameters(
            **settings.ACTION_TRIGGERS["brokers"][key]["conn_details"]
        )
    )


@contextmanager
def get_kafka_conn(key: str = "kafka_1"):
    """Get a connection to a Kafka broker.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "kafka_1".

    Yields:
        Consumer: The connection to the broker
    """

    conn = Consumer(
        {
            "enable.auto.commit": False,
            "auto.offset.reset": "earliest",
            "group.id": "test_group_1",
            **settings.ACTION_TRIGGERS["brokers"][key]["conn_details"],  # type: ignore[dict-item]  # noqa E501
        }
    )

    yield conn

    conn.close()


@contextmanager
def get_kafka_consumer(key: str = "kafka_1"):
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


@contextmanager
def get_kafka_producer(key: str = "kafka_1"):
    """Get a Kafka producer.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "kafka_1".

    Yields:
        Producer: The Kafka producer
    """

    producer = Producer(
        **settings.ACTION_TRIGGERS["brokers"][key]["conn_details"],
    )

    yield producer

    producer.close()


def can_connect_to_rabbitmq() -> bool:
    """Check if the service can connect to RabbitMQ.

    Returns:
        bool: True if the service can connect to RabbitMQ, False otherwise
    """

    if pika is None:
        return False

    try:
        with get_rabbitmq_conn():
            return True
    except pika.exceptions.ProbableAuthenticationError:
        return False


def can_connect_to_kafka() -> bool:
    """Check if the service can connect to Kafka.

    Returns:
        bool: True if the service can connect to Kafka, False otherwise
    """

    if Consumer is None or Producer is None:
        return False

    try:
        with get_kafka_conn():
            return True
    except Exception:
        return False
