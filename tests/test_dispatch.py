"""Tests for the `dispatch` module."""

import asyncio
from asyncio.exceptions import TimeoutError
from unittest.mock import AsyncMock, patch

import pytest
from aioresponses import aioresponses
from model_bakery import baker

from action_triggers.dispatch import handle_action
from action_triggers.models import Config, MessageBrokerQueue, Webhook
from tests.models import (
    CustomerModel,
    CustomerOrderModel,
    M2MModel,
    One2OneModel,
)


@pytest.mark.django_db
class TestHandleAction:
    """Tests for the `handle_action` function."""

    @patch("action_triggers.dispatch.process_webhook", new_callable=AsyncMock)
    @patch(
        "action_triggers.dispatch.process_msg_broker_queue",
        new_callable=AsyncMock,
    )
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
        with aioresponses() as mocked:
            mocked.post("http://example.com", status=200)

            config = baker.make(Config, payload=config_payload)
            webhooks = baker.make(
                Webhook,
                http_method="POST",
                url="http://example.com",
                config=config,
                _quantity=2,
            )
            baker.make(Webhook)

            model_instance = baker.make(model_class)
            handle_action(config, model_instance)

            assert mock_process_webhook.call_count == 2
            assert mock_process_webhook.call_args_list[0][0][1] in webhooks
            assert mock_process_webhook.call_args_list[1][0][1] in webhooks
            assert mock_process_msg_broker_queue.call_count == 0

    @patch("action_triggers.dispatch.WebhookProcessor")
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

    def test_skips_over_webhooks_with_errors(
        self,
        customer_webhook_post_save_signal,
        caplog,
    ):
        config = customer_webhook_post_save_signal.config
        webhook = baker.make(Webhook, config=config, url="https://bad-url.com")
        baker.make(CustomerModel)

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert (
            f"Error processing webhook {webhook.id} for config {config.id}"
            in caplog.records[0].message
        )

    def test_skips_over_msg_broker_queues_with_errors(
        self,
        customer_webhook_post_save_signal,
        caplog,
    ):
        config = customer_webhook_post_save_signal.config
        msg_broker_queue = baker.make(
            MessageBrokerQueue, config=config, conn_details={"host": "bad"}
        )
        baker.make(CustomerModel)

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert (
            f"Error processing message broker queue {msg_broker_queue.id} "
            f"for config {config.id}" in caplog.records[0].message
        )

    @patch("action_triggers.webhooks.WebhookProcessor.process")
    def test_kills_job_if_it_exceeds_timeout_webhook_action(
        self,
        mock_process,
        customer_webhook_post_save_signal,
        caplog,
    ):
        async def side_effect(*args, **kwargs):
            await asyncio.sleep(3)
            return

        mock_process.side_effect = side_effect

        webhook = customer_webhook_post_save_signal.trigger
        webhook.timeout_secs = 0.1
        webhook.save()

        baker.make(CustomerModel)

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert isinstance(caplog.records[0].args[2], TimeoutError)
