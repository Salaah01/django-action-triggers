"""Module for processing webhook based actions."""

import typing as _t

import requests

from action_triggers.models import Webhook


class WebhookProcessor:
    """Process an action which involves sending a webhook.

    Args:
            webhook: The webhook configuration to process.
            payload: The payload to send with the webhook.
    """

    def __init__(self, webhook: Webhook, payload: _t.Union[str, dict]):
        self.webhook = webhook
        self.payload = payload
        self.response: _t.Optional[requests.Response] = None

    def __call__(self) -> requests.Response:
        return self.process()

    def process(self) -> requests.Response:
        """Processes the webhook action."""

        req_fn = self.get_request_fn()
        fn_kwargs = self.get_fn_kwargs()

        self.response = req_fn(**fn_kwargs)
        self.response.raise_for_status()

        return self.response

    def get_request_fn(self) -> _t.Callable[..., requests.Response]:
        """Returns the request function to use for the webhook.

        Returns:
            The request function to use for the webhook.
        """

        return getattr(requests, self.webhook.http_method.lower())

    def get_fn_kwargs(self) -> dict:
        """Returns the keyword arguments to pass to the request function.

        Returns:
            The keyword arguments to pass to the request function.
        """

        fn_kwargs = {"url": self.webhook.url, "headers": self.webhook.headers}
        if isinstance(self.payload, dict):
            fn_kwargs["json"] = self.payload
        else:
            fn_kwargs["data"] = self.payload

        return fn_kwargs

    def get_headers(self) -> dict:
        """Returns the headers to use for the webhook.

        Returns:
            The headers to use for the webhook.
        """

        return self.webhook.headers
