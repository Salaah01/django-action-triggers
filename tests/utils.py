from contextlib import contextmanager

import pika  # type: ignore[import-untyped]
from django.conf import settings
from kafka import KafkaConsumer, KafkaProducer  # type: ignore[import-untyped]


def get_rabbitmq_conn(key: str = "rabbitmq_1") -> pika.BlockingConnection:
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
def get_kafka_conn(key: str = "kafka_1") -> KafkaConsumer:
    """Get a connection to a Kafka broker.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "kafka_1".

    Yields:
        KafkaConsumer: The connection to the broker
    """

    conn = KafkaConsumer(
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        group_id="test_group_1",
        fetch_max_wait_ms=4000,
        **settings.ACTION_TRIGGERS["brokers"][key]["conn_details"],
    )

    yield conn

    conn.close()


@contextmanager
def get_kafka_consumer(key: str = "kafka_1") -> KafkaConsumer:
    """Consume a message from a Kafka broker.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "kafka_1".

    Returns:
        KafkaConsumer: The Kafka consumer
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
        KafkaProducer: The Kafka producer
    """

    producer = KafkaProducer(
        **settings.ACTION_TRIGGERS["brokers"][key]["conn_details"],
    )

    yield producer

    producer.close()


def can_connect_to_rabbitmq() -> bool:
    """Check if the service can connect to RabbitMQ.

    Returns:
        bool: True if the service can connect to RabbitMQ, False otherwise
    """

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

    try:
        with get_kafka_conn():
            return True
    except Exception:
        return False
