"""Tests for the `signals` module."""

import logging

import pytest
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker

from action_triggers.enums import SignalChoices
from action_triggers.models import Config, ConfigSignal
from action_triggers.registry import add_to_registry
from tests.models import CustomerModel, CustomerOrderModel


class TestSignal:
    """Tests that the signals are connected to the callback function."""

    def test_signal_callback_prints_message(self, caplog):
        caplog.set_level(logging.DEBUG)
        add_to_registry(CustomerModel)
        add_to_registry(CustomerOrderModel)
        config = baker.make(Config)
        config.content_types.add(
            ContentType.objects.get_for_model(CustomerModel)
        )
        baker.make(ConfigSignal, config=config, signal=SignalChoices.POST_SAVE)
        CustomerModel.create_record()

        assert "Signal triggered for config:" in caplog.text

    def test_action_does_not_run_for_inactive_message(self, caplog):
        caplog.set_level(logging.DEBUG)
        add_to_registry(CustomerModel)
        add_to_registry(CustomerOrderModel)
        config = baker.make(Config, active=False)
        config.content_types.add(
            ContentType.objects.get_for_model(CustomerModel)
        )
        baker.make(ConfigSignal, config=config, signal=SignalChoices.POST_SAVE)
        CustomerModel.create_record()

        assert "Signal triggered for config:" not in caplog.text

    def test_does_not_trigger_action_for_unregistered_model(self, caplog):
        caplog.set_level(logging.DEBUG)
        config = baker.make(Config)
        config.content_types.add(
            ContentType.objects.get_for_model(CustomerOrderModel)
        )
        baker.make(ConfigSignal, config=config, signal=SignalChoices.POST_SAVE)
        CustomerModel.create_record()

        assert "Signal triggered for config:" not in caplog.text

    @pytest.mark.parametrize(
        "signal_choice",
        (
            SignalChoices.POST_DELETE,
            SignalChoices.PRE_DELETE,
        ),
    )
    def test_action_not_triggered_for_unassociated_signals(
        self,
        signal_choice,
        caplog,
    ):
        caplog.set_level(logging.DEBUG)
        add_to_registry(CustomerModel)
        config = baker.make(Config)
        config.content_types.add(
            ContentType.objects.get_for_model(CustomerModel)
        )
        baker.make(ConfigSignal, config=config, signal=signal_choice)
        CustomerModel.create_record()

        assert "Signal triggered for config:" not in caplog.text
