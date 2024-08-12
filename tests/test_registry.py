"""Tests for the registry module."""

import pytest
from model_bakery import baker

from action_triggers import registry
from action_triggers.models import Config
from action_triggers.registry import (
    add_to_registry,
    model_in_registry,
    model_str,
    registered_content_types,
)


class TestRegistry:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Resets the registry to an empty state before each test."""
        registry.registered_models = {}

    def test_model_str_returns_correct_string(self):
        assert model_str(Config) == "action_triggers.config"

    def test_add_to_registry_adds_model_class_to_registry(self):
        add_to_registry(Config)
        assert registry.registered_models == {"action_triggers.config": Config}

    def test_add_to_registry_on_model_instance_adds_model_class_to_registry(
        self,
    ):
        config = baker.make(Config)
        add_to_registry(config)
        assert registry.registered_models == {"action_triggers.config": Config}

    def test_model_in_registry_returns_true_if_model_in_registry(self):
        assert model_in_registry(Config) is False
        add_to_registry(Config)
        assert model_in_registry(Config) is True

    def test_registered_content_types_returns_qs_of_registered_content_types(
        self,
    ):
        add_to_registry(Config)
        assert registered_content_types().count() == 1
        assert registered_content_types().first().model == "config"
        assert (
            registered_content_types().first().app_label == "action_triggers"
        )
