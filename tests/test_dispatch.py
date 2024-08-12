"""Tests for the `dispatch` module."""

from unittest.mock import patch

import pytest
from model_bakery import baker

from action_triggers.dispatch import handle_action
from action_triggers.models import Config, MessageBrokerQueue, Webhook
from tests.models import (
    CustomerModel,
    CustomerOrderModel,
    M2MModel,
    One2OneModel,
)


class TestHandleAction:
    """Tests for the `handle_action` function."""

    @patch("action_triggers.dispatch.process_webhook")
    @patch("action_triggers.dispatch.process_msg_broker_queue")
    @pytest.mark.parametrize(
        "model_class",
        (CustomerModel, CustomerOrderModel, M2MModel, One2OneModel),
    )
    @pytest.mark.parametrize("config_payload", (None, {"foo": "bar"}))
    def test_for_all_webhooks_webhook_handler_called(
        self,
        mock_process_msg_broker_queue,
        mock_process_webhook,
        model_class,
        config_payload,
    ):
        config = baker.make(Config, payload=config_payload)
        webhooks = baker.make(Webhook, config=config, _quantity=2)
        baker.make(Webhook)

        model_instance = baker.make(model_class)
        handle_action(config, model_instance)

        assert mock_process_webhook.call_count == 2
        assert mock_process_webhook.call_args_list[0][0][0] in webhooks
        assert mock_process_webhook.call_args_list[1][0][0] in webhooks
        assert mock_process_msg_broker_queue.call_count == 0

    @patch("action_triggers.dispatch.process_webhook")
    @patch("action_triggers.dispatch.process_msg_broker_queue")
    @pytest.mark.parametrize(
        "model_class",
        (CustomerModel, CustomerOrderModel, M2MModel, One2OneModel),
    )
    @pytest.mark.parametrize("config_payload", (None, {"foo": "bar"}))
    def test_for_all_msg_broker_queues_msg_broker_queue_handler_called(
        self,
        mock_process_msg_broker_queue,
        mock_process_webhook,
        model_class,
        config_payload,
    ):
        config = baker.make(Config, payload=config_payload)
        msg_broker_queues = baker.make(
            MessageBrokerQueue, config=config, _quantity=2
        )
        baker.make(MessageBrokerQueue)

        model_instance = baker.make(model_class)
        handle_action(config, model_instance)

        assert mock_process_msg_broker_queue.call_count == 2
        assert (
            mock_process_msg_broker_queue.call_args_list[0][0][0]
            in msg_broker_queues
        )
        assert (
            mock_process_msg_broker_queue.call_args_list[1][0][0]
            in msg_broker_queues
        )
        assert mock_process_webhook.call_count == 0
