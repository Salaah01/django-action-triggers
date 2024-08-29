"""Tests for the `exceptions` module."""

from action_triggers.exceptions import DisallowedWebhookEndpointError


class TestDisallowedWebhookEndpointError:
    def test_error_message(self):
        error = DisallowedWebhookEndpointError("http://example.com")
        assert (
            str(error)
            == "Webhook endpoint 'http://example.com' is not whitelisted."
        )
