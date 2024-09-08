"""Tests for the Kafka message broker."""

import pytest
from django.conf import settings
from django.test import override_settings

from action_triggers.message_broker.exceptions import ConnectionValidationError
from action_triggers.message_broker.kafka import KafkaBroker, KafkaConnection
from tests.utils.kafka import can_connect_to_kafka


class TestKafkaConnection:
    """Tests for the `KafkaConnection` class."""

    def test_raises_exception_if_no_topic_found(self):
        with pytest.raises(ConnectionValidationError):
            KafkaConnection(
                config={},
                conn_details={},
                params={},
            )

    @pytest.mark.parametrize(
        "config,params",
        (
            ({"params": {"topic": "test_topic_1"}}, {}),
            ({}, {"topic": "test_topic_1"}),
        ),
    )
    def test_passes_when_topic_exists(self, config, params):
        KafkaConnection(
            config=config,
            conn_details={},
            params=params,
        )

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not can_connect_to_kafka(),
        reason="Kafka is not running.",
    )
    async def test_connection_and_close_mechanism(self):
        conn = KafkaConnection(
            config={"params": {"topic": "test_topic_1"}},
            conn_details=settings.KAFKA_CONN_DETAILS,
            params={},
        )
        await conn.connect()
        assert conn.conn is not None
        await conn.close()
        assert conn.conn is None


class TestKafkaBroker:
    """Tests for the `KafkaBroker` class."""

    @override_settings(
        ACTION_TRIGGERS={
            "brokers": {
                "kafka_1": {
                    "conn_details": {
                        "bootstrap_servers": "localhost:9092",
                    },
                    "params": {},
                },
            },
        },
    )
    def test_requires_topic(self):
        with pytest.raises(ConnectionValidationError):
            KafkaBroker(
                broker_key="kafka_1",
                conn_params={},
                params={},
            )

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not can_connect_to_kafka(),
        reason="Kafka is not running.",
    )
    async def test_message_can_be_sent(self):
        """It should be able to send a message to Kafka."""
        broker = KafkaBroker(
            broker_key="kafka_1",
            conn_params={},
            params={"topic": "test_topic_1"},
        )
        await broker.send_message("test message")
        assert True
