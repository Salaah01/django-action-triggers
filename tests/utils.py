import pika  # type: ignore[import-untyped]
from django.conf import settings
from kafka import KafkaConsumer
from contextlib import contextmanager


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
        # heartbeat_interval_ms=2000,
        # session_timeout_ms=3000,
        fetch_max_wait_ms=4000,
        # request_timeout_ms=5500,
        # connections_max_idle_ms=6000,
        **settings.ACTION_TRIGGERS["brokers"][key]["conn_details"],
    )
    conn.subscribe(
        settings.ACTION_TRIGGERS["brokers"][key]["params"]["topic"],
    )

    yield conn

    conn.close()
