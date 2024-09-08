"""Tests for the Reid message broker."""

import pytest
from django.conf import settings

from action_triggers.message_broker.exceptions import ConnectionValidationError
from action_triggers.message_broker.redis import RedisBroker, RedisConnection
from tests.utils.redis import can_connect_to_redis


class TestRedisConnection:
    """Tests for the `RedisConnection` class."""

    def test_raises_exception_if_no_channel_found(self):
        with pytest.raises(ConnectionValidationError):
            RedisConnection(
                config={},
                conn_details={},
                params={},
            )

    @pytest.mark.parametrize(
        "config,params",
        (
            ({"params": {"channel": "test_channel_1"}}, {}),
            ({}, {"channel": "test_channel_1"}),
        ),
    )
    def test_passes_when_channel_exists(self, config, params):
        RedisConnection(
            config=config,
            conn_details={
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
            },
            params=params,
        )

    def test_raises_exception_if_url_nor_host_defined(self):
        with pytest.raises(ConnectionValidationError):
            RedisConnection(
                config={},
                conn_details={},
                params={"channel": "test_channel_1"},
            )

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not can_connect_to_redis(),
        reason="Redis is not running.",
    )
    @pytest.mark.parametrize("key", ("redis_with_host", "redis_with_url"))
    async def test_connection_and_close_mechanism(self, key):
        conn = RedisConnection(
            config=settings.ACTION_TRIGGERS["brokers"][key],
            conn_details={},
            params={},
        )
        await conn.connect()
        assert conn.conn is not None
        await conn.close()
        assert conn.conn is None


@pytest.mark.skipif(
    not can_connect_to_redis(),
    reason="Cannot connect to Redis.",
)
class TestRedisBroker:
    """Tests for the `RedisBroker` class."""

    @pytest.mark.asyncio
    async def test_message_can_be_sent(self):
        broker = RedisBroker(
            "redis_with_host",
            conn_details={},
            params={},
        )
        await broker.send_message("test_message")
