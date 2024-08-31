"""Module for processing webhook based actions."""

import typing as _t

import aiohttp

from action_triggers.dynamic_loading import replace_dict_values_with_results
from action_triggers.exceptions import DisallowedWebhookEndpointError
from action_triggers.models import Webhook


class WebhookProcessor:
    """Process an action which involves sending a webhook.

    :param webhook: The webhook configuration to process.
    :param payload: The payload to send with the webhook.
    """

    def __init__(self, webhook: Webhook, payload: _t.Union[str, dict]):
        self.webhook = webhook
        self.payload = payload
        self.response: _t.Optional[aiohttp.ClientResponse] = None

    async def __call__(self) -> aiohttp.ClientResponse:
        return await self.process()

    async def process(self) -> aiohttp.ClientResponse:
        """Processes the webhook action."""

        if not self.webhook.is_endpoint_whitelisted():
            raise DisallowedWebhookEndpointError(self.webhook.url)

        fn_kwargs = self.get_fn_kwargs()

        async with aiohttp.ClientSession() as session:
            req_fn = self.get_request_fn(session)
            async with req_fn(**fn_kwargs) as response:
                self.response = response
                self.response.raise_for_status()

                return self.response

    def get_request_fn(
        self,
        session: aiohttp.ClientSession,
    ) -> _t.Callable[..., aiohttp.ClientResponse]:
        """Returns the function to use for the webhook.

        :raises AttributeError: If the HTTP method is not supported.
        :return: The request function to use for the webhook.
        """
        return getattr(session, self.webhook.http_method.lower())

    def get_fn_kwargs(self) -> dict:
        """Returns the keyword arguments to pass to the request function.

        :return: The keyword arguments to pass to the request function.
        """

        fn_kwargs: _t.Dict[str, _t.Any] = {"url": self.webhook.url}
        headers = self.get_headers()
        if headers:
            fn_kwargs["headers"] = replace_dict_values_with_results(headers)

        if isinstance(self.payload, dict):
            fn_kwargs["json"] = self.payload
        else:
            fn_kwargs["data"] = self.payload

        return fn_kwargs

    def get_headers(self) -> dict:
        """Returns the headers to use for the webhook.

        :return: The headers to use for the webhook.
        :rtype: dict
        """

        return self.webhook.headers
