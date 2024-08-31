"""Tests for the `webhooks` module."""

from unittest.mock import AsyncMock, patch

import aiohttp
import pytest
from aioresponses import aioresponses

from action_triggers.exceptions import DisallowedWebhookEndpointError
from action_triggers.webhooks import WebhookProcessor


class TestWebhookProcessor:
    """Tests for the `WebhookProcessor` class."""

    @pytest.mark.parametrize(
        "http_method,expected",
        (
            ("GET", aiohttp.ClientSession.get),
            ("POST", aiohttp.ClientSession.post),
            ("PUT", aiohttp.ClientSession.put),
            ("PATCH", aiohttp.ClientSession.patch),
            ("DELETE", aiohttp.ClientSession.delete),
        ),
    )
    @pytest.mark.asyncio
    async def test_get_request_fn_returns_correct_function(
        self,
        http_method,
        expected,
        webhook,
    ):
        webhook.http_method = http_method
        processor = WebhookProcessor(webhook, {})
        async with aiohttp.ClientSession() as session:
            result = processor.get_request_fn(session)
            assert result.__code__ is expected.__code__

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

    @pytest.mark.asyncio
    async def test_process_sends_webhook_request(self, webhook):
        processor = WebhookProcessor(webhook, {"foo": "bar"})

        with aioresponses() as mocked:
            mocked.post(webhook.url, payload={"foo": "bar"})

            await processor()
            mocked.assert_called_once()
            assert str(mocked._responses[0].url) == webhook.url

    @pytest.mark.asyncio
    @patch.object(WebhookProcessor, "process", new_callable=AsyncMock)
    async def test_call_calls_process(self, mock_process, webhook):
        processor = WebhookProcessor(webhook, {})
        await processor()
        mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_not_whitelisted_endpoint_raises_error(self, webhook):
        webhook.url = "http://not-allowed.com/"
        processor = WebhookProcessor(webhook, {})
        with pytest.raises(DisallowedWebhookEndpointError):
            await processor.process()
