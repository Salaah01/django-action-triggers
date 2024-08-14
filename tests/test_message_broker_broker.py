import pytest

from action_triggers.message_broker.broker import get_broker_class
from action_triggers.message_broker.rabbitmq import RabbitMQBroker
from action_triggers.message_broker.kafka import KafkaBroker


class TestGetBrokerClass:
    @pytest.mark.parametrize(
        "broker_name, expected",
        (
            ("rabbitmq_1", RabbitMQBroker),
            ("rabbitmq_2", RabbitMQBroker),
            ("kafka_1", KafkaBroker),
            ("kafka_2", KafkaBroker),
        ),
    )
    def test_correct_class_returned(self, broker_name, expected):
        assert get_broker_class(broker_name) == expected
