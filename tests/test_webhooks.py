"""Tests for the `webhooks` module."""

from unittest.mock import patch

import pytest
import requests
import responses
from model_bakery import baker

from action_triggers.exceptions import DisallowedWebhookEndpointError
from action_triggers.models import Webhook
from action_triggers.webhooks import WebhookProcessor


class TestWebhookProcessor:
    """Tests for the `WebhookProcessor` class."""

    @pytest.mark.parametrize(
        "http_method,expected",
        (
            ("GET", requests.get),
            ("POST", requests.post),
            ("PUT", requests.put),
            ("PATCH", requests.patch),
            ("DELETE", requests.delete),
        ),
    )
    def test_get_request_fn_returns_correct_function(
        self,
        http_method,
        expected,
    ):
        webhook = baker.make(Webhook, http_method=http_method)
        processor = WebhookProcessor(webhook, {})
        assert processor.get_request_fn() is expected

    def test_get_fn_kwargs_returns_correct_data_for_json_req(self, webhook):
        processor = WebhookProcessor(webhook, {"foo": "bar"})
        assert processor.get_fn_kwargs() == {
            "url": webhook.url,
            "json": {"foo": "bar"},
        }

    def test_get_fn_kwargs_returns_correct_data_for_data_req(self, webhook):
        processor = WebhookProcessor(webhook, "foo=bar")
        assert processor.get_fn_kwargs() == {
            "url": webhook.url,
            "data": "foo=bar",
        }

    def test_get_fn_kwargs_replaces_headers_with_results(self, webhook):
        webhook.headers = {
            "content-type": "application/json",
            "Authorization": "Bearer {{ tests.test_dynamic_loading.get_api_token }}",  # noqa: E501
        }
        webhook.save()
        processor = WebhookProcessor(webhook, {})

        assert processor.get_fn_kwargs() == {
            "url": webhook.url,
            "json": {},
            "headers": {
                "content-type": "application/json",
                "Authorization": "Bearer test_token",
            },
        }

    @pytest.mark.parametrize(
        "payload,expected_data_or_json",
        (
            ("foo=bar", {"data": "foo=bar"}),
            ({"foo": "bar"}, {"json": {"foo": "bar"}}),
        ),
    )
    def test_get_fn_kwargs_works_includes_headers(
        self,
        webhook_with_headers,
        payload,
        expected_data_or_json,
    ):
        processor = WebhookProcessor(webhook_with_headers, payload)
        assert processor.get_fn_kwargs() == {
            "url": webhook_with_headers.url,
            "headers": webhook_with_headers.headers,
            **expected_data_or_json,
        }

    def test_get_headers_returns_the_headers(self, webhook_with_headers):
        processor = WebhookProcessor(webhook_with_headers, {})
        assert processor.get_headers() == webhook_with_headers.headers

    @responses.activate
    def test_process_sends_webhook_request(self, webhook):
        responses.add(responses.POST, webhook.url, status=200)
        processor = WebhookProcessor(webhook, {"foo": "bar"})
        processor.process()
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == webhook.url

    @patch.object(WebhookProcessor, "process")
    def test_call_calls_process(self, mock_process, webhook):
        processor = WebhookProcessor(webhook, {})
        processor()
        mock_process.assert_called_once()

    def test_not_whitelisted_endpoint_raises_error(self, webhook):
        webhook.url = "http://not-allowed.com/"
        processor = WebhookProcessor(webhook, {})
        with pytest.raises(DisallowedWebhookEndpointError):
            processor.process()
