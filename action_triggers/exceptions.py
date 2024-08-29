"""Module containing custom exceptions."""


class DisallowedEndpointError(ValueError):
    """Exception raised when an endpoint is disallowed."""


class DisallowedWebhookEndpointError(DisallowedEndpointError):
    """Exception raised when a webhook endpoint is disallowed."""

    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Webhook endpoint '{url}' is not whitelisted.")
