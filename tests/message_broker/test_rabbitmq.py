"""Tests for RabbitMQ message broker."""

import asyncio
import json

try:
    import aio_pika  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    aio_pika = None  # type: ignore[assignment]
import pytest
from django.conf import settings

from action_triggers.message_broker.exceptions import ConnectionValidationError
from action_triggers.message_broker.rabbitmq import (
    RabbitMQBroker,
    RabbitMQConnection,
)
from tests.utils.rabbitmq import can_connect_to_rabbitmq, get_rabbitmq_conn


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

    @pytest.mark.skipif(
        not can_connect_to_rabbitmq(), reason="RabbitMQ is not running."
    )
    @pytest.mark.asyncio
    async def test_connection_and_close_mechanism(self):
        conn = RabbitMQConnection(
            config={"queue": "test_queue_1"},
            conn_details=settings.ACTION_TRIGGERS["brokers"]["rabbitmq_1"][
                "conn_details"
            ],
            params={},
        )
        await conn.connect()
        assert conn.conn is not None
        await conn.close()
        assert conn.conn is None


class TestRabbitMQBroker:
    """Tests for the `RabbitMQBroker` class."""

    @pytest.fixture(autouse=True)
    def purge_all_messages(self):
        async def purge_messages():
            async with get_rabbitmq_conn() as conn:
                channel = await conn.channel()
                await channel.set_qos(prefetch_count=1)
                queue = await channel.declare_queue("test_queue_1")
                await queue.purge()

        asyncio.run(purge_messages())

    @pytest.mark.skipif(
        not can_connect_to_rabbitmq(), reason="RabbitMQ is not running."
    )
    @pytest.mark.asyncio
    async def test_message_can_be_sent(self):
        """It should be able to send a message to RabbitMQ."""

        async with get_rabbitmq_conn() as connection:
            broker = RabbitMQBroker(
                broker_key="rabbitmq_1",
                conn_params={},
                params={"queue": "test_queue_1"},
            )
            await broker.send_message("new message")

            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=1)
                queue = await channel.declare_queue("test_queue_1")
                message = await queue.get()
                assert message.body == b"new message"
