"""Tests for the `api.serializers` module."""

import pytest
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker

from action_triggers.api.serializers import ConfigSerializer
from action_triggers.models import (
    Config,
    ConfigSignal,
    MessageBrokerQueue,
    Webhook,
    Action,
)
from tests.models import CustomerModel, CustomerOrderModel, M2MModel


@pytest.mark.django_db
class TestConfigSerializer:
    """Tests for the `ConfigSerializer` class."""

    def test_shows_data_correctly(self, full_loaded_config):
        config = full_loaded_config.config
        config_signal_1, config_signal_2 = full_loaded_config.config_signals
        webhook_1, webhook_2 = full_loaded_config.webhooks
        message_broker_queue_1, message_broker_queue_2 = (
            full_loaded_config.mesage_broker_queues
        )
        action_1, action_2 = full_loaded_config.actions

        serializer = ConfigSerializer(config)

        assert serializer.data == {
            "id": config.id,
            "active": config.active,
            "config_signals": [
                {"signal": config_signal_1.signal},
                {"signal": config_signal_2.signal},
            ],
            "content_types": [
                {
                    "app_label": CustomerModel._meta.app_label,
                    "model": CustomerModel._meta.model_name,
                },
                {
                    "app_label": CustomerOrderModel._meta.app_label,
                    "model": CustomerOrderModel._meta.model_name,
                },
            ],
            "webhooks": [
                {
                    "url": webhook_1.url,
                    "http_method": webhook_1.http_method,
                    "headers": webhook_1.headers,
                    "timeout_secs": webhook_1.timeout_secs,
                },
                {
                    "url": webhook_2.url,
                    "http_method": webhook_2.http_method,
                    "headers": webhook_2.headers,
                    "timeout_secs": webhook_2.timeout_secs,
                },
            ],
            "message_broker_queues": [
                {
                    "name": message_broker_queue_1.name,
                    "conn_details": message_broker_queue_1.conn_details,
                    "parameters": message_broker_queue_1.parameters,
                    "timeout_secs": message_broker_queue_1.timeout_secs,
                },
                {
                    "name": message_broker_queue_2.name,
                    "conn_details": message_broker_queue_2.conn_details,
                    "parameters": message_broker_queue_2.parameters,
                    "timeout_secs": message_broker_queue_2.timeout_secs,
                },
            ],
            "actions": [
                {
                    "name": action_1.name,
                    "conn_details": action_1.conn_details,
                    "parameters": action_1.parameters,
                    "timeout_secs": action_1.timeout_secs,
                },
                {
                    "name": action_2.name,
                    "conn_details": action_2.conn_details,
                    "parameters": action_2.parameters,
                    "timeout_secs": action_2.timeout_secs,
                },
            ],
            "payload": config.payload,
        }

    def test_shows_data_correctly_when_using_plaintext_payload(self, config):
        config.payload = "some plaintext payload"
        config.save()

        serializer = ConfigSerializer(config)

        assert serializer.data == {
            "id": config.id,
            "active": config.active,
            "config_signals": [],
            "content_types": [],
            "webhooks": [],
            "message_broker_queues": [],
            "actions": [],
            "payload": config.payload,
        }

    def test_create_method_creates_objects_correctly(self):
        data = {
            "config_signals": [
                {"signal": "pre_save"},
                {"signal": "post_save"},
            ],
            "content_types": [
                {
                    "app_label": CustomerModel._meta.app_label,
                    "model": CustomerModel._meta.model_name,
                },
                {
                    "app_label": CustomerOrderModel._meta.app_label,
                    "model": CustomerOrderModel._meta.model_name,
                },
            ],
            "webhooks": [
                {
                    "url": "http://test1.com",
                    "http_method": "POST",
                    "headers": {"Content-Type": "application/json"},
                    "timeout_secs": 10,
                },
                {
                    "url": "http://test2.com",
                    "http_method": "GET",
                    "headers": {"Content-Type": "application/json"},
                },
            ],
            "message_broker_queues": [
                {
                    "name": "test_queue_1",
                    "conn_details": {"host": "localhost", "port": 5672},
                    "parameters": {"queue": "test_queue_1"},
                    "timeout_secs": 20,
                },
                {
                    "name": "test_queue_2",
                    "conn_details": {"host": "localhost", "port": 5672},
                    "parameters": {"queue": "test_queue_2"},
                },
            ],
            "actions": [
                {
                    "name": "test_action_1",
                    "conn_details": {"host": "localhost", "port": 5672},
                    "parameters": {"queue": "test_queue_1"},
                    "timeout_secs": 30,
                },
                {
                    "name": "test_action_2",
                    "conn_details": {"host": "localhost", "port": 5672},
                    "parameters": {"queue": "test_queue_2"},
                },
            ],
            "payload": {"key": "value"},
        }

        serializer = ConfigSerializer()
        config = serializer.create(data)

        assert isinstance(config, Config)
        assert set(config.config_signals.values_list("signal", flat=True)) == {
            "pre_save",
            "post_save",
        }
        assert set(config.content_types.values_list("model", flat=True)) == {
            CustomerModel._meta.model_name,
            CustomerOrderModel._meta.model_name,
        }
        assert set(config.webhooks.values_list("url", flat=True)) == {
            "http://test1.com",
            "http://test2.com",
        }

        assert set(
            config.message_broker_queues.values_list("name", flat=True)
        ) == {
            "test_queue_1",
            "test_queue_2",
        }
        assert config.payload == {"key": "value"}

    def test_update_method_can_update_objects_correctly(self):
        config = baker.make(Config, payload={"key": "value"})

        config.content_types.set(
            [
                ContentType.objects.get_for_model(CustomerModel),
            ]
        )

        webhook_1, webhook_2 = baker.make(
            Webhook,
            config=config,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {{ path.to.token }}",
            },
            _quantity=2,
        )
        message_broker_queue_1, message_broker_queue_2 = baker.make(
            MessageBrokerQueue,
            config=config,
            conn_details={"host": "localhost", "port": 5672},
            parameters={"queue": "test_queue_1"},
            _quantity=2,
        )
        action_1, action_2 = baker.make(
            Action,
            config=config,
            conn_details={"host": "localhost", "port": 5672},
            parameters={"queue": "test_queue_1"},
            _quantity=2,
        )
        baker.make(
            ConfigSignal,
            config=config,
            signal="post_delete",
        )

        data = {
            "config_signals": [
                {"signal": "pre_save"},
                {"signal": "post_save"},
            ],
            "content_types": [
                {
                    "app_label": CustomerModel._meta.app_label,
                    "model": CustomerModel._meta.model_name,
                },
                {
                    "app_label": M2MModel._meta.app_label,
                    "model": M2MModel._meta.model_name,
                },
            ],
            "webhooks": [
                {
                    "url": "http://new-test-1.com",
                    "http_method": "POST",
                    "headers": {"Content-Type": "application/json"},
                },
                {
                    "url": "http://new-test-2.com",
                    "http_method": "GET",
                    "headers": {"Content-Type": "application/json"},
                },
            ],
            "message_broker_queues": [
                {
                    "name": "test_queue_1",
                    "conn_details": {"host": "localhost", "port": 5672},
                    "parameters": {"queue": "new_test_queue_1"},
                },
            ],
            "actions": [
                {
                    "name": "test_action_1",
                    "conn_details": {"host": "localhost", "port": 5672},
                    "parameters": {"queue": "new_test_queue_1"},
                }
            ],
            "payload": {"key": "new value"},
        }

        serializer = ConfigSerializer(config)
        res = serializer.update(config, data)

        assert res == config
        assert set(config.config_signals.values_list("signal", flat=True)) == {
            "pre_save",
            "post_save",
        }
        assert set(config.content_types.values_list("model", flat=True)) == {
            CustomerModel._meta.model_name,
            M2MModel._meta.model_name,
        }
        assert set(config.webhooks.values_list("url", flat=True)) == {
            "http://new-test-1.com",
            "http://new-test-2.com",
        }
        assert config.message_broker_queues.count() == 1
        assert config.message_broker_queues.first().name == "test_queue_1"
        assert config.message_broker_queues.first().parameters == {
            "queue": "new_test_queue_1"
        }

        assert config.actions.count() == 1
        assert config.actions.first().name == "test_action_1"
        assert config.actions.first().parameters == {
            "queue": "new_test_queue_1"
        }

        assert config.payload == {"key": "new value"}
