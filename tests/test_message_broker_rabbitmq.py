"""Tests for RabbitMQ message broker."""

import action_triggers
import json
import socket

try:
    import pika  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    pika = None
import pytest
from django.conf import settings

from action_triggers.message_broker.exceptions import ConnectionValidationError
from action_triggers.message_broker.rabbitmq import (
    RabbitMQBroker,
    RabbitMQConnection,
)
from tests.utils import get_rabbitmq_conn
from tests.conftest import config


def conn_test() -> bool:
    """Verify that a connection can be made to RabbitMQ."""
    if pika is None:
        return False

    try:
        get_rabbitmq_conn()
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

    def test_raises_exception_if_queue_not_provided(self):
        with pytest.raises(ConnectionValidationError) as exc:
            RabbitMQConnection(
                config={},
                conn_details={},
                params={},
            )

        assert json.dumps(exc.value.as_dict()) == json.dumps(
            {
                "connection_params": {},
                "params": {"queue": ["Queue name must be provided."]},
            }
        )

    @pytest.mark.parametrize(
        "config,params",
        (
            ({"queue": "test"}, {}),
            ({}, {"queue": "test"}),
        ),
    )
    def test_valid_connection(self, config, params):
        conn = RabbitMQConnection(
            config=config,
            conn_details={},
            params=params,
        )
        assert conn


class TestRabbitMQBroker:
    """Tests for the `RabbitMQBroker` class."""

    @pytest.mark.skipif(not conn_test(), reason="RabbitMQ is not running.")
    def test_message_can_be_sent(self):
        """It should be able to send a message to RabbitMQ."""

        conn_param = pika.ConnectionParameters(
            **settings.ACTION_TRIGGERS["brokers"]["rabbitmq_1"]["conn_details"]
        )

        with pika.BlockingConnection(conn_param) as conn:
            broker = RabbitMQBroker(
                broker_key="rabbitmq_1",
                conn_params={},
                params={"queue": "test_queue_1"},
            )
            broker.send_message("new message")

        with pika.BlockingConnection(conn_param) as conn:
            channel = conn.channel()
            channel.queue_declare(queue="test_queue_1")
            method_frame, header_frame, body = channel.basic_get(
                queue="test_queue_1",
                auto_ack=True,
            )

            assert body == b"new message"
