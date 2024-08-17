"""Tests for the `message_broker.exceptions` module."""

import json
import pytest

from action_triggers.message_broker.exceptions import (
    ConnectionValidationError,
    MissingDependenciesError,
)
from collections import defaultdict


class TestMissingDependenciesError:
    """Tests for the `MissingDependenciesError` class."""

    def test_shows_custom_message(self):
        exc = MissingDependenciesError(
            broker_name="broker-name",
            extra_name="extra-name",
            package_name="package-name",
        )
        exc_str = str(exc)

        assert "The `extra-name` extra must be installed" in exc_str
        assert "to use the broker-name broker" in exc_str
        assert "action-triggers[extra-name]" in exc_str
        assert "pip install package-name" in exc_str


class TestConnectionValidationError:
    """Tests for the `ConnectionValidationError` class."""

    @pytest.fixture
    def err_with_msg(self):
        err = defaultdict(list)
        err["a"].append(1)
        err["a"].append("z")
        err["b"].append(2)
        return ConnectionValidationError(err)

    def test_as_dict_converts_message_to_dict(self, err_with_msg):
        assert err_with_msg.as_dict() == {
            "a": [1, "z"],
            "b": [2],
        }

    def test_as_json_converts_message_to_json(self, err_with_msg):
        assert err_with_msg.as_json() == json.dumps(
            {
                "a": [1, "z"],
                "b": [2],
            }
        )
