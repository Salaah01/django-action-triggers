import typing as _t

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework import serializers  # type: ignore[import-untyped]

from action_triggers.models import (
    Config,
    ConfigSignal,
    MessageBrokerQueue,
    Webhook,
)


class ConfigSignalSerializer(serializers.ModelSerializer):
    """Serializer for the `ConfigSignal` model."""

    class Meta:
        model = ConfigSignal
        fields = ("signal",)


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer for the `Webhook` model."""

    class Meta:
        model = Webhook
        fields = ["url", "http_method", "headers"]


class ContentTypeSerializer(serializers.ModelSerializer):
    """Serializer for the `ContentType` model."""

    class Meta:
        model = ContentType
        fields = ["app_label", "model"]


class MessageBrokerQueueSerializer(serializers.ModelSerializer):
    """Serializer for the `MessageBrokerQueue` model."""

    class Meta:
        model = MessageBrokerQueue
        fields = ("name", "conn_details", "parameters")


class ConfigSerializer(serializers.ModelSerializer):
    """Serializer for the `Config` model."""

    config_signals = ConfigSignalSerializer(many=True)
    message_broker_queues = MessageBrokerQueueSerializer(many=True)
    webhooks = WebhookSerializer(many=True)
    content_types = ContentTypeSerializer(many=True)

    class Meta:
        model = Config
        fields = (
            "id",
            "active",
            "payload",
            "config_signals",
            "content_types",
            "webhooks",
            "message_broker_queues",
        )

    @staticmethod
    def get_content_types_from_data(
        data: _t.List[dict],
    ) -> _t.List[ContentType]:
        """Get content types from the data

        :param data: List of content types data where the app_label and model
            are provided.
        :return: List of content types.
        """

        return [
            ContentType.objects.get(
                app_label=content_type["app_label"],
                model=content_type["model"],
            )
            for content_type in data
        ]

    @transaction.atomic
    def create(self, validate_data: dict) -> Config:
        """Create a new `Config` instance and related objects.

        :param validate_data: The validated data.
        :return: The created `Config` instance.
        """

        config_signals = validate_data.pop("config_signals")
        message_broker_queues = validate_data.pop("message_broker_queues")
        webhooks = validate_data.pop("webhooks")
        content_types = self.get_content_types_from_data(
            validate_data.pop("content_types")
        )

        config = Config.objects.create(**validate_data)
        config.content_types.set(content_types)

        for signal in config_signals:
            ConfigSignal.objects.create(config=config, **signal)

        for webhook in webhooks:
            Webhook.objects.create(config=config, **webhook)

        for queue in message_broker_queues:
            MessageBrokerQueue.objects.create(config=config, **queue)

        return config

    @transaction.atomic
    def update(self, instance: Config, validate_data: dict) -> Config:
        """Update the `Config` instance updating any related objects.

        :param instance: The `Config` instance to update.
        :param validate_data: The validated data.
        :return: The updated `Config` instance.
        """

        config_signals = validate_data.pop("config_signals")
        message_broker_queues = validate_data.pop("message_broker_queues")
        webhooks = validate_data.pop("webhooks")
        content_types = self.get_content_types_from_data(
            validate_data.pop("content_types")
        )

        instance = super().update(instance, validate_data)

        instance.config_signals.all().delete()
        instance.message_broker_queues.all().delete()
        instance.webhooks.all().delete()
        instance.content_types.set(content_types)

        for signal in config_signals:
            ConfigSignal.objects.create(config=instance, **signal)

        for webhook in webhooks:
            Webhook.objects.create(config=instance, **webhook)

        for queue in message_broker_queues:
            MessageBrokerQueue.objects.create(config=instance, **queue)

        return instance
