"""Tests for RabbitMQ message broker."""

import socket
import json
import pytest
from action_triggers.message_broker.rabbitmq import (
    RabbitMQBroker,
    RabbitMQConnection,
)
import pika
from action_triggers.message_broker.exceptions import ConnectionValidationError
from django.conf import settings


def get_conn() -> pika.BlockingConnection:
    """Get a connection to RabbitMQ."""
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            **settings.ACTION_TRIGGERS["brokers"]["rabbitmq_1"]["conn_details"]
        )
    )


def conn_test() -> bool:
    """Verify that a connection can be made to RabbitMQ."""
    try:
        get_conn()
        return True
    except socket.gaierror as e:
        if str(e) in {
            "[Errno -2] Name or service not known",
            "[Errno -3] Temporary failure in name resolution",
        }:
            return False
        raise
    except pika.exceptions.ProbableAuthenticationError:
        return False


class TestRabbitMQConnection:
    """Tests for the `RabbitMQConnection` class."""

    def test_requires_queue(self):
        """It should require a queue name."""
        with pytest.raises(ConnectionValidationError) as exc:
            RabbitMQConnection(
                conn_details={},
                params={},
            )

        assert str(exc.value) == json.dumps(
            {
                "connection_params": {
                    "queue": ["Queue name must be provided."]
                },
                "params": {},
            }
        )

    def test_valid_connection(self):
        """It should not raise an exception when the connection is valid."""
        conn = RabbitMQConnection(
            conn_details={},
            params={"queue": "test"},
        )
        assert conn


class TestRabbitMQBroker:
    """Tests for the `RabbitMQBroker` class."""

    @pytest.mark.skipif(not conn_test(), reason="RabbitMQ is not running.")
    def test_message_can_be_sent(self):
        """It should be able to send a message to RabbitMQ."""
        conn = pika.BlockingConnection(
            pika.ConnectionParameters(
                **settings.ACTION_TRIGGERS["brokers"]["rabbitmq_1"][
                    "conn_details"
                ]
            )
        )
        channel = conn.channel()
        channel.queue_declare(queue="test_queue_1")

        broker = RabbitMQBroker(
            broker_key="rabbitmq_1",
            conn_params={},
            params={"queue": "test_queue_1"},
        )
        broker.send_message("test message")

        method_frame, header_frame, body = channel.basic_get(
            queue="test_queue_1"
        )
        assert body == b"test message"
        conn.close()
