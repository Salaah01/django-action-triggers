from contextlib import contextmanager

import pika  # type: ignore[import-untyped]
from django.conf import settings
from kafka import KafkaConsumer  # type: ignore[import-untyped]


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
def get_kafka_consumer(key: str = "kafka_1") -> KafkaConsumer:
    """Consume a message from a Kafka broker.

    Args:
        key (str, optional): The key of the broker in the settings.
            Defaults to "kafka_1".

    Returns:
        KafkaConsumer: The Kafka consumer
    """

    conn = KafkaConsumer(
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        group_id="test_group_1",
        fetch_max_wait_ms=4000,
        **settings.ACTION_TRIGGERS["brokers"][key]["conn_details"],
    )
    conn.subscribe(
        settings.ACTION_TRIGGERS["brokers"][key]["params"]["topic"],  # type: ignore[index]  # noqa E501
    )

    yield conn

    conn.close()
