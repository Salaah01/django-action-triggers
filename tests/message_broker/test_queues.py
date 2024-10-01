"""Tests for the `message_brokers.queues` module."""

import asyncio
from asyncio.exceptions import TimeoutError
from unittest.mock import MagicMock, patch

import pytest
from model_bakery import baker

from action_triggers.dispatch import handle_action
from action_triggers.models import Config, MessageBrokerQueue
from tests.models import CustomerModel


@pytest.mark.django_db(transaction=True)
class TestProcessMsgBrokerQueues:
    """Tests for the `process_msg_broker_queue` function."""

    @patch("action_triggers.message_broker.queue.get_broker_class")
    def test_flow_calls_the_right_functions(self, mock_get_broker_class):
        config = baker.make(Config)
        mock_get_broker_class.return_value = MagicMock()
        baker.make(MessageBrokerQueue, config=config)
        customer = baker.make(CustomerModel)
        handle_action(config, customer)

        mock_get_broker_class.assert_called_once()
        mock_get_broker_class.return_value.assert_called_once()

    @patch("action_triggers.message_broker.base.BrokerBase.send_message")
    def test_kills_job_if_it_exceeds_timeout(
        self,
        mock_send_message,
        customer_rabbitmq_post_save_signal,
        caplog,
    ):
        async def side_effect(*args, **kwargs):
            await asyncio.sleep(3)
            return

        mock_send_message.side_effect = side_effect

        trigger = customer_rabbitmq_post_save_signal.trigger
        trigger.timeout_secs = 0.1
        trigger.save()

        baker.make(CustomerModel)

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert caplog.records[0].args[2] is TimeoutError
