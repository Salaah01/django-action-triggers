"""Tests for the `api.views` module."""

from django.test import Client
from django.urls import reverse

from tests.models import CustomerModel, CustomerOrderModel


class TestConfigViewSet:
    """Tests for the `ConfigViewSet` class."""

    def test_list_returns_configs(self, full_loaded_config):
        client = Client()
        response = client.get(reverse("action_triggers:config-list"))

        config = full_loaded_config.config
        config_signal_1, config_signal_2 = full_loaded_config.config_signals
        webhook_1, webhook_2 = full_loaded_config.webhooks
        message_broker_queue_1, message_broker_queue_2 = (
            full_loaded_config.mesage_broker_queues
        )

        assert response.status_code == 200

        res = response.json()

        assert len(res) == 1
        assert res[0]["id"] == config.id
        assert res[0]["config_signals"] == [
            {"signal": config_signal_1.signal},
            {"signal": config_signal_2.signal},
        ]
        assert res[0]["content_types"] == [
            {
                "app_label": CustomerModel._meta.app_label,
                "model": CustomerModel._meta.model_name,
            },
            {
                "app_label": CustomerOrderModel._meta.app_label,
                "model": CustomerOrderModel._meta.model_name,
            },
        ]
        assert res[0]["webhooks"] == [
            {
                "url": webhook_1.url,
                "http_method": webhook_1.http_method,
                "headers": webhook_1.headers,
            },
            {
                "url": webhook_2.url,
                "http_method": webhook_2.http_method,
                "headers": webhook_2.headers,
            },
        ]
        assert res[0]["message_broker_queues"] == [
            {
                "name": message_broker_queue_1.name,
                "conn_details": message_broker_queue_1.conn_details,
                "parameters": message_broker_queue_1.parameters,
            },
            {
                "name": message_broker_queue_2.name,
                "conn_details": message_broker_queue_2.conn_details,
                "parameters": message_broker_queue_2.parameters,
            },
        ]
        assert res[0]["payload"] == config.payload
