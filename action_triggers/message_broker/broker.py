import typing as _t

from django.conf import settings

from action_triggers.message_broker.base import BrokerBase
from action_triggers.message_broker.enums import BrokerType
from action_triggers.message_broker.kafka import KafkaBroker
from action_triggers.message_broker.rabbitmq import RabbitMQBroker


def get_broker_class(broker_name: str) -> _t.Type[BrokerBase]:
    """Get the broker class based on the broker name.

    :param broker_name: The name of the broker.
    :return: The broker class.
    :raises ValueError: If the broker name is invalid.
    """

    broker_type_to_class_map = {
        BrokerType.RABBITMQ.name: RabbitMQBroker,
        BrokerType.KAFKA.name: KafkaBroker,
    }

    return broker_type_to_class_map[
        _t.cast(
            str,
            settings.ACTION_TRIGGERS["brokers"][broker_name]["broker_type"],  # type: ignore[index]  # noqa E501
        ).upper()
    ]
