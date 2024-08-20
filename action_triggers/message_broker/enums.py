from enum import Enum


class BrokerType(Enum):
    """Represents the types of brokers supported by the application."""

    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"
