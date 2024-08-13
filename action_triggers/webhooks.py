import typing as _t

import requests

from action_triggers.models import Webhook


class WebhookProcessor:
    def __init__(self, webhook: Webhook, payload: _t.Union[str, dict]):
        self.webhook = webhook
        self.payload = payload
        self.response: _t.Optional[requests.Response] = None

    def process(self) -> requests.Response:
        req_fn = self.get_request_fn()
        fn_kwargs = self.get_fn_kwargs()

        self.response = req_fn(**fn_kwargs)
        self.response.raise_for_status()

        return self.response

    def get_request_fn(self) -> _t.Callable[..., requests.Response]:
        return getattr(requests, self.webhook.http_method.lower())

    def get_fn_kwargs(self) -> dict:
        fn_kwargs = {"url": self.webhook.url, "headers": self.webhook.headers}
        if isinstance(self.payload, dict):
            fn_kwargs["json"] = self.payload
        else:
            fn_kwargs["data"] = self.payload

        return fn_kwargs

    def get_headers(self) -> dict:
        return self.webhook.headers
