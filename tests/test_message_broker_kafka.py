"""Tests for the Kafka message broker."""

import pytest
from django.test import override_settings

from action_triggers.message_broker.exceptions import ConnectionValidationError
from action_triggers.message_broker.kafka import KafkaBroker, KafkaConnection
from tests.utils import can_connect_to_kafka


class TestKafkaConnection:
    """Tests for the `KafkaConnection` class."""

    def test_requires_topic(self):
        with pytest.raises(ConnectionValidationError):
            KafkaConnection(
                conn_details={},
                params={},
            )


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

    @pytest.mark.skipif(
        not can_connect_to_kafka(),
        reason="Kafka is not running.",
    )
    def test_message_can_be_sent(self):
        """It should be able to send a message to Kafka."""
        broker = KafkaBroker(
            broker_key="kafka_1",
            conn_params={},
            params={"topic": "test_topic_1"},
        )
        broker.send_message("test message")
        assert True
