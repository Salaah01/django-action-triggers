"""Tests for the `models` module."""

from model_bakery import baker

from action_triggers.models import (Config, ConfigSignal, MessageBrokerQueue,
                                    Webhook)


class TestConfig:
    """Tests for the `Config` model."""

    def test_str_returns_a_string_representation_of_the_instance(self):
        assert isinstance(str(baker.make(Config)), str)


class TestWebhook:
    """Tests for the `Webhook` model."""

    def test_str_returns_a_string_representation_of_the_instance(self):
        assert isinstance(str(baker.make(Webhook)), str)


class TestMessageBrokerQueue:
    """Tests for the `MessageBrokerQueue` model."""

    def test_str_returns_a_string_representation_of_the_instance(self):
        assert isinstance(str(baker.make(MessageBrokerQueue)), str)


class TestConfigSignal:
    """Tests for the `ConfigSignal` model."""

    def test_str_returns_a_string_representation_of_the_instance(self):
        assert isinstance(str(baker.make(ConfigSignal)), str)

    def test_repr_returns_a_string_representation_of_the_instance(self):
        assert isinstance(repr(baker.make(ConfigSignal)), str)
