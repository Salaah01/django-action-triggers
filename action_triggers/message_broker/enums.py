"""Enums specific to Action Trigger message brokers."""


from enum import Enum


class BrokerType(Enum):
    """Represents the types of brokers supported by the application."""

    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"
    REDIS = "redis"
    AWS_SQS = "aws_sqs"
    AWS_SNS = "aws_sns"
    GCP_PUBSUB = "gcp_pubsub"
