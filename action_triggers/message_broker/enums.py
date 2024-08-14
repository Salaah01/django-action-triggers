from enum import Enum


class BrokerType(Enum):
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"
    SQS = "sqs"
