"""Tests for the `exceptions` module."""

import json
from collections import defaultdict

import pytest

from action_triggers.exceptions import (
    ConnectionValidationError,
    DisallowedWebhookEndpointError,
)


class TestDisallowedWebhookEndpointError:
    def test_error_message(self):
        error = DisallowedWebhookEndpointError("http://example.com")
        assert (
            str(error)
            == "Webhook endpoint 'http://example.com' is not whitelisted."
        )


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
